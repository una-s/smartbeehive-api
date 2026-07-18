import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "kosnice.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # redovi se ponasaju kao recnici
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kosnica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            lokacija TEXT,
            datum_postavljanja TEXT
        )
    """)
    conn.commit()
    conn.close()


#GET /kosnice — lista svih kosnica
@app.route("/kosnice", methods=["GET"])
def get_kosnice():
    conn = get_db()
    redovi = conn.execute("SELECT * FROM kosnica").fetchall()
    conn.close()
    return jsonify([dict(red) for red in redovi])

#GET /kosnice/<id> — jedna kosnica po id-ju (GET sa parametrom)
@app.route("/kosnice/<int:kosnica_id>", methods=["GET"])
def get_kosnica(kosnica_id):
    conn = get_db()
    red = conn.execute(
        "SELECT * FROM kosnica WHERE id = ?", (kosnica_id,)
    ).fetchone()
    conn.close()
    if red is None:
        return jsonify({"greska": "Košnica sa tim id-jem ne postoji"}), 404
    return jsonify(dict(red))

#POST /kosnice — dodavanje nove kosnice
@app.route("/kosnice", methods=["POST"])
def dodaj_kosnicu():
    podaci = request.get_json()
    if not podaci or "naziv" not in podaci:
        return jsonify({"greska": "Polje 'naziv' je obavezno"}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO kosnica (naziv, lokacija, datum_postavljanja) VALUES (?, ?, ?)",
        (podaci["naziv"], podaci.get("lokacija"), podaci.get("datum_postavljanja")),
    )
    conn.commit()
    novi_id = cur.lastrowid
    conn.close()
    return jsonify({"id": novi_id, "poruka": "Košnica uspešno dodata"}), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True)