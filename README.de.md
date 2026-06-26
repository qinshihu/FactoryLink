# Industrielles Datenerfassungs-Gateway v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [English](./README.en.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## Was ist das?

Ein **einzelnes EXE, Doppelklick zum Starten, keine Abhängigkeiten, vollständig Open-Source und kostenlos** — ein industrielles Datenerfassungs-Gateway.

Entwickelt für Fertigungsingenieure, Fabrik-IT-Mitarbeiter und kleine Systemintegratoren.

## Warum wurde das entwickelt?

- Kommerzielle Gateways kosten über 1.000 € pro Stück — wir haben eine kostenlose Alternative geschaffen
- Andere Open-Source-Projekte erfordern Docker, was Fertigungsingenieure nicht bedienen können
- Die meisten internationalen Projekte haben keine chinesische Dokumentation, was die Fehlersuche erschwert

## Verwendung

1. [`FactoryLink.exe` herunterladen](https://github.com/qinshihu/FactoryLink/releases/latest)

2. Doppelklicken zum Starten (ein Taskleistensymbol erscheint unten rechts)

![Taskleistensymbol](images/1(2).png)

3. Der Browser öffnet automatisch die Konfigurationsseite (Standard: `http://localhost:8000`)

![Konfigurationsseite](images/1(1).png)

4. PLC-IP, Punktetabelle und MQTT-Adresse konfigurieren

  ![Gerätekonfiguration](images/1(4).png)

5. Auf „Datenerfassung starten" klicken — fertig!

> Rechtsklick auf das Taskleistensymbol: Konfigurationsseite öffnen, Erfassung starten/stoppen, Programm beenden.
> 
> Docker-Deployment wird ebenfalls unterstützt: [Docker-Deployment-Anleitung](#docker-deployment)

## Unterstützte Protokolle

| Protokoll | Unterstützte Modelle | Bibliothek |
|-----------|---------------------|------------|
| Modbus TCP | Alle standard Modbus TCP-Geräte | pymodbus 3.x |
| Modbus RTU | Alle standard Modbus RTU-Geräte (seriell) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (reines Python) |
| Mitsubishi MC | FX5U / Q-Serie / L-Serie | pymcprotocol |

## Kernfunktionen

- **Einzelne EXE**: Doppelklick zum Starten, keine Laufzeitumgebung erforderlich
- **Web-Konfigurationsoberfläche**: Konfiguration über Browser, keine Kommandozeilenkenntnisse nötig
- **Echtzeit-Datenansicht**: WebSocket-Push, Datenaktualisierung in Echtzeit
- **MQTT-Weiterleitung**: Automatische Weiterleitung erfasster Daten an MQTT-Server
- **Excel-Import**: Stapelimport von Punktkonfigurationen aus Excel-Tabellen mit Vorschau-Dialog
- **KI-Konfigurationsassistent**: Beschreiben Sie Ihr Gerät in natürlicher Sprache, KI generiert automatisch die Konfiguration (unterstützt OpenAI / Qwen / DeepSeek, SSE-Streaming + bearbeitbare Vorschau)
- **Geräteverbindungstest**: Ein-Klick-PLC-Verbindungstest
- **Automatische Wiederverbindung**: Automatische Wiederverbindung bei Netzwerkverlust mit exponentiellem Backoff
- **Autostart beim Booten**: Ein-Klick-Windows-Autostart-Konfiguration
- **Taskleiste**: Läuft im Hintergrund, Rechtsklick auf Taskleistensymbol für Operationen
- **Log-Viewer**: Erfassungsprotokolle direkt in der Web-Oberfläche mit Level-Filterung anzeigen
- **Hot-Reload**: Nach Konfigurationsänderungen auf „Übernehmen" klicken, um den Collector automatisch neu zu starten
- **Automatisches Backup**: Automatische Erstellung von `config.json.bak` bei jedem Speichern
- **Port-Konfliktbehandlung**: Automatischer Wechsel zu 8001, 8002... wenn Port 8000 belegt ist

## UI-Übersicht

| Seite | Funktionen |
|-------|-----------|
| **Startseite** | Gerätekartenliste, Echtzeitdatenanzeige, Start/Stopp-Taste, Geräte-Online-Status, MQTT-Verbindungsstatus |
| **Gerätekonfiguration** | Geräte hinzufügen/bearbeiten/löschen, protokollspezifische Konfiguration, Punktetabellen-CRUD, Excel-Import (Vorschau)/Vorlagen-Download, Verbindungstest, **KI-Konfigurationsassistent** (natürliche Sprache zu Gerätekonfiguration) |
| **Systemeinstellungen** | MQTT-Konfiguration, Erfassungsintervall, Wiederverbindungsstrategie, Autostart beim Booten, **KI-Einstellungen** (API-URL/Key/Modell), Log-Viewer (mit Level-Filterung) |

## Datenformat

### MQTT-Daten-Topic

```
{topic_prefix}/{device_id}
```

Beispiel: `factory/gateway-001/dev1`

### MQTT-Daten-Payload

```json
{
  "gateway": "Werkstatt-Gateway 1",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "Temperatur1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "Druck1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### Status-Topic

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "Verbindung erfolgreich",
  "timestamp": 1719123456789
}
```

- Status-Werte: `online` (normale Erfassung), `offline` (getrennt), `error` (Fehler)
- Quality-Werte: `good` (normal), `bad` (Lesefehler), `uncertain` (verdächtige Daten)

## Punkt-Datentypen

| Typ | Beschreibung | Bytes |
|-----|-------------|-------|
| bool | Boolean | 1 bit |
| int16 | 16-Bit vorzeichenbehaftete Ganzzahl | 2 |
| uint16 | 16-Bit vorzeichenlose Ganzzahl | 2 |
| int32 | 32-Bit vorzeichenbehaftete Ganzzahl | 4 |
| uint32 | 32-Bit vorzeichenlose Ganzzahl | 4 |
| float | 32-Bit Gleitkommazahl | 4 |
| double | 64-Bit Gleitkommazahl | 8 |

> Istwert = Rohwert × Faktor + Offset. Faktor und Offset werden in den Punkteinstellungen konfiguriert.

## Konfigurationsdatei

Alle Einstellungen werden in `config.json` im selben Verzeichnis wie die EXE gespeichert und bei Änderungen automatisch in `config.json.bak` gesichert.

```json
{
  "gateway_name": "Werkstatt-Gateway 1",
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
        {"name": "Temperatur1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
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
  },
  "ai": {
    "enabled": false,
    "api_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo"
  }
}
```

- `collect_interval`: Erfassungsintervall in Millisekunden, 1000 = einmal pro Sekunde
- `reconnect.max_retries`: 0 = unbegrenzte Wiederholungen
- Wiederholungsintervall: exponentieller Backoff, 1s → 2s → 4s → 8s → 16s → 32s → 60s (Obergrenze)

## Protokoll-Adressformate

### Modbus

| Adressbereich | Bereich | Beispiel |
|---------------|---------|----------|
| 40001-49999 | Holding Register | `40001` |
| 30001-39999 | Input Register | `30001` |
| 10001-19999 | Discrete Inputs | `10001` |
| 00001-09999 | Coils | `00001` |

### Siemens S7

| Format | Beschreibung | Beispiel |
|--------|-------------|----------|
| DBx.DBDy | DB-Block Doppelwort (32-Bit) | `DB1.DBD0` |
| DBx.DBXy.z | DB-Block Bit | `DB1.DBX8.0` |
| DBx.DBWy | DB-Block Wort (16-Bit) | `DB1.DBW0` |
| Mx.y | Speicherbit | `M0.0` |
| Ix.y | Eingangsbit | `I0.0` |
| Qx.y | Ausgangsbit | `Q0.0` |

> S7-1200/1500: rack=0, slot=1; S7-300/400: rack=0, slot=2

### Mitsubishi MC

| Format | Beschreibung | Beispiel |
|--------|-------------|----------|
| Dxxxx | Datenregister | `D100` |
| Mxxxx | Internes Relais | `M100` |
| Xx | Eingangsrelais | `X0` |
| Yx | Ausgangsrelais | `Y0` |
| Wxxxx | Link-Register | `W100` |

## Excel-Punktetabellenformat

| Punktname | Adresse | Datentyp | Faktor | Offset | Einheit |
|-----------|---------|----------|--------|--------|---------|
| Temperatur1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| Druck1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| Betriebsstatus | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- Erste Zeile ist die Kopfzeile (festes Format), Daten beginnen ab Zeile 2
- Unterstützt `.xlsx` und `.xls` Formate
- Vorlage auf der Gerätekonfigurationsseite herunterladbar

## Aus dem Quellcode ausführen

```bash
# 1. Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
venv\Scripts\activate

# 2. Python-Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Frontend bauen
cd frontend
npm install
npm run build
cd ..

# 4. Backend starten
cd backend
python main.py
```

Öffnen Sie `http://localhost:8000` im Browser.

## EXE erstellen

```bash
# Sicherstellen, dass das Frontend gebaut ist
cd frontend && npm run build && cd ..

# Build-Skript ausführen
build.bat
```

Ausgabe: `dist/FactoryLink.exe` (~25 MB)

## Docker-Deployment

Wenn Sie die EXE nicht verwenden möchten, können Sie Docker verwenden (geeignet für Server, Industrie-PCs, Raspberry Pi).

### Schnellstart

```bash
# Image pullen
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# Verzeichnisse für Konfiguration und Logs erstellen
mkdir -p /opt/factorylink/{logs,config}

# Container ausführen
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### Parameter-Referenz

| Parameter | Beschreibung |
|-----------|-------------|
| `-p 8000:8000` | Port der Web-Konfigurationsseite mappen |
| `-v /opt/factorylink/config:/app/config` | Konfigurationsverzeichnis mounten (config.json hier gespeichert) |
| `-v /opt/factorylink/logs:/app/logs` | Log-Verzeichnis mounten |
| `--restart always` | Automatischer Neustart bei Container-Fehler |

### Ersteinrichtung

1. Nach Container-Start `http://ihre-server-ip:8000` im Browser öffnen
2. PLC-Geräte und MQTT konfigurieren
3. Auf „Datenerfassung starten" klicken

> Hinweis: Die Docker-Version unterstützt **kein** Taskleistensymbol und keinen Autostart beim Booten (Windows-exklusive Funktionen).

### docker-compose verwenden

`docker-compose.yml` erstellen:

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

Starten:

```bash
docker-compose up -d
```

## Technologie-Stack

- **Backend**: Python 3.11+ / FastAPI / WebSocket / uvicorn
- **Frontend**: Vue 3 / Vite / Element Plus / xlsx
- **Protokollbibliotheken**: pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**: paho-mqtt
- **Paketierung**: PyInstaller 6.x (`--onefile --windowed`)
- **Taskleiste**: pystray + Pillow

## Projektstruktur

```
FactoryLink/
├── backend/
│   ├── main.py              # FastAPI-Einstiegspunkt (WebSocket, Tray, Port-Erkennung)
│   ├── config.py            # Konfigurationsverwaltung (Lesen/Schreiben, Backup, thread-sicher)
│   ├── logger.py            # Log-Verwaltung (10MB Rotation × 5, API-Lesen)
│   ├── schemas.py           # Pydantic-Datenmodelle
│   ├── collector/
│   │   ├── base.py          # Collector-Basisklasse (exponentieller Backoff-Reconnect, Hintergrund-Reconnect-Thread)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # MQTT-Weiterleitung (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Layout-Framework (Navigation, Logo, Autoreninfo)
│   │   ├── router.js        # Routen-Konfiguration
│   │   └── views/
│   │       ├── Home.vue          # Startseite (Gerätekarten, Echtzeitdaten, WebSocket)
│   │       ├── DeviceConfig.vue  # Gerätekonfiguration (CRUD, Punktverwaltung, Excel-Import)
│   │       └── Settings.vue      # Systemeinstellungen (MQTT, Erfassung, Reconnect, Autostart, Logs)
│   └── dist/                # Kompilierte statische Dateien
├── build.bat                # PyInstaller Build-Skript
├── requirements.txt         # Python-Abhängigkeitsliste
├── Dockerfile               # Docker-Image
└── README.md                # Diese Datei
```

## FAQ

**F: Beim Doppelklick auf die EXE passiert nichts?**

A: Überprüfen Sie die Taskleiste unten rechts auf das Gateway-Symbol. Wenn der Port belegt ist, wechselt das Programm automatisch den Port. Rechtsklicken Sie auf das Taskleistensymbol und wählen Sie „Konfigurationsseite öffnen".

**F: Keine Verbindung zur PLC möglich?**

A: Klicken Sie zuerst auf der Gerätekonfigurationsseite auf „Verbindung testen", um IP, Port, Rack/Slot-Nummern zu überprüfen. Siemens S7-1200/1500 verwendet rack=0, slot=1; S7-300/400 verwendet rack=0, slot=2.

**F: MQTT empfängt keine Daten?**

A: Überprüfen Sie, ob MQTT-Serveradresse und Port korrekt sind und MQTT aktiviert ist. Sehen Sie sich die Logs auf der Systemeinstellungsseite an, um Verbindungsfehler zu diagnostizieren.

**F: Wie importiere ich Punkte im Stapel?**

A: Laden Sie die Excel-Vorlage von der Gerätekonfigurationsseite herunter, füllen Sie sie aus und importieren Sie sie. Die Kopfzeile ist fest: Punktname, Adresse, Datentyp, Faktor, Offset, Einheit.

**F: Wie konfiguriere ich den Modbus RTU seriellen Port?**

A: Geben Sie den Portnamen direkt ein, z.B. `COM3`, `COM4`. Standard-Baudrate ist 9600, Standard-Parität ist None (N).

**F: Welches Erfassungsintervall ist optimal?**

A: Standard ist 1000ms (1 Sekunde). Für schnelle PLCs sind 500ms möglich. Für langsamere Geräte werden 2000ms+ empfohlen. Zu kurze Intervalle können zu Lese-Timeouts führen.

---

Denn 90% der Fertigungsingenieure brauchen kein Cloud-Native oder Docker — sie wollen einfach ein einfaches, benutzerfreundliches Werkzeug, das funktioniert.

---

## Lizenz

Dieses Projekt ist unter der **Mozilla Public License 2.0 (MPL-2.0)** als Open Source lizenziert.

## Autor

**Tan Ce** — Unabhängiger Entwickler | Industrial IoT Explorer

- 📝 Blog: [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 E-Mail: huawei_network@foxmail.com
- 💬 WeChat Official Account: **IT Online**

![WeChat QR-Code](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce