# text-to-sql-eval

## Getting Started

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
docker run -it --name postgres -p 5432:5432 -v t2s_data:/var/lib/postgresql/data postgres:17
```

Though it's suggested to run a DB with `pgai` available, e.g. such as via
[these instructions](https://github.com/timescale/pgai/blob/main/docs/install_docker.md) for
Docker. You will want to edit the `.env` file with connection details for your DB.

## Running the suite

### Locally

First, you should do:

```bash
cp .env.sample .env
```

and then configure your API keys and other values as necessary.

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

1. Use the `load` command to load the datasets into your database.
1. Use the `setup` command to setup your agent for loaded datasets.
1. Use the `eval` command to run the eval suite.

All commands have various options/arguments to configure behavior, use `--help` to see more info.

### Via GH Actions

The suite is setup to be runnable via GH actions via a workflow dispatch. To do so, go to the
[Run Eval Suite](https://github.com/timescale/text-to-sql-eval/actions/workflows/run.yml) action,
and use the "Run workflow" to configure various settings and trigger the suite. Each dataset and
database tuple are split into their own job in the action, and the results are aggregated via the
`report_results` job that runs at the end, where can view accuracy. Results are also saved to a
database in Timescale Cloud.

## Viewing Results

If the `REPORT_POSTGRES_DSN` value is set, then runs of `eval` are recorded to that database and
are viewable there, or via the eval site. To run the eval site, do:

```bash
uv run flask --app suite.eval_site run
```

To setup the eval site database, you must run `python3 scripts/setup_db.py` to create the necessary
tables.

## Repository Structure

The repository is structured as follows:

* `datasets` - Folder contains all the datasets we use for evaluating
* `scripts` - Various helper scripts for importing external datasets into this repo
* `suite` - Source code for the eval suite
