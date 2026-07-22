
import time
import paho.mqtt.client as mqtt
import serial

# Povezivanje na serijski port Arduina
ard = serial.Serial("/dev/ttyUSB0", 9600)
time.sleep(2)

# Povezivanje na MQTT Broker (ako je broker na samom RPi-ju koristimo 'localhost')
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883, 60)

print("Skripta pokrenuta: Čitam Arduino i šaljem na MQTT...")

try:
    while True:
        if ard.in_waiting > 0:
            # Čita liniju sa Arduina i uklanja razmake/nove redove
            poruka = ard.readline().decode("utf-8").strip()
            print(f"Stiglo sa Arduina: {poruka}")

            # Šalje na MQTT temu
            mqtt_client.publish("pcelinjak/senzori", poruka)
except KeyboardInterrupt:
    print("\nPrekid rada skripte.")