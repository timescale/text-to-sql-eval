import os
from contextlib import contextmanager

from flask import Flask
from psycopg_pool import ConnectionPool


class Database:
    def __init__(self):
        self.app = None
        self.pool = None

    def init_app(self, app: Flask):
        self.app = app
        self.connect()

    def connect(self):
        self.pool = ConnectionPool(
            os.environ["REPORT_POSTGRES_DSN"], min_size=1, max_size=20
        )
        return self.pool

    @contextmanager
    def get_cursor(self, **kwargs):
        if self.pool is None:
            self.connect()
        con = self.pool.getconn()
        try:
            yield con.cursor(**kwargs)
            con.commit()
        finally:
            self.pool.putconn(con)
