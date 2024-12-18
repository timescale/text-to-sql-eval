# text-to-sql-eval

## Getting Started

Install [`uv`](https://docs.astral.sh/uv/), and then run the following:

```bash
uv sync
```

If using the `baseline.py`, then will need to copy `.env.sample` and update the
value for `OPENAI_API_KEY`.

To run the database

```bash
docker compose up
```

## Running the suite

```text
$ uv run suite --help
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
