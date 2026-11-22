import asyncio
from asyncua import Server

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")

    idx = await server.register_namespace("http://pabrik.local")

    pabrik = await server.nodes.objects.add_object(idx, "Pabrik")

    suhu    = await pabrik.add_variable(idx, "Suhu", 85.0)
    status  = await pabrik.add_variable(idx, "Status", 1)
    counter = await pabrik.add_variable(idx, "Counter", 42)
    alarm   = await pabrik.add_variable(idx, "Alarm", 0)

    await suhu.set_writable()

    async with server:
        print("OPC UA Server nyala di opc.tcp://0.0.0.0:4840")
        print("Path: Pabrik/Suhu, Pabrik/Status, Pabrik/Counter, Pabrik/Alarm")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())