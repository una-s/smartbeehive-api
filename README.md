# IoT sistem za praćenje parametara proizvodnje meda

IoT sistem koji prati temperaturu i vlažnost u košnici, šalje podatke
preko MQTT protokola, skladišti ih u InfluxDB i prikazuje na dashboardu.

## Funkcionalnosti

1. Merenje temperature i vlažnosti u košnici
2. Slanje podataka preko MQTT protokola
3. Skladištenje i vizualizacija u InfluxDB
4. REST API u Flasku za upravljanje košnicama i pregled merenja

## Tehnologije

Arduino Uno, Raspberry Pi, Python, Flask, SQLite, Mosquitto, Telegraf, InfluxDB

## Veb servisi

- `GET /kosnice` — lista košnica
- `GET /merenja?kosnica_id=1` — merenja za košnicu
- `POST /kosnice` — dodavanje košnice
