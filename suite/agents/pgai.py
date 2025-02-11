import psycopg
from dotenv import load_dotenv

from ..exceptions import FailedToGenerateQueryError
from ..types import Provider, TextToSql
from ..utils import setup_pgai_config

load_dotenv()


def get_tables(
    conn: psycopg.Connection, inp: str, provider: Provider, model: str
) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(
            f"select * from ai.find_relevant_obj('{inp}', objtypes=>array['table column']);"
        )
        objs = cur.fetchall()
    return list(set([row[1][1] for row in objs]))


def text_to_sql(
    conn: psycopg.Connection, inp: str, provider: Provider, model: str
) -> TextToSql:
    messages = []

    def notice_handler(notice: psycopg.errors.Diagnostic):
        messages.append({"role": "notice", "content": notice.message_primary})

    conn.add_notice_handler(notice_handler)
    with conn.cursor() as cur:
        setup_pgai_config(cur)
        cur.execute("set client_min_messages to 'DEBUG1';")
        cur.execute(
            f"""
            select ai.text_to_sql(
                %s,
                config => '{{"provider": "{provider}", "model": "{model}", "max_iter": 4}}'::jsonb
            )
            """,
            (inp,),
        )
        query = cur.fetchone()[0]
        cur.execute("set client_min_messages to 'NOTICE';")
    conn.remove_notice_handler(notice_handler)
    return {
        "error": FailedToGenerateQueryError() if query is None else None,
        "messages": messages,
        "query": query,
    }
