# text-to-sql-eval

## Getting Started

You will need to have the following installed:

* [`git`](https://git-scm.com/)
* [`docker`](https://www.docker.com/)
* [`just`](https://just.systems/)
* [`Python 3.12+`](https://www.python.org/)
* [`uv`](https://docs.astral.sh/uv/)

To get started, clone the [`pgai`](https://github.com/timescale/pgai) and setup
its dependencies:

```bash
git clone https://github.com/timescale/pgai.git
cd pgai
just pgai install
```

Then clone this repository and set it up:

```bash
git clone https://github.com/timescale/text-to-sql-eval
cd text-to-sql
uv sync
cp .env.sample .env
```

You will then need to open the `.env` file and configure it, adding the API keys
for the provider/models that you are interested in comparing for.

Finally, you will need to run a DB to run the eval suite and store the results.
You can get a simple PG instance in Docker by doing:

```bash
docker run -d --name text-to-sql-eval \
    -p 127.0.0.1:5432:5432 \
    -e POSTGRES_HOST_AUTH_METHOD=trust \
    timescale/timescaledb-ha:pg17
```

You can run separate database servers for running the eval suite as well as for
where to store the results, e.g. running a server locally for running the suite
and a cloud database to store results. You will need to configure the `DSN` values
in the `.env` file when doing this.

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
