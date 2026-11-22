import asyncio
from asyncua import Server

import asyncio
import random
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840")

    idx = await server.register_namespace("http://pabrik.local")

    pabrik = await server.nodes.objects.add_object(idx, "Pabrik")

    suhu    = await pabrik.add_variable(idx, "Suhu", 85.0)
    status  = await pabrik.add_variable(idx, "Status", 1)
    counter = await pabrik.add_variable(idx, "Counter", 42)
    alarm   = await pabrik.add_variable(idx, "Alarm", 0)

    await suhu.set_writable()
    await status.set_writable()
    await counter.set_writable()
    await alarm.set_writable()

    async with server:
        print("OPC UA Server nyala di opc.tcp://127.0.0.1:4840")
        print("Suhu berubah tiap 2 detik (60-100°C)...")
        while True:
            suhu_baru = round(random.uniform(60.0, 100.0), 1)
            await suhu.write_value(suhu_baru)

            if suhu_baru > 80:
                await alarm.write_value(1)
            else:
                await alarm.write_value(0)

            counter_baru = random.randint(40, 60)
            await counter.write_value(counter_baru)

            print(f"[Server] Suhu: {suhu_baru}°C, Counter: {counter_baru}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())