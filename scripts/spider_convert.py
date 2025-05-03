#!/usr/bin/env python3

import os
import re
import sqlite3

import click
import psycopg
from dotenv import load_dotenv

load_dotenv()

mapping = {
    "BLOB": "BYTEA",
    "DATETIME": "TIMESTAMP",
    "DOUBLE": "DOUBLE PRECISION",
    "INT": "INTEGER",
    "NUMBER": "NUMERIC",
    "REAL": "DOUBLE PRECISION",
    "TINYINT": "SMALLINT",
    "VARCHAR2": "VARCHAR",
}

root_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


@click.command()
def main():
    main_postgres = psycopg.connect(f"{os.environ['POSTGRES_DSN']}/postgres")
    main_postgres.autocommit = True
    for entry in os.scandir(os.path.join(root_directory, "spider_data", "database")):
        dbname = f"spider_{entry.name}"
        main_postgres.execute(f'DROP DATABASE IF EXISTS "{dbname}"')
        main_postgres.execute(f'CREATE DATABASE "{dbname}"')
        sqlite = sqlite3.connect(os.path.join(entry.path, f"{entry.name}.sqlite"))
        postgres = psycopg.connect(f"{os.environ['POSTGRES_DSN']}/{dbname}")
        postgres.autocommit = True

        sqlite_cursor = sqlite.cursor()
        sqlite_cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        sqlite_cursor.execute(
            """
      SELECT
          m.name AS table_name,
          p.cid AS col_id,
          p.name AS col_name,
          p.type AS col_type,
          p.pk AS col_is_pk,
          p.dflt_value AS col_default_val,
          p.[notnull] AS col_is_not_null,
          (
              SELECT MAX(il.[unique])
              FROM pragma_index_list(m.name) il
              LEFT JOIN pragma_index_info(il.name) ii
              WHERE ii.name = p.name
          ) AS col_is_unique
      FROM sqlite_master m
      LEFT JOIN pragma_table_info((m.name)) p
      WHERE m.type = 'table';
    """
        )
        buffered_queries = []
        created_tables = []
        table = None
        columns = []
        for column in sqlite_cursor.fetchall():
            if not table:
                table = column[0]
            elif column[0] != table:
                clause = []
                if entry.name == "store_product" and table == "product":
                    new_columns = []
                    for col in columns:
                        col = list(col)
                        if col[2] == "product_id":
                            col[2] = "Product_ID"
                        else:
                            col[2] = "".join(word.title() for word in col[2].split("_"))
                        new_columns.append(col)
                    columns = new_columns
                for col in columns:
                    if (
                        entry.name == "car_1"
                        and table == "car_makers"
                        and col[2] == "Country"
                    ):
                        type = "INTEGER"
                    elif (
                        entry.name == "party_people"
                        and table == "member"
                        and col[2] == "Party_ID"
                    ):
                        type = "INTEGER"
                    elif (
                        entry.name == "sakila_1"
                        and table == "film"
                        and col[3] == "YEAR"
                    ):
                        type = "INTEGER"
                    elif not len(col[3]):
                        type = "TEXT"
                    else:
                        match = re.match(r"(\w+)(\(.*\))?", col[3])
                        if not match:
                            raise ValueError(f"Invalid type {col[3]}")
                        base_type = match.group(1).upper()
                        base_type = mapping.get(base_type, base_type)
                        if (
                            entry.name == "aircraft"
                            and table == "match"
                            and col[2] in ("Winning_Pilot", "Winning_Aircraft")
                        ):
                            base_type = "INTEGER"
                        length_spec = (
                            (match.group(2) or "")
                            if base_type not in ("INTEGER")
                            else ""
                        )
                        type = f"{base_type}{length_spec}"
                    col_clause = (
                        f'"{col[2]}" {type} {"NOT NULL" if col[6] == 1 else ""}'
                    )
                    if entry.name == "yelp":
                        if (table == "business" or table == "user") and col[2].endswith(
                            "_id"
                        ):
                            col_clause += " UNIQUE"
                    clause.append(col_clause)
                clause = ",\n".join(clause)
                primary_keys = []
                for col in columns:
                    if col[4] > 0:
                        primary_keys.append(f'"{col[2]}"')
                if len(primary_keys):
                    clause += ",\nPRIMARY KEY (" + ", ".join(primary_keys) + ")"

                fk_cursor = sqlite.cursor()
                fk_cursor.execute(f"PRAGMA foreign_key_list('{table}')")
                foreign_keys = []
                foreign_key_tables = []
                for fk in fk_cursor.fetchall():
                    if len(foreign_keys) < (fk[0] + 1):
                        foreign_keys.append([])
                    foreign_keys[fk[0]].append(fk[2:5])
                fk_cursor.close()

                i = 1
                while i < len(foreign_keys):
                    if foreign_keys[i] in foreign_keys[0:i]:
                        foreign_keys.pop(i)
                    else:
                        i += 1
                for fks in foreign_keys:
                    from_cols = [fk[1] for fk in fks]
                    to_cols = [fk[2] for fk in fks]
                    foreign_key_tables.append(fks[0][0])
                    clause += f',\nFOREIGN KEY ("{'","'.join(from_cols)}") REFERENCES "{fks[0][0]}" ("{'","'.join(to_cols)}")'

                query = f"""
          CREATE TABLE "{table}" (
            {clause}
          )
        """

                for fk_table in foreign_key_tables:
                    if fk_table not in created_tables:
                        buffered_queries.append([table, foreign_key_tables, query])
                        break
                else:
                    try:
                        postgres.execute(query)
                        created_tables.append(table)
                    except psycopg.Error as e:
                        print(query)
                        raise e
                if len(buffered_queries):
                    new_buffered_queries = []
                    for item in buffered_queries:
                        for fk_table in item[1]:
                            if fk_table not in created_tables:
                                new_buffered_queries.append(item)
                                break
                        else:
                            try:
                                postgres.execute(item[2])
                                created_tables.append(item[0])
                            except psycopg.Error as e:
                                print(item[2])
                                raise e
                    buffered_queries = new_buffered_queries
                table = column[0]
                columns = []
            columns.append(column)


if __name__ == "__main__":
    main()
