import os
import psycopg2
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient

load_dotenv()

client = ModbusTcpClient("127.0.0.1", port=5020)
client.connect()

hasil = client.read_holding_registers(address=0, count=4)

if hasil.isError():
    print(f"ERROR: {hasil}")
else:
    suhu    = hasil.registers[0]
    status  = hasil.registers[1]
    counter = hasil.registers[2]
    alarm   = hasil.registers[3]

    print(f"Suhu    : {suhu}")
    print(f"Status  : {status}")
    print(f"Counter : {counter}")
    print(f"Alarm   : {alarm}")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO plc_data (suhu, status, counter, alarm) VALUES (%s, %s, %s, %s)",
        (suhu, status, counter, alarm)
    )
    conn.commit()
    cur.close()
    conn.close()

    print("Tersimpan ke database")

client.close()