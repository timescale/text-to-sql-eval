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

```text
$ uv run python3 -m suite --help
Usage: suite [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  eval  Runs the eval suite for a given agent and task.
  load  Load the datasets into the database.
```

1. Use the `load` command to load the datasets into your database.
1. Use the `eval` command to run the eval suite.

Both commands have various options/arguments, use `--help` to see more info.

## Repository Structure

The repository is structured as follows:

* `datasets` - Folder contains all the datasets we use for evaluating
* `scripts` - Various helper scripts for importing external datasets into this repo
* `suite` - Source code for the eval suite
