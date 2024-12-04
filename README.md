# text-to-sql-eval

## Getting Started

Install [`uv`](https://docs.astral.sh/uv/), and then run the following:

```bash
uv sync
```

If using the `baseline.py`, then will need to copy `.env.sample` and update the
value for `OPENAI_API_KEY`.

To run the database and initialize the datasets:

```
docker compose up
```

## Running the suite

```bash
uv run main.py
```
