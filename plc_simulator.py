from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

# Isi "loket" (register) PLC palsu
# Alamat 1: suhu, Alamat 2: status, Alamat 3: counter, Alamat 4: alarm
register_awal = [85, 1, 42, 0]

store = ModbusDeviceContext(
    hr=ModbusSequentialDataBlock(1, register_awal)
)

context = ModbusServerContext(devices=store, single=True)

print("PLC Simulator nyala di port 5020...")
print("Register: suhu=85, status=1, counter=42, alarm=0")
StartTcpServer(context=context, address=("0.0.0.0", 5020))