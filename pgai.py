import psycopg

def get_tables(conn: psycopg.Connection, inp: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select set_config('ai.enable_feature_flag_text_to_sql', 'true', false)"
        )
        cur.execute(f"select * from ai.find_relevant_obj('{inp}', objtypes=>array['table']);")
        tables = cur.fetchall()
    return [table[1][1] for table in tables]
