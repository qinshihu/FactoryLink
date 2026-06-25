# Industrial Data Acquisition Gateway v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## What is this?

A **single EXE, double-click to run, zero dependencies, completely open-source and free** industrial device data acquisition gateway.

Designed for frontline engineers, factory IT staff, and small system integrators in the manufacturing industry.

## Why build this?

- Some commercial acquisition gateways cost $1,500+ per unit — we made a free one for everyone
- Other open-source projects require Docker, which shop-floor engineers can't use
- Most international projects lack Chinese documentation, making troubleshooting difficult

## How to Use?

1. [Download `FactoryLink.exe`](https://github.com/qinshihu/FactoryLink/releases/latest)

2. Double-click to run (a system tray icon will appear in the bottom-right corner)

![Tray Icon](images/1 (2).png)

3. The browser will automatically open the configuration page (default `http://localhost:8000`)

![Configuration Page](images/1 (1).png)

4. Configure your PLC IP, point table, and MQTT address

  ![Device Configuration](images/1 (4).png)

5. Click "Start Acquisition" — done!

> Right-click the tray icon to: open configuration page, start/stop acquisition, or exit the program.
> 
> Docker deployment is also supported: [Docker Deployment Guide](#docker-deployment)

## Supported Protocols

| Protocol | Supported Models | Library |
|----------|------------------|---------|
| Modbus TCP | All standard Modbus TCP devices | pymodbus 3.x |
| Modbus RTU | All standard Modbus RTU devices (serial) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (pure Python) |
| Mitsubishi MC | FX5U / Q Series / L Series | pymcprotocol |

## Core Features

- **Single EXE**: Double-click to run, no runtime environment required
- **Web Configuration UI**: Configure via browser, no command-line knowledge needed
- **Real-time Data View**: WebSocket push, data refreshes in real time
- **MQTT Forwarding**: Automatically forwards collected data to MQTT server
- **Excel Import**: Batch import point configurations from Excel spreadsheets
- **Device Connection Test**: One-click PLC connectivity test
- **Auto Reconnection**: Automatic reconnection on network loss with exponential backoff
- **Auto-start on Boot**: One-click Windows startup configuration
- **System Tray**: Runs in background, right-click tray icon for operations
- **Log Viewer**: View acquisition logs directly in web UI with level filtering
- **Hot Reload**: Click "Apply" after config changes to automatically restart collector
- **Auto Backup**: Auto-generates `config.json.bak` on every save
- **Port Conflict Handling**: Auto-switches to 8001, 8002... if port 8000 is occupied

## UI Overview

| Page | Functions |
|------|-----------|
| **Home** | Device card list, real-time data display, acquisition start/stop button, device online status, MQTT connection status |
| **Device Config** | Add/edit/delete devices, protocol-specific configuration, point table CRUD, Excel import/template download, connection test |
| **System Settings** | MQTT configuration, collection interval, reconnection strategy, auto-start on boot, log viewer (with level filtering) |

## Data Format

### MQTT Data Topic

```
{topic_prefix}/{device_id}
```

Example: `factory/gateway-001/dev1`

### MQTT Data Payload

```json
{
  "gateway": "Workshop Gateway #1",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "Temperature1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "Pressure1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### Status Topic

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "Connected successfully",
  "timestamp": 1719123456789
}
```

- status values: `online` (normal acquisition), `offline` (disconnected), `error` (abnormal)
- quality values: `good` (normal), `bad` (read failed), `uncertain` (suspicious data)

## Point Data Types

| Type | Description | Bytes |
|------|-------------|-------|
| bool | Boolean | 1 bit |
| int16 | 16-bit signed integer | 2 |
| uint16 | 16-bit unsigned integer | 2 |
| int32 | 32-bit signed integer | 4 |
| uint32 | 32-bit unsigned integer | 4 |
| float | 32-bit floating point | 4 |
| double | 64-bit floating point | 8 |

> Actual value = Raw value × Rate + Offset. Rate and offset are configured in the point settings.

## Configuration File

All configuration is saved in `config.json` in the same directory as the EXE. Auto-backed up to `config.json.bak` on every change.

```json
{
  "gateway_name": "Workshop Gateway #1",
  "devices": [
    {
      "id": "dev1",
      "name": "Siemens S7-1200",
      "protocol": "s7",
      "ip": "192.168.1.100",
      "rack": 0,
      "slot": 1,
      "enabled": true,
      "points": [
        {"name": "Temperature1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
      ]
    }
  ],
  "mqtt": {
    "host": "192.168.1.200",
    "port": 1883,
    "client_id": "gateway-001",
    "topic_prefix": "factory/gateway-001",
    "username": "",
    "password": "",
    "qos": 1,
    "enabled": true
  },
  "collect_interval": 1000,
  "reconnect": {
    "max_retries": 0,
    "base_delay": 1,
    "max_delay": 60
  }
}
```

- `collect_interval`: Collection interval in milliseconds, 1000 = once per second
- `reconnect.max_retries`: 0 = unlimited retries
- Retry interval: exponential backoff, 1s → 2s → 4s → 8s → 16s → 32s → 60s (capped)

## Protocol Address Formats

### Modbus

| Address Range | Area | Example |
|---------------|------|---------|
| 40001-49999 | Holding Registers | `40001` |
| 30001-39999 | Input Registers | `30001` |
| 10001-19999 | Discrete Inputs | `10001` |
| 00001-09999 | Coils | `00001` |

### Siemens S7

| Format | Description | Example |
|--------|-------------|---------|
| DBx.DBDy | DB block double word (32-bit) | `DB1.DBD0` |
| DBx.DBXy.z | DB block bit | `DB1.DBX8.0` |
| DBx.DBWy | DB block word (16-bit) | `DB1.DBW0` |
| Mx.y | Memory bit | `M0.0` |
| Ix.y | Input bit | `I0.0` |
| Qx.y | Output bit | `Q0.0` |

> S7-1200/1500: rack=0, slot=1; S7-300/400: rack=0, slot=2

### Mitsubishi MC

| Format | Description | Example |
|--------|-------------|---------|
| Dxxxx | Data Register | `D100` |
| Mxxxx | Internal Relay | `M100` |
| Xx | Input Relay | `X0` |
| Yx | Output Relay | `Y0` |
| Wxxxx | Link Register | `W100` |

## Excel Point Table Format

| Point Name | Address | Data Type | Rate | Offset | Unit |
|------------|---------|-----------|------|--------|------|
| Temperature1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| Pressure1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| Running Status | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- First row is the header (fixed format), data starts from row 2
- Supports `.xlsx` and `.xls` formats
- Download the template from the device configuration page

## Run from Source

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Build frontend
cd frontend
npm install
npm run build
cd ..

# 4. Start backend
cd backend
python main.py
```

Open `http://localhost:8000` in your browser.

## Build EXE

```bash
# Ensure frontend is built
cd frontend && npm run build && cd ..

# Run build script
build.bat
```

Output: `dist/FactoryLink.exe` (~25MB)

## Docker Deployment

If you prefer not to use the EXE, you can run with Docker (suitable for servers, industrial PCs, Raspberry Pi).

### Quick Start

```bash
# Pull image
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# Create directories for config and logs
mkdir -p /opt/factorylink/{logs,config}

# Run container
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### Parameter Reference

| Parameter | Description |
|-----------|-------------|
| `-p 8000:8000` | Map web configuration page port |
| `-v /opt/factorylink/config:/app/config` | Mount config directory (config.json stored here) |
| `-v /opt/factorylink/logs:/app/logs` | Mount log directory |
| `--restart always` | Auto-restart on container failure |

### First-Time Setup

1. After container starts, open `http://your-server-ip:8000` in browser
2. Configure PLC devices and MQTT
3. Click "Start Acquisition"

> Note: Docker version does **not** support system tray icon and auto-start on boot (Windows-only features).

### Using docker-compose

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  factorylink:
    image: registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
    container_name: factorylink
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
```

Start:

```bash
docker-compose up -d
```

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI / WebSocket / uvicorn
- **Frontend**: Vue 3 / Vite / Element Plus / xlsx
- **Protocol Libraries**: pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**: paho-mqtt
- **Packaging**: PyInstaller 6.x (`--onefile --windowed`)
- **System Tray**: pystray + Pillow

## Project Structure

```
FactoryLink/
├── backend/
│   ├── main.py              # FastAPI entry point (WebSocket, tray, port detection)
│   ├── config.py            # Configuration management (read/write, backup, thread-safe)
│   ├── logger.py            # Log management (10MB rotation × 5, API read)
│   ├── schemas.py           # Pydantic data models
│   ├── collector/
│   │   ├── base.py          # Collector base class (exponential backoff reconnect, background reconnect thread)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # MQTT forwarding (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Layout framework (navigation, logo, author info)
│   │   ├── router.js        # Route configuration
│   │   └── views/
│   │       ├── Home.vue          # Home page (device cards, real-time data, WebSocket)
│   │       ├── DeviceConfig.vue  # Device configuration (CRUD, point management, Excel import)
│   │       └── Settings.vue      # System settings (MQTT, collection, reconnect, auto-start, logs)
│   └── dist/                # Compiled static files
├── build.bat                # PyInstaller build script
├── requirements.txt         # Python dependency list
├── Dockerfile               # Docker image
└── README.md                # This file
```

## FAQ

**Q: Nothing happens when I double-click the EXE?**

A: Check the system tray in the bottom-right corner for the gateway icon. If the port is occupied, the program will auto-switch ports. Right-click the tray icon and select "Open Configuration Page".

**Q: Can't connect to PLC?**

A: First click "Test Connection" on the device configuration page to verify IP, port, rack/slot numbers. Siemens S7-1200/1500 use rack=0, slot=1; S7-300/400 use rack=0, slot=2.

**Q: MQTT not receiving data?**

A: Check that the MQTT server address and port are correct, and that MQTT is enabled. View logs on the system settings page to troubleshoot connection errors.

**Q: How to batch import points?**

A: Download the Excel template from the device configuration page, fill it in, and import. The header is fixed: Point Name, Address, Data Type, Rate, Offset, Unit.

**Q: How to set Modbus RTU serial port?**

A: Enter the port name directly, e.g., `COM3`, `COM4`. Default baud rate is 9600, default parity is None (N).

**Q: What's the best collection interval?**

A: Default is 1000ms (1 second). For fast PLCs, 500ms works. For slower devices, 2000ms+ is recommended. Too short may cause read timeouts.

---

Because 90% of shop-floor engineers don't need cloud-native or Docker — they just want a simple, easy-to-use tool that gets the job done.

---

## License

This project is open-sourced under the **Mozilla Public License 2.0 (MPL-2.0)**.

## Author

**Tan Ce** — Independent Developer | Industrial IoT Explorer

- 📝 Blog: [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 Email: huawei_network@foxmail.com
- 💬 WeChat Official Account: **IT Online**

![WeChat QR Code](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce
