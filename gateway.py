import os
import time
import asyncio
import psycopg2
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient
from asyncua import Client as OpcUaClient

load_dotenv()

def simpan_ke_db(sumber, suhu=None, status=None, counter=None, alarm=None):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO industrial_data (sumber, suhu, status, counter, alarm) VALUES (%s, %s, %s, %s, %s)",
        (sumber, suhu, status, counter, alarm)
    )
    conn.commit()
    cur.close()
    conn.close()

def on_mqtt_message(client, userdata, msg):
    try:
        suhu = float(msg.payload.decode())
        print(f"[MQTT] Suhu: {suhu}")
        simpan_ke_db('mqtt', suhu=suhu)
    except Exception as e:
        print(f"[MQTT] Error: {e}")

def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = on_mqtt_message
    client.connect("localhost", 1883)
    client.subscribe("pabrik/suhu")
    client.loop_start()
    print("[MQTT] Subscriber jalan di background")
    return client

def baca_plc():
    client = ModbusTcpClient("127.0.0.1", port=5020)
    if not client.connect():
        return None
    hasil = client.read_holding_registers(address=0, count=4)
    client.close()
    if hasil.isError():
        return None
    return {
        'suhu':    hasil.registers[0],
        'status':  hasil.registers[1],
        'counter': hasil.registers[2],
        'alarm':   hasil.registers[3],
    }

async def baca_opcua():
    async with OpcUaClient(url="opc.tcp://127.0.0.1:4840") as client:
        idx = await client.get_namespace_index("http://pabrik.local")
        pabrik = await client.nodes.objects.get_child(f"{idx}:Pabrik")
        suhu    = await (await pabrik.get_child(f"{idx}:Suhu")).read_value()
        status  = await (await pabrik.get_child(f"{idx}:Status")).read_value()
        counter = await (await pabrik.get_child(f"{idx}:Counter")).read_value()
        alarm   = await (await pabrik.get_child(f"{idx}:Alarm")).read_value()
        return {
            'suhu': suhu, 'status': status,
            'counter': counter, 'alarm': alarm,
        }

async def main():
    print("Gateway nyala. Tekan Ctrl+C untuk stop.\n")
    mqtt_client = start_mqtt()

    try:
        while True:
            plc = baca_plc()
            if plc:
                print(f"[PLC] Suhu: {plc['suhu']}, Status: {plc['status']}, Counter: {plc['counter']}")
                simpan_ke_db('plc', **plc)
            else:
                print("[PLC] Gagal baca (server mati?)")

            try:
                opcua = await baca_opcua()
                print(f"[OPCUA] Suhu: {opcua['suhu']}, Status: {opcua['status']}")
                simpan_ke_db('opcua', **opcua)
            except Exception as e:
                print(f"[OPCUA] Error: {e}")

            await asyncio.sleep(5)
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("\nGateway berhenti.")

if __name__ == "__main__":
    asyncio.run(main())