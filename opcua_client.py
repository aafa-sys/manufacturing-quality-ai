import os
import asyncio
import psycopg2
from dotenv import load_dotenv
from asyncua import Client

load_dotenv()

async def main():
    async with Client(url="opc.tcp://127.0.0.1:4840") as client:
        idx = await client.get_namespace_index("http://pabrik.local")

        pabrik = await client.nodes.objects.get_child(f"{idx}:Pabrik")

        suhu    = await pabrik.get_child(f"{idx}:Suhu")
        status  = await pabrik.get_child(f"{idx}:Status")
        counter = await pabrik.get_child(f"{idx}:Counter")
        alarm   = await pabrik.get_child(f"{idx}:Alarm")

        nilai_suhu    = await suhu.read_value()
        nilai_status  = await status.read_value()
        nilai_counter = await counter.read_value()
        nilai_alarm   = await alarm.read_value()

        print(f"Suhu    : {nilai_suhu}°C")
        print(f"Status  : {nilai_status}")
        print(f"Counter : {nilai_counter}")
        print(f"Alarm   : {nilai_alarm}")

        if nilai_suhu > 80:
            keputusan = "BAHAYA"
            print(f" {keputusan}! Suhu {nilai_suhu}°C melebihi batas 80°C")
        else:
            keputusan = "AMAN"
            print(f" {keputusan}. Suhu {nilai_suhu}°C dalam batas normal")

        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO opcua_data (suhu, status, counter, alarm) VALUES (%s, %s, %s, %s)",
            (nilai_suhu, nilai_status, nilai_counter, nilai_alarm)
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"Tersimpan ke database (status: {keputusan})")

if __name__ == "__main__":
    asyncio.run(main())