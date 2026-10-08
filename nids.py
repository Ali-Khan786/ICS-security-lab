import sys
from scapy.all import sniff, TCP, Raw, IP

def detect_modbus_attack(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        payload = packet[Raw].load

        print(f"[*] Intercepted Modbus packet: {len(payload)} bytes")
        sys.stdout.flush()

        if len(payload) >= 8:
            function_code = payload[7] if isinstance(payload[7], int) else ord(payload[7])

            if function_code in [5, 6, 15, 16]:
                src_ip = packet[IP].src if packet.haslayer(IP) else "Local"
                print("\n[!!!] CRITICAL: UNAUTHORIZED MODBUS WRITE DETECTED [!!!]")
                print(f"      Source IP: {src_ip}")
                print(f"      Function Code Used: {function_code}")
                print("      Alert: Possible logic override in progress.\n")
                sys.stdout.flush()

print("[*] ICS Intrusion Detection System Online.")
print("[*] Sniffing podman0/veth0 for Modbus traffic on port 502...")
sys.stdout.flush()

sniff(iface=["podman0", "veth0"], filter="tcp port 502", prn=detect_modbus_attack, store=0)
