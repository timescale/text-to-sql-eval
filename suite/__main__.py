try:
    from .main import cli
except ImportError:
    raise SystemExit("You need run this script via `python3 -m suite`") from None


cli()
