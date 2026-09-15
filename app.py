from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "clients.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                business_type TEXT,
                site_url TEXT,
                status TEXT NOT NULL DEFAULT 'Discovery',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def dashboard():
    with get_db() as conn:
        clients = conn.execute(
            "SELECT * FROM clients ORDER BY created_at DESC"
        ).fetchall()
    return render_template("dashboard.html", clients=clients)


@app.route("/add", methods=["GET", "POST"])
def add_client():
    if request.method == "POST":
        name = request.form["name"]
        business_type = request.form["business_type"]
        site_url = request.form["site_url"]
        status = request.form["status"]
        notes = request.form["notes"]
        with get_db() as conn:
            conn.execute(
                "INSERT INTO clients (name, business_type, site_url, status, notes) VALUES (?, ?, ?, ?, ?)",
                (name, business_type, site_url, status, notes),
            )
        return redirect(url_for("dashboard"))
    return render_template("add_client.html")


@app.route("/client/<int:client_id>")
def client_detail(client_id):
    with get_db() as conn:
        client = conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
    if not client:
        return "Client not found", 404
    return render_template("client_detail.html", client=client)


@app.route("/client/<int:client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    with get_db() as conn:
        client = conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
    if not client:
        return "Client not found", 404
    if request.method == "POST":
        name = request.form["name"]
        business_type = request.form["business_type"]
        site_url = request.form["site_url"]
        status = request.form["status"]
        notes = request.form["notes"]
        with get_db() as conn:
            conn.execute(
                "UPDATE clients SET name=?, business_type=?, site_url=?, status=?, notes=? WHERE id=?",
                (name, business_type, site_url, status, notes, client_id),
            )
        return redirect(url_for("client_detail", client_id=client_id))
    return render_template("edit_client.html", client=client)


@app.route("/client/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    with get_db() as conn:
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    return redirect(url_for("dashboard"))


# ── Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
