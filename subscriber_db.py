import paho.mqtt.client as mqtt
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD =os.getenv("DB_PASSWORD")

def simpan_ke_db(topic, suhu):
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sensor_data (topic, suhu) VALUES (%s, %s)",
        (topic, suhu)
    )
    conn.commit()
    cur.close()
    conn.close()

def on_message(client, userdata, msg):
    suhu = msg.payload.decode()
    print(f"Terima: {msg.topic} = {suhu}")
    if float(suhu) > 80:
        print("ALARM! Suhu bahaya!")
    else:
        print("Suhu aman")
    simpan_ke_db(msg.topic, float(suhu))
    print("Tersimpan ke database")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("pabrik/suhu")
print("Dengerin pabrik/suhu & simpan ke DB...")
client.loop_forever()