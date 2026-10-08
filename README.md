# ICS/OT Cybersecurity Lab: Modbus TCP Exploitation and Network Defense

**Author:** Ali Ahmed Khan  
**Environment:** Parrot OS, Podman/Docker, Python 3  
**Target:** OpenPLC Virtual Runtime (Modbus TCP port 502)  
**Tools:** `pymodbus`, `scapy`

## Executive Summary
This project demonstrates the vulnerabilities inherent in unauthenticated industrial control protocols and the implementation of passive network defenses. An industrial water tank process was simulated using an OpenPLC runtime deployed via Podman. After establishing a legitimate Human-Machine Interface (HMI) to monitor the process, a Python-based Modbus injection script was developed to bypass the programmable logic controller's (PLC) safety interlocks. Finally, a custom Network Intrusion Detection System (NIDS) was engineered using Scapy to monitor the containerized network bridge and alert on unauthorized logic overrides in real-time.

## Phase 1: Environment Setup and HMI Simulation
**Objective:** Establish a baseline connection to the industrial control system to monitor physical processes.

The target environment consisted of an OpenPLC container executing a standard water tank ladder logic program. To interact with the PLC legitimately, a Python HMI client was developed utilizing the `pymodbus` library.

**HMI Client Functionality:**
1. Connected to the Modbus TCP server on `localhost:502`.
2. Read Holding Register 0 (`%MW0`) to monitor the current tank level.
3. Pulsed Coil 1 (`%QX0.1`) to simulate an operator pressing the "Start" button.
4. Continuously polled the PLC to output the pump status and tank level changes to the terminal.

<img width="1920" height="1080" alt="terminalpic" src="https://github.com/user-attachments/assets/09d99d58-0820-4323-b982-b21dcfa0a4b1" />


## Phase 2: Modbus Command Injection Attack
**Objective:** Exploit the lack of authentication in the Modbus TCP protocol to alter the physical state of the process, simulating a logic override attack.

A malicious Python script (`attack.py`) was developed to inject unauthorized Modbus packets directly into the PLC memory, bypassing the standard HMI and the controller's internal safety logic.

**Attack Vectors Executed:**
*   **Sensor Spoofing (View Manipulation):** Wrote a value of `100` to Holding Register 0 to trick monitoring systems into reading a full tank.
*   **Safety Interlock Override (Command Injection):** Wrote `TRUE` to Coil 0 (`PUMP_CMD`), forcing the industrial pump to run continuously despite the tank supposedly being full—a scenario that would cause a catastrophic overflow or mechanical failure in the real world.
*   **Setpoint Tampering:** Overwrote Holding Register 1 (`LEVEL_SETPOINT`) to `0` to disrupt the standard operating parameters.

Because Modbus inherently trusts all traffic on the network, the PLC blindly accepted and executed the injected payload.

*(Insert your Attack Execution and altered HMI logs screenshot here)*

## Phase 3: Developing the NIDS Defense Mechanism
**Objective:** Engineer a passive network defense tool to detect unauthenticated write commands targeted at the PLC.

Because standard Modbus traffic cannot be encrypted or authenticated without breaking legacy equipment, defense relies on monitoring the wire. A Python-based Network Intrusion Detection System (`nids.py`) was developed using the `scapy` library.

**Detection Logic:**
*   The script monitored the network for raw TCP packets traversing port 502.
*   It dissected the 7-byte Modbus Application Protocol (MBAP) header.
*   It isolated the 8th byte (the Function Code) to determine the packet's intent.
*   If the packet utilized Function Codes 5, 6, 15, or 16 (Modbus WRITE commands), it instantly flagged the source IP and generated a critical alert, as legitimate HMIs primarily utilize READ commands during standard operations.

## Phase 4: Container Network Topology and Routing Resolution
**Objective:** Ensure the NIDS successfully intercepts traffic routed through virtualized container networks.

Initial deployments of the NIDS failed to capture the attack traffic. Troubleshooting revealed a network topology discrepancy: because the OpenPLC instance was hosted inside a Podman container, the Modbus packets were not traveling across the local loopback (`lo`) interface. Instead, the OS routed them through a virtual network bridge.

**The Fix:**
The `scapy` sniffing parameters were reconfigured to explicitly tap into the Podman virtual interfaces.


```python
# Final Sniffing Configuration
sniff(iface=["podman0", "veth0"], filter="tcp port 502", prn=detect_modbus_attack, store=0)
<img width="1920" height="1080" alt="detectionscreen" src="https://github.com/user-attachments/assets/b1400898-0fec-48a9-ac28-54c59128f448" />
