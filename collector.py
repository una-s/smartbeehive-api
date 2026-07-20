import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

# 1. Konfiguracija za InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "8xzHFCR7miMmGufuinkShAOc1-NNSCLGz7r5dokEp_a0ddZ20b1pf7JD3v54k0v-wiCz7IrE9hxUUMGpnyM2Mw=="
INFLUX_ORG = "Faculty of Organizational Sciences"
INFLUX_BUCKET = "projekat"

# Inicijalizacija InfluxDB klijenta
influx_client = InfluxDBClient(
    url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# 2. MQTT Callback - Poziva se svaki put kada stigne poruka sa senzora
def on_message(client, userdata, msg):
    try:
        # Poruka stiže u JSON formatu, npr. {"kosnica_id": 1, "temperatura": 24.5, "vlaznost": 60}
        payload = json.loads(msg.payload.decode("utf-8"))

        kosnica_id = str(payload.get("kosnica_id", 1))
        temp = float(payload.get("temperatura", 0.0))
        vlaznost = float(payload.get("vlaznost", 0.0))

        # Pravljenje InfluxDB "Point"-a (podatak sa merenjem)
        point = (
            Point("merenja_senzora")
            .tag("kosnica_id", kosnica_id)
            .field("temperatura", temp)
            .field("vlaznost", vlaznost)
        )

        # Upis u InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        print(
            f"Uspešno upisano u InfluxDB za košnicu {kosnica_id}: Temp={temp}°C, Vlažnost={vlaznost}%"
        )

    except Exception as e:
        print(f"Greška pri obradi poruke: {e}")


# 3. Podešavanje MQTT klijenta
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

# Povezivanje na MQTT Broker (npr. Mosquitto koji radi na RPi ili lokalno)
mqtt_client.connect("localhost", 1883, 60)

# Pretplata na temu gde senzori šalju podatke
mqtt_client.subscribe("pcelinjak/senzori")

print("Započeto slušanje MQTT poruka...")
# Pokretanje beskonačne petlje za slušanje poruka
mqtt_client.loop_forever()