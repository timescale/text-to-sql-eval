import os

from dotenv import load_dotenv
import psycopg

load_dotenv()


def get_tables(conn: psycopg.Connection, inp: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(f"select * from ai.find_relevant_obj('{inp}', objtypes=>array['table column']);")
        objs = cur.fetchall()
    return list(set([row[1][1] for row in objs]))


def text_to_sql(conn: psycopg.Connection, inp: str) -> str:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(
            "select set_config('ai.openai_api_key', %s, false) is not null",
            (os.environ['OPENAI_API_KEY'],),
        )
        cur.execute("""
            select ai.text_to_sql(
                'Construct a query that gives me the distinct foo where the corresponding ids are evenly divisible life.'
                , ai.text_to_sql_openai('gpt-4o-mini')
                )
        """)
        query = cur.fetchone()[0]
    return query.replace('```sql', '').replace('```', '').strip()
