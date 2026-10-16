"""Painting company database manager.

A small Flask web app that lets the user pick one of three separate
SQLite databases and read, add, edit and delete its records.

Run:  python app.py   ->  open http://127.0.0.1:5000
"""
import os
import sqlite3

from flask import Flask, abort, redirect, render_template, request, url_for

import seed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "databases")


DATABASES = {
    "customers": {"label": "Customers", "file": "customers.db", "table": "customers"},
    "projects": {"label": "Projects", "file": "projects.db", "table": "projects"},
    "inventory": {"label": "Paint inventory", "file": "inventory.db", "table": "paints"},
}

app = Flask(__name__)


def get_db(key):
    """Return (connection, settings) for the selected database or 404."""
    if key not in DATABASES:
        abort(404)
    settings = DATABASES[key]
    con = sqlite3.connect(os.path.join(DB_DIR, settings["file"]))
    con.row_factory = sqlite3.Row
    return con, settings


def get_columns(con, table):
    """Read the column names of a table from the database itself."""
    return [row["name"] for row in con.execute(f"PRAGMA table_info({table})")]


def editable_columns(columns):
    """All columns except the auto-generated id."""
    return [c for c in columns if c != "id"]


def form_values(columns):
    """Collect values from the submitted form; empty fields become NULL."""
    return [request.form.get(c, "").strip() or None for c in columns]


@app.route("/")
def index():
    return redirect(url_for("view_db", key="customers"))


@app.route("/db/<key>")
def view_db(key):
    con, settings = get_db(key)
    table = settings["table"]
    columns = get_columns(con, table)
    search = request.args.get("q", "").strip()

    if search:
        where = " OR ".join(f"CAST({c} AS TEXT) LIKE ?" for c in columns)
        rows = con.execute(
            f"SELECT * FROM {table} WHERE {where} ORDER BY id", [f"%{search}%"] * len(columns)
        ).fetchall()
    else:
        rows = con.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
    con.close()

    return render_template(
        "index.html",
        databases=DATABASES,
        key=key,
        settings=settings,
        columns=columns,
        editable=editable_columns(columns),
        rows=rows,
        search=search,
        edit_row=None,
    )


@app.route("/db/<key>/add", methods=["POST"])
def add_row(key):
    con, settings = get_db(key)
    table = settings["table"]
    cols = editable_columns(get_columns(con, table))
    placeholders = ", ".join("?" for _ in cols)
    con.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", form_values(cols))
    con.commit()
    con.close()
    return redirect(url_for("view_db", key=key))


@app.route("/db/<key>/edit/<int:row_id>", methods=["GET", "POST"])
def edit_row(key, row_id):
    con, settings = get_db(key)
    table = settings["table"]
    columns = get_columns(con, table)
    cols = editable_columns(columns)

    if request.method == "POST":
        assignments = ", ".join(f"{c} = ?" for c in cols)
        con.execute(f"UPDATE {table} SET {assignments} WHERE id = ?", form_values(cols) + [row_id])
        con.commit()
        con.close()
        return redirect(url_for("view_db", key=key))

    row = con.execute(f"SELECT * FROM {table} WHERE id = ?", [row_id]).fetchone()
    rows = con.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
    con.close()
    if row is None:
        abort(404)

    return render_template(
        "index.html",
        databases=DATABASES,
        key=key,
        settings=settings,
        columns=columns,
        editable=cols,
        rows=rows,
        search="",
        edit_row=row,
    )


@app.route("/db/<key>/delete/<int:row_id>", methods=["POST"])
def delete_row(key, row_id):
    con, settings = get_db(key)
    con.execute(f"DELETE FROM {settings['table']} WHERE id = ?", [row_id])
    con.commit()
    con.close()
    return redirect(url_for("view_db", key=key))


@app.route("/reset", methods=["POST"])
def reset():
    seed.seed()
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not all(os.path.exists(os.path.join(DB_DIR, d["file"])) for d in DATABASES.values()):
        seed.seed()
    app.run(debug=True)
