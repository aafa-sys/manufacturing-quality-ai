import paho.mqtt.client as mqtt
import random
import time
#connect ke mqtt broker

client = mqtt.Client()
client.connect("localhost",1883)

print("sensor pabrik menyala! mulai kirim data tiap 2 detik")

#looping tanpa henti

while True:
    #membuat angka random antara 70 sampai 95
    suhu = round(random.uniform(70.0,95.00), 2)

    #kirim ke mqtt
    client.publish("pabrik/suhu", str(suhu))
    print(f"[SENSOR] mengirim suhu: {suhu} derajat")

    #istirahat 2 detik
    time.sleep(2)