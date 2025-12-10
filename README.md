# Miniature Substation Automation Project  
*A complete IEC 61850-enabled training, testing, and demonstration platform.*

This project implements a fully automated **miniature high-voltage substation**, including switchyard, protection relay, CT simulation, medium-voltage switchgear, an IEC 61850/IEC 60870-5-104 gateway, HMI, and a central SCADA system.

The goal is to create a realistic environment for experimenting with:

- IEC 61850 servers/clients  
- GOOSE and MMS communication  
- Protection-relay logic and interlocking  
- SCADA integration  
- Mixed-protocol environments (Modbus, IEC 104, IEC 61850)  
- Hardware–software co-simulation  
- Educational and research applications  

The project integrates **Raspberry Pi**, **Arduino**, **Linux PCs**, and multiple open-source automation components.

---

## 🔌 System Overview

**Components:**

- **Switchyard Model**
  - Raspberry Pi with servo-hat
  - 4 miniature circuit breakers
  - 10 disconnectors (motorized/servo)
  - Local I/O logic

- **Protection Relay Model**
  - Raspberry Pi with LCD display
  - Receives CT readings from Arduino
  - Implements simplified protection logic (overcurrent, interlocking, trip commands)

- **CT Measurement Unit**
  - Arduino with analog inputs
  - Sends current readings over serial to relay
  - Provides Modbus TCP interface for MS switchgear I/O

- **Gateway / RTU**
  - Raspberry Pi
  - Runs IEC 61850 ↔ IEC 60870-5-104 gateway

- **HMI**
  - Asus EEE PC running Linux
  - Uses IEC 61850 client for SCADA-style interface

- **Central SCADA**
  - Multi-feeder overview
  - Alarm/event lists
  - Real-time topology view
  - Integration via IEC 61850 and IEC 104

---

## 🏗️ Architecture (High-Level)

```

```
                +------------------------+
                |     Central SCADA      |
                |  (open_scada_dms)      |
                +-----------+------------+
                            |
                            | IEC60870-5-104
                            v
                  +---------+---------+
                  |  IEC61850/104     |
                  |  Gateway / RTU    |
                  +---------+---------+
                            |
                    +-------+------+
                    |   IEC61850   |
                    |   MMS/GOOSE  |
                    +-------+------+
                            |
 +--------------------------+--------------------------+
 |                          |                          |
 v                          v                          v
```

+------------+         +----------------+         +------------------+
| Switchyard |         | Protection     |         | HMI (EEE PC)     |
| (Servo Pi) |<------->| Relay (LCD Pi) |<------->| IEC61850 Client  |
+------------+  GOOSE  +----------------+   MMS   +------------------+
|
v
+-----------+
| CT Unit   |
| Arduino   |
+-----------+

```

---

## 📁 Repository Structure

```

mini_substation_automation/
│
├── docs/
│   ├── architecture/
│   ├── communication_maps/
│   ├── SCL_files/
│   └── hardware/
│
├── hardware/
│   ├── switchyard/
│   ├── protection_relay/
│   ├── ct_arduino/
│   ├── ms_switchgear/
│   └── hmi_pc/
│
├── firmware/
│   ├── arduino_ct/
│   ├── arduino_modbus/
│   ├── rpi_switchyard/
│   └── rpi_relay/
│
├── software/
│   ├── iec61850/
│   │   ├── servers/
│   │   ├── clients/
│   │   ├── gateway_rtu/
│   │   └── utils/
│   ├── scada/
│   │   ├── central_scada/
│   │   ├── hmi_app/
│   │   └── data_models/
│   └── tools/
│
├── config/
│   ├── iec61850/
│   ├── modbus/
│   ├── hmi/
│   ├── scada/
│   └── gateway/
│
├── deps/
│   ├── libiec61850/
│   ├── iec61850_open_server/
│   ├── iec61850_open_client/
│   ├── iec61850_open_gateway/
│   └── open_scada_dms/
│
├── scripts/
├── tests/
├── .gitmodules
└── README.md

````

---

## 🧩 Included External Projects (Git Submodules)

The following upstream projects are included as **read-only Git submodules**:

- **libiec61850**  
- **iec61850_open_server**  
- **iec61850_open_client**  
- **iec61850_open_gateway**  
- **open_scada_dms**

All custom extensions or plugins for these live **inside this repository**, not inside the upstream code.

You may create local branches for experiments if needed.

---

## 🛠️ Building

### Clone with submodules:

```bash
git clone --recursive https://github.com/<yourname>/mini_substation_automation.git
````

If you forgot `--recursive`:

```bash
git submodule update --init --recursive
```

### Building the software stack

Each subcomponent has its own `README.md` under:

* `software/iec61850/servers/`
* `software/iec61850/clients/`
* `software/iec61850/gateway_rtu/`
* `software/scada/*`
* `firmware/*`
* `hardware/*`

Most IEC 61850 components follow:

```bash
mkdir build && cd build
cmake ..
make -j4
```

---

## 📡 Protocols Used

| Subsystem              | Protocols                          |
| ---------------------- | ---------------------------------- |
| IEC61850 Server/Client | MMS, GOOSE                         |
| Gateway/RTU            | IEC60870-5-104 → IEC61850 bridging |
| CT Arduino Unit        | Serial + Modbus TCP                |
| Switchyard RPi         | GOOSE (commands)                   |
| SCADA & HMI            | IEC61850 Client                    |

---

## 🧪 Testing

The `tests/` directory contains:

* Unit tests (firmware & C code)
* IEC61850 simulation tools
* Protocol fuzzing utilities
* End-to-end system tests (substation → SCADA)

Example:

```bash
cd tests/integration
./run_switchyard_sim.sh
```

---

## 🤝 Contributing

Contributions are welcome, especially in:

* IEC61850 data modeling
* SCL engineering
* Protection logic algorithms
* SCADA visualizations
* Hardware integration (servos, sensors, UI)

Please follow branching guidelines:

* `main` → stable project
* `dev` → active changes
* Feature branches: `feature/<name>`

Submodules should **not** be modified unless working on a dedicated branch.

---

## 📝 License

To be defined (MIT recommended unless restrictions apply).

---

## 📬 Contact

For questions, ideas, or collaboration:

* Project owner: **<your name>**
* GitHub: [https://github.com/](https://github.com/)<yourname>

---

Enjoy experimenting with your very own **miniature digital substation**! ⚡
This project aims to bring IEC61850 automation into a fun, hands-on, hardware-rich environment.

```

---

