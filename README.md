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
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  eval
  load
```

1. Use the `eval` command to load the datasets into your database.
1. Use the `load` command to run the eval suite.

Both commands have various options/arguments, use `--help` to see more info.
