import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
import sqlite3


INFLUX_URL = "http://raspberrypi.local:8086/"
INFLUX_TOKEN = "UFbOji8eqqSHK01grfrHBGAqX1TC4Br8d6-cszjKQ4yRNZXPHbQ7PgqDPyxuHUDcecsKvFNOyYV8RlgIGOE-0w=="
INFLUX_ORG = "Faculty of Organizational Sciences"
INFLUX_BUCKET = "projekat"

# Inicijalizacija klijenta za čitanje iz baze
influx_client = InfluxDBClient(
    url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
)

app = Flask(__name__)
DB = "kosnice.db"
app.json.ensure_ascii = False

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

@app.route("/api/kosnica/<int:kosnica_id>/statistika-klime", methods=["GET"])
def statistika_klime(kosnica_id):
    try:
        # Upit za InfluxDB: uzimamo prosečnu temp i vlažnost za poslednja 24h i pre 24h
        query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -48h)
            |> filter(fn: (r) => r["_measurement"] == "merenja_senzora")
            |> filter(fn: (r) => r["kosnica_id"] == "{kosnica_id}")
            |> filter(fn: (r) => r["_field"] == "temperatura" or r["_field"] == "vlaznost")
            |> aggregateWindow(every: 24h, fn: mean, createEmpty: false)
        """
        tables = influx_client.query_api().query(query)

        tempe = []
        vlaznosti = []

        for table in tables:
            for record in table.records:
                field = record.get_field()
                val = record.get_value()
                if field == "temperatura":
                    tempe.append(val)
                elif field == "vlaznost":
                    vlaznosti.append(val)

        if len(tempe) < 2 or len(vlaznosti) < 2:
            return (
                jsonify(
                    {
                        "poruka": "Nedovoljno istorijskih podataka za preracun trenda (potrebno je bar 24h-48h rada).",
                        "trenutni_podaci": {
                            "temperatura": tempe[-1] if tempe else 0,
                            "vlaznost": vlaznosti[-1] if vlaznosti else 0,
                        },
                    }
                ),
                200,
            )

        prosek_temp_danas = round(tempe[-1], 2)
        prosek_temp_juce = round(tempe[-2], 2)
        trend_temp = round(prosek_temp_danas - prosek_temp_juce, 2)

        prosek_vlaznost_danas = round(vlaznosti[-1], 2)
        prosek_vlaznost_juce = round(vlaznosti[-2], 2)
        trend_vlaznost = round(prosek_vlaznost_danas - prosek_vlaznost_juce, 2)

        # Logika preračuna: Procena mikroklimatske stabilnosti
        # Idealna temp kosnice je između 34.0°C i 35.5°C
        odstupanje = abs(prosek_temp_danas - 34.8)
        if odstupanje <= 1.5:
            ocena_klime = "Odlicna (Optimalni uslovi za leglo)"
        elif odstupanje <= 3.5:
            ocena_klime = "Umerena (Pcele aktivno regulisu temperaturu)"
        else:
            ocena_klime = "Nestabilna (Niski ili previsoki uslovi u okruzenju)"

        return (
            jsonify(
                {
                    "kosnica_id": kosnica_id,
                    "prosek_temperatura_24h": prosek_temp_danas,
                    "promena_temp_u_odnosu_na_juce": f"{'+' if trend_temp > 0 else ''}{trend_temp}°C",
                    "prosek_vlaznost_24h": prosek_vlaznost_danas,
                    "promena_vlaznosti_u_odnosu_na_juce": f"{'+' if trend_vlaznost > 0 else ''}{trend_vlaznost}%",
                    "ocena_mikroklime": ocena_klime,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"greska": str(e)}), 500
    
@app.route("/api/kosnica/<int:kosnica_id>/alerti", methods=["GET"])
def proveru_alerta(kosnica_id):
    try:
        # Uzimamo samo najnovije merenje (poslednjih 15 minuta)
        query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -15m)
            |> filter(fn: (r) => r["_measurement"] == "merenja_senzora")
            |> filter(fn: (r) => r["kosnica_id"] == "{kosnica_id}")
            |> filter(fn: (r) => r["_field"] == "temperatura" or r["_field"] == "vlaznost")
            |> last()
        """
        tables = influx_client.query_api().query(query)

        temp = None
        vlaznost = None

        for table in tables:
            for record in table.records:
                if record.get_field() == "temperatura":
                    temp = record.get_value()
                elif record.get_field() == "vlaznost":
                    vlaznost = record.get_value()

        if temp is None or vlaznost is None:
            return jsonify({
                "kosnica_id": kosnica_id,
                "status": "OFLAJN",
                "poruka": "Senzori ne šalju podatke u poslednjih 15 minuta!"
            }), 200

        alerti = []

        # Provera temperature
        if temp > 38.0:
            alerti.append({
                "nivo": "KRITIČNO",
                "tip": "VISOKA_TEMPERATURA",
                "poruka": f"Previsoka temperatura ({temp}°C)! Rizik od toplotnog stresa."
            })
        elif temp < 31.0:
            alerti.append({
                "nivo": "UPOZORENJE",
                "tip": "NISKA_TEMPERATURA",
                "poruka": f"Niska temperatura ({temp}°C) u leglu."
            })

        # Provera vlaznosti
        if vlaznost > 80.0:
            alerti.append({
                "nivo": "UPOZORENJE",
                "tip": "VISOKA_VLAZNOST",
                "poruka": f"Povecana vlaznost ({vlaznost}%). Rizik od pojave buđi."
            })
        elif vlaznost < 40.0:
            alerti.append({
                "nivo": "INFO",
                "tip": "NISKA_VLAZNOST",
                "poruka": f"Vlaznost je niska ({vlaznost}%)."
            })

        return jsonify({
            "kosnica_id": kosnica_id,
            "trenutno": {"temperatura": temp, "vlaznost": vlaznost},
            "ima_alerta": len(alerti) > 0,
            "broj_alerta": len(alerti),
            "alerti": alerti
        }), 200

    except Exception as e:
        return jsonify({"greska": str(e)}), 500    
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)