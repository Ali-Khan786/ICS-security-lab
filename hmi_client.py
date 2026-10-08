import time
from pymodbus.client import ModbusTcpClient

# Connect to the local OpenPLC runtime on port 502
client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

print("[+] Connected to OpenPLC Modbus TCP Server")

# 1. Read current TANK_LEVEL (Holding Register 0 / %MW0)
rr = client.read_holding_registers(address=0, count=1)
if not rr.isError():
    print(f"[*] Initial Tank Level: {rr.registers[0]}%")

# 2. Press START_PB (Coil 1 / %QX0.1) to start the pump cycle
print("[+] Pulsing START_PB (Turning on Coil 1)...")
client.write_coil(address=1, value=True)
time.sleep(0.5)
client.write_coil(address=1, value=False)

# 3. Monitor the filling process
print("[*] Monitoring tank level changes:")
for _ in range(10):
    rr = client.read_holding_registers(address=0, count=1)
    coils = client.read_coils(address=0, count=1)

    level = rr.registers[0] if not rr.isError() else "Error"
    pump_status = "RUNNING" if (not coils.isError() and coils.bits[0]) else "OFF"

    print(f"    Pump Status: {pump_status} | Tank Level: {level}%")
    time.sleep(1)

client.close()
