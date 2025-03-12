from dotenv import load_dotenv
from flask import Flask, render_template
from psycopg.rows import dict_row

from .database import Database

load_dotenv()

app = Flask(__name__)
db = Database()
db.init_app(app)


@app.route("/")
def index() -> str:
    with db.get_cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT * FROM runs ORDER BY start_time DESC")
        runs = cursor.fetchall()
    print(runs)
    return render_template("index.html", runs=runs)


@app.route("/run/<int:run_id>")
def show_run(run_id: int) -> str:
    with db.get_cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT * FROM runs WHERE id = %s", (run_id,))
        run = cursor.fetchone()
        if run is None:
            return "Run not found", 404
        cursor.execute("SELECT * FROM evals WHERE run_id = %s", (run_id,))
        evals = cursor.fetchall()
    return render_template("run.html", evals=evals, run=run)
