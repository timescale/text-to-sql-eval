import os

from dotenv import load_dotenv


load_dotenv()


def get_psycopg_str(dbname: str = "postgres") -> str:
    return f"host={os.environ['POSTGRES_HOST']} dbname={dbname} user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}"
