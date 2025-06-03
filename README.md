# text-to-sql-eval

## Getting Started

First you must checkout the [`pgai`](https://github.com/timescale/pgai/) repo next
to this one.

Install [`uv`](https://docs.astral.sh/uv/), and then run the following:

```bash
uv sync
cp .env.sample .env
```

You will then need to edit the `.env` file, plugging in the appropriate values for
the LLM provider you wish to use. You may omit any that you don't plan to use.

You will need to run a DB to run the eval suite. You can get a simple PG instance
in Docker by doing:

```bash
docker run -d --name text-to-sql-eval \
    -p 127.0.0.1:5555:5432 \
    -e POSTGRES_HOST_AUTH_METHOD=trust \
    timescale/timescaledb-ha:pg17
```

You will want to edit the `.env` file with connection details for your DB.

## Running the suite

```text
$ uv run python3 -m suite --help
Usage: python -m suite [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  eval             Runs the eval suite for a given agent and task.
  generate-matrix  Generates a matrix of all datasets and their databases...
  generate-report
  get-model        Given a provider, returns the default model for it if...
  load             Load the datasets into the database.
  setup            Setup the agent
```

1. Use the `load` command to load the datasets into your database:

    ```bash
    uv run python3 -m suite load
    ```

1. Use the `setup` command to setup your agent for loaded datasets:

    ```bash
    uv run python3 -m suite setup pgai
    ```

1. Use the `eval` command to run the eval suite for a given agent for a given task:

    ```bash
    uv run python3 -m suite eval pgai text_to_sql
    ```

All commands have various options/arguments to configure behavior, use `--help` to see more info.

## Viewing Results

After a run is complete, there is a `results/results.json` file that is generated that has the
run details. You can use the `generate-report` CLI command to have it be pretty printed out
to the console.

If the `REPORT_POSTGRES_DSN` value is set, then runs of `eval` are recorded to that database and
are viewable there, or via the eval site. To run the eval site, do:

```bash
uv run flask --app suite.eval_site run
```

To setup the eval site database, you must run `python3 scripts/setup_db.py` to create the necessary
tables.

## Using GH Actions

The suite is setup to be runnable via GH actions via a workflow dispatch. To do so, go to the
[Run Eval Suite](https://github.com/timescale/text-to-sql-eval/actions/workflows/run.yml) action,
and use the "Run workflow" to configure various settings and trigger the suite. Each dataset and
database tuple are split into their own job in the action, and the results are aggregated via the
`report_results` job that runs at the end, where can view accuracy. Results are also saved to a
database in Timescale Cloud.

## Repository Structure

The repository is structured as follows:

* `datasets` - Folder contains all the datasets we use for evaluating
* `scripts` - Various helper scripts for importing external datasets into this repo
* `suite` - Source code for the eval suite
