## Tehnologije

- **Hardver:** Arduino Uno, Raspberry Pi 3B, senzori DHT11
- **Backend:** Python, Flask, SQLite, InfluxDB 2.x
- **Komunikacija:** MQTT (Mosquitto), serial (USB, 9600 bps)
- **Frontend:** HTML, JavaScript (fetch API), Bootstrap 5

## Struktura repozitorijuma

| Fajl | Opis |
|---|---|
| `app.py` | Flask REST API + posluživanje frontenda |
| `templates/index.html` | Web aplikacija za pčelara |
| `collector.py` | Prijem MQTT poruka i upis u InfluxDB (Raspberry Pi) |
| `skripta.py` | Čitanje Arduina i objavljivanje na MQTT (Raspberry Pi) |
| `skripta.ino` | Arduino kod za čitanje senzora |
| `requirements.txt` | Python zavisnosti |


## Pokretanje

Kloniranje repozitorijuma:

```bash
git clone https://github.com/<korisnicko_ime>/smartbeehive-api.git
cd smartbeehive-api
```

Kreiranje virtuelnog okruženja i instalacija zavisnosti:

```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# ili: source venv/bin/activate  (Linux/Mac)
pip install -r requirements.txt
```

Pokretanje Flask aplikacije:

```bash
python app.py
```

Aplikacija je dostupna na `http://127.0.0.1:5000`.

## REST API — dostupne rute

| Metoda | Ruta | Opis |
|---|---|---|
| GET | `/` | Web aplikacija (frontend) |
| GET | `/kosnice` | Lista svih košnica |
| GET | `/kosnice/<id>` | Podaci o pojedinačnoj košnici |
| POST | `/kosnice` | Dodavanje nove košnice |
| DELETE | `/kosnice/<id>` | Brisanje košnice |
| GET | `/api/kosnica/<id>/statistika-klime` | Prosek 24h + trend |
| GET | `/api/kosnica/<id>/alerti` | Trenutni status i upozorenja |

## Autor

Una — projektni zadatak iz predmeta Internet inteligentnih uredjaja, Fakultet organizacionih nauka, 2026.
