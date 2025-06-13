import os
import time
from collections import Counter
from textwrap import dedent

import polars as pl
import psycopg
import simplejson as json
from polars.testing import assert_frame_equal, assert_series_equal
from pydantic_ai.direct import model_request
from pydantic_ai.messages import ModelRequest
from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.tools import ToolDefinition
from sql_metadata import Parser
from tokencost import TOKEN_COSTS, calculate_cost_by_tokens

from ..agents import AgentFn
from ..exceptions import AgentFnError, GetExpectedError, QueryExecutionError
from ..types import ContextMode, Provider


def get_dataframe(query: str, conn: psycopg.Connection) -> pl.DataFrame:
    """
    Execute a SQL query and return the results as a Polars DataFrame.

    This function is a workaround for pl.read_database which does not support
    multiple columns with the same name. It executes the query using a cursor,
    fetches all results, and constructs a Polars DataFrame while ensuring unique
    column names by appending an index to duplicate names. It then relies on
    the `compare` function to handle mapping of columns between actual and expected
    DataFrames with whatever column names we end up with.
    """
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
        colnames = [desc.name for desc in cur.description]
        counter = Counter(colnames)
        for i, colname in enumerate(colnames):
            if counter[colname] > 1:
                colnames[i] = f"{colname}_{i}"
        return pl.DataFrame(data, schema=colnames, orient="row")


def compare(actual: pl.DataFrame, expected: pl.DataFrame) -> bool:
    column_mappings = {}

    if len(actual.columns) < len(expected.columns):
        return False

    for e_col in expected.columns:
        e_values = expected[e_col]
        for a_col in actual.columns:
            # Check if the values match in the same order
            try:
                assert_series_equal(
                    e_values, actual[a_col], check_names=False, check_order=False
                )
                column_mappings[a_col] = e_col
                break
            except AssertionError:
                pass

    actual_adjusted = actual.select(list(column_mappings.keys())).rename(
        column_mappings
    )
    try:
        assert_frame_equal(
            actual_adjusted, expected, check_column_order=False, check_row_order=False
        )
        return True
    except AssertionError:
        return False


async def run(
    conn: psycopg.Connection,
    path: str,
    inp: str,
    agent_fn: AgentFn,
    provider: Provider,
    model: str,
    context_mode: ContextMode,
    llm_judge: str,
    *args,
) -> bool:
    if os.path.exists(f"{path}/actual_query.sql"):
        os.unlink(f"{path}/actual_query.sql")
    if os.path.exists(f"{path}/actual_messages.txt"):
        os.unlink(f"{path}/actual_messages.txt")
    if os.path.exists(f"{path}/details.json"):
        os.unlink(f"{path}/details.json")
    with open(f"{path}/eval.json", "r") as fp:
        gold_query = json.load(fp).get("query")
    gold_tables_list = []
    if context_mode == "specific_ids":
        parser = Parser(gold_query)
        gold_tables_list = [table.lower() for table in parser.tables]
    start = time.time()
    try:
        result = await agent_fn(
            conn, inp, provider, model, context_mode, gold_tables_list
        )
    except Exception as e:
        raise AgentFnError(e) from e
    duration = round(time.time() - start, 3)
    with open(f"{path}/actual_messages.txt", "w") as fp:
        for i in range(len(result["messages"])):
            if i > 0:
                fp.write("\n")
            message = result["messages"][i]
            if isinstance(message, str):
                fp.write(f"{message}")
            else:
                fp.write(f"{message['role']}:\n{message['content']}")
    if "error" in result and result["error"] is not None:
        raise (
            result["error"]
            if isinstance(result["error"], Exception)
            else AgentFnError(str(result["error"]))
        )
    query = result["query"]
    with open(f"{path}/actual_query.sql", "w") as fp:
        fp.write(query)

    try:
        expected = get_dataframe(gold_query, conn)
    except (psycopg.DatabaseError, psycopg.errors.QueryCanceled) as e:
        raise GetExpectedError(e) from e

    try:
        actual = get_dataframe(query, conn)
    except (psycopg.DatabaseError, psycopg.errors.QueryCanceled) as e:
        raise QueryExecutionError(e) from e

    usage = result.get(
        "usage",
        {
            "cached_tokens": 0,
            "cached_tokens_cost": 0.0,
            "request_tokens": 0,
            "request_tokens_cost": 0.0,
            "response_tokens": 0,
            "response_tokens_cost": 0.0,
        },
    )

    cost_model = model
    if cost_model not in TOKEN_COSTS:
        cost_model = f"{provider}/{model}"

    try:
        usage["cached_tokens_cost"] = float(
            calculate_cost_by_tokens(usage["cached_tokens"], cost_model, "cached")
        )
    except KeyError:
        usage["cached_tokens_cost"] = 0.0

    try:
        usage["request_tokens_cost"] = float(
            calculate_cost_by_tokens(usage["request_tokens"], cost_model, "input")
        )
    except KeyError:
        usage["request_tokens_cost"] = 0.0

    try:
        usage["response_tokens_cost"] = float(
            calculate_cost_by_tokens(usage["response_tokens"], cost_model, "output")
        )
    except KeyError:
        usage["response_tokens_cost"] = 0.0

    status = "pass" if compare(actual, expected) else "fail"
    llm_judgement = None
    if llm_judge != "none":
        if status == "fail" or llm_judge == "all":
            from tabulate import tabulate

            parts = [
                dedent(f"""
                    Is the following query equivalent to the expected query for the given question?
                    You MUST answer using the `sql_judge` tool call.

                    Question: {inp}

                    Expected Query:
                    ```sql
                    {gold_query}
                    ```

                    Subset of expected results:
                """),
                tabulate(
                    expected.head(10).to_pandas(),
                    headers="keys",
                    tablefmt="github",
                    showindex=False,
                ),
                dedent(f"""

                    Actual Query:
                    ```sql
                    {query}
                    ```

                    Subset of actual results:
                """),
                tabulate(
                    actual.head(10).to_pandas(),
                    headers="keys",
                    tablefmt="github",
                    showindex=False,
                ),
            ]
            messages = [
                ModelRequest.user_text_prompt("".join(parts)),
            ]
            # print(messages[0].parts[0].content)
            model_response = await model_request(
                "openai:gpt-4.1-nano",
                messages,
                model_request_parameters=ModelRequestParameters(
                    output_tools=[
                        ToolDefinition(
                            name="sql_judge",
                            description="Provide a yes or no answer to whether the actual query is equivalent to the expected query for the given question along with reasoning on why.",
                            parameters_json_schema={
                                "type": "object",
                                "properties": {
                                    "judgement": {
                                        "type": "boolean",
                                        "description": (
                                            "Indicate whether the actual query is equivalent to the expected query"
                                        ),
                                    },
                                    "explanation": {
                                        "type": "string",
                                        "description": (
                                            "Concise explanation of the judgement if queries were equivalent or not"
                                        ),
                                    },
                                },
                                "required": [
                                    "judgement",
                                    "explanation",
                                ],
                            },
                        )
                    ]
                ),
            )
            part = model_response.parts[0]
            if part.part_kind != "tool-call":
                print("    Unexpected response from LLM judge, expected tool call")
            else:
                args = part.args_as_dict()
                llm_judgement = args.get("judgement", None)
                llm_explanation = args.get("explanation", "")

    details = {
        "generated_query": query,
        "expected_query": gold_query,
        "duration": duration,
        "usage": usage,
    }

    if context_mode == "specific_ids":
        details["gold_tables"] = gold_tables_list
    if llm_judgement is not None:
        details["llm_judge"] = llm_judgement
        details["llm_explanation"] = llm_explanation

    return_obj = {
        "status": status,
        "details": details,
    }

    with open(f"{path}/details.json", "w") as fp:
        json.dump(return_obj, fp, indent=2, ignore_nan=True, use_decimal=True)

    return return_obj
