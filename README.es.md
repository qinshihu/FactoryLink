# Gateway de Adquisición de Datos Industriales v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [English](./README.en.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## ¿Qué es esto?

Un **gateway de adquisición de datos industriales** en un **solo EXE, doble clic para ejecutar, cero dependencias, completamente open-source y gratuito**.

Diseñado para ingenieros de planta, personal de IT de fábrica y pequeños integradores de sistemas en la industria manufacturera.

## ¿Por qué crear esto?

- Los gateways comerciales cuestan más de 1.000 € por unidad — creamos uno gratuito para todos
- Otros proyectos open-source requieren Docker, que los ingenieros de taller no saben usar
- La mayoría de los proyectos internacionales no tienen documentación en chino, dificultando la resolución de problemas

## ¿Cómo usar?

1. [Descargar `FactoryLink.exe`](https://github.com/qinshihu/FactoryLink/releases/latest)

2. Doble clic para ejecutar (aparecerá un icono en la bandeja del sistema en la esquina inferior derecha)

![Icono de bandeja](images/1(2).png)

3. El navegador abrirá automáticamente la página de configuración (por defecto `http://localhost:8000`)

![Página de configuración](images/1(1).png)

4. Configure la IP de su PLC, tabla de puntos y dirección MQTT

![Configuración de dispositivo](images/1(4).png)  

5. Haga clic en "Iniciar adquisición" — ¡listo!

> Clic derecho en el icono de la bandeja para: abrir página de configuración, iniciar/detener adquisición, salir del programa.
> 
> También se admite el despliegue con Docker: [Guía de despliegue Docker](#despliegue-docker)

## Protocolos soportados

| Protocolo | Modelos soportados | Biblioteca |
|-----------|-------------------|------------|
| Modbus TCP | Todos los dispositivos Modbus TCP estándar | pymodbus 3.x |
| Modbus RTU | Todos los dispositivos Modbus RTU estándar (serial) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (Python puro) |
| Mitsubishi MC | FX5U / Serie Q / Serie L | pymcprotocol |

## Funcionalidades principales

- **EXE único**: Doble clic para ejecutar, sin necesidad de entorno de ejecución
- **Interfaz Web**: Configuración mediante navegador, sin conocimientos de línea de comandos
- **Datos en tiempo real**: Push por WebSocket, datos actualizados en tiempo real
- **Reenvío MQTT**: Reenvío automático de datos recolectados al servidor MQTT
- **Importación Excel**: Importación masiva de configuraciones de puntos desde hojas Excel
- **Prueba de conexión**: Prueba de conectividad PLC con un solo clic
- **Reconexión automática**: Reconexión automática ante pérdida de red con retroceso exponencial
- **Inicio automático**: Configuración de inicio de Windows con un solo clic
- **Bandeja del sistema**: Ejecución en segundo plano, clic derecho en el icono para operaciones
- **Visor de logs**: Visualización de logs de adquisición directamente en la interfaz web con filtrado por nivel
- **Recarga en caliente**: Haga clic en "Aplicar" tras cambios de configuración para reiniciar automáticamente el colector
- **Copia de seguridad automática**: Generación automática de `config.json.bak` en cada guardado
- **Manejo de conflictos de puerto**: Cambio automático a 8001, 8002... si el puerto 8000 está ocupado

## Descripción de la interfaz

| Página | Funciones |
|--------|-----------|
| **Inicio** | Lista de tarjetas de dispositivos, visualización de datos en tiempo real, botón iniciar/detener, estado en línea de dispositivos, estado de conexión MQTT |
| **Config. Dispositivo** | Añadir/editar/eliminar dispositivos, configuración por protocolo, CRUD de tabla de puntos, importación Excel/descarga de plantilla, prueba de conexión |
| **Config. Sistema** | Configuración MQTT, intervalo de recolección, estrategia de reconexión, inicio automático, visor de logs (con filtrado por nivel) |

## Formato de datos

### Topic de datos MQTT

```
{topic_prefix}/{device_id}
```

Ejemplo: `factory/gateway-001/dev1`

### Carga útil MQTT

```json
{
  "gateway": "Gateway Taller 1",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "Temperatura1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "Presión1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### Topic de estado

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "Conexión exitosa",
  "timestamp": 1719123456789
}
```

- Valores de status: `online` (adquisición normal), `offline` (desconectado), `error` (anomalía)
- Valores de quality: `good` (normal), `bad` (fallo de lectura), `uncertain` (datos sospechosos)

## Tipos de datos de puntos

| Tipo | Descripción | Bytes |
|------|-------------|-------|
| bool | Booleano | 1 bit |
| int16 | Entero con signo de 16 bits | 2 |
| uint16 | Entero sin signo de 16 bits | 2 |
| int32 | Entero con signo de 32 bits | 4 |
| uint32 | Entero sin signo de 32 bits | 4 |
| float | Punto flotante de 32 bits | 4 |
| double | Punto flotante de 64 bits | 8 |

> Valor real = Valor bruto × Factor + Desplazamiento. El factor y el desplazamiento se configuran en los ajustes del punto.

## Archivo de configuración

Toda la configuración se guarda en `config.json` en el mismo directorio que el EXE, con copia de seguridad automática en `config.json.bak` en cada cambio.

```json
{
  "gateway_name": "Gateway Taller 1",
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
        {"name": "Temperatura1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
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

- `collect_interval`: Intervalo de recolección en milisegundos, 1000 = una vez por segundo
- `reconnect.max_retries`: 0 = reintentos ilimitados
- Intervalo de reintento: retroceso exponencial, 1s → 2s → 4s → 8s → 16s → 32s → 60s (límite)

## Formatos de dirección de protocolos

### Modbus

| Rango de direcciones | Área | Ejemplo |
|---------------------|------|---------|
| 40001-49999 | Registros de retención | `40001` |
| 30001-39999 | Registros de entrada | `30001` |
| 10001-19999 | Entradas discretas | `10001` |
| 00001-09999 | Bobinas | `00001` |

### Siemens S7

| Formato | Descripción | Ejemplo |
|---------|-------------|---------|
| DBx.DBDy | Palabra doble de bloque DB (32 bits) | `DB1.DBD0` |
| DBx.DBXy.z | Bit de bloque DB | `DB1.DBX8.0` |
| DBx.DBWy | Palabra de bloque DB (16 bits) | `DB1.DBW0` |
| Mx.y | Bit de memoria | `M0.0` |
| Ix.y | Bit de entrada | `I0.0` |
| Qx.y | Bit de salida | `Q0.0` |

> S7-1200/1500: rack=0, slot=1; S7-300/400: rack=0, slot=2

### Mitsubishi MC

| Formato | Descripción | Ejemplo |
|---------|-------------|---------|
| Dxxxx | Registro de datos | `D100` |
| Mxxxx | Relé interno | `M100` |
| Xx | Relé de entrada | `X0` |
| Yx | Relé de salida | `Y0` |
| Wxxxx | Registro de enlace | `W100` |

## Formato de tabla Excel de puntos

| Nombre del punto | Dirección | Tipo de dato | Factor | Desplazamiento | Unidad |
|-----------------|-----------|-------------|--------|---------------|--------|
| Temperatura1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| Presión1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| Estado marcha | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- La primera fila es el encabezado (formato fijo), los datos comienzan desde la fila 2
- Soporta formatos `.xlsx` y `.xls`
- Descargue la plantilla desde la página de configuración del dispositivo

## Ejecutar desde el código fuente

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Compilar el frontend
cd frontend
npm install
npm run build
cd ..

# 4. Iniciar el backend
cd backend
python main.py
```

Abra `http://localhost:8000` en su navegador.

## Compilar a EXE

```bash
# Asegurarse de que el frontend está compilado
cd frontend && npm run build && cd ..

# Ejecutar script de compilación
build.bat
```

Salida: `dist/FactoryLink.exe` (~25 MB)

## Despliegue Docker

Si prefiere no usar el EXE, puede ejecutar con Docker (adecuado para servidores, PCs industriales, Raspberry Pi).

### Inicio rápido

```bash
# Descargar imagen
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# Crear directorios para configuración y logs
mkdir -p /opt/factorylink/{logs,config}

# Ejecutar contenedor
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### Referencia de parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `-p 8000:8000` | Mapear puerto de la página de configuración web |
| `-v /opt/factorylink/config:/app/config` | Montar directorio de configuración (config.json se guarda aquí) |
| `-v /opt/factorylink/logs:/app/logs` | Montar directorio de logs |
| `--restart always` | Reinicio automático ante fallo del contenedor |

### Primera configuración

1. Después de iniciar el contenedor, abra `http://ip-de-su-servidor:8000` en el navegador
2. Configure los dispositivos PLC y MQTT
3. Haga clic en "Iniciar adquisición"

> Nota: La versión Docker **no soporta** el icono de la bandeja del sistema ni el inicio automático (funcionalidades exclusivas de Windows).

### Usar docker-compose

Cree `docker-compose.yml`:

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

Iniciar:

```bash
docker-compose up -d
```

## Stack tecnológico

- **Backend**: Python 3.11+ / FastAPI / WebSocket / uvicorn
- **Frontend**: Vue 3 / Vite / Element Plus / xlsx
- **Bibliotecas de protocolo**: pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**: paho-mqtt
- **Empaquetado**: PyInstaller 6.x (`--onefile --windowed`)
- **Bandeja del sistema**: pystray + Pillow

## Estructura del proyecto

```
FactoryLink/
├── backend/
│   ├── main.py              # Punto de entrada FastAPI (WebSocket, bandeja, detección de puerto)
│   ├── config.py            # Gestión de configuración (lectura/escritura, copia de seguridad, thread-safe)
│   ├── logger.py            # Gestión de logs (rotación 10 MB × 5, lectura API)
│   ├── schemas.py           # Modelos de datos Pydantic
│   ├── collector/
│   │   ├── base.py          # Clase base del colector (reconexión con retroceso exponencial, hilo de reconexión)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # Reenvío MQTT (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Framework de diseño (navegación, logo, info del autor)
│   │   ├── router.js        # Configuración de rutas
│   │   └── views/
│   │       ├── Home.vue          # Página de inicio (tarjetas de dispositivos, datos en tiempo real, WebSocket)
│   │       ├── DeviceConfig.vue  # Configuración de dispositivo (CRUD, gestión de puntos, importación Excel)
│   │       └── Settings.vue      # Configuración del sistema (MQTT, recolección, reconexión, inicio auto, logs)
│   └── dist/                # Archivos estáticos compilados
├── build.bat                # Script de compilación PyInstaller
├── requirements.txt         # Lista de dependencias Python
├── Dockerfile               # Imagen Docker
└── README.md                # Este archivo
```

## Preguntas frecuentes

**P: ¿No pasa nada al hacer doble clic en el EXE?**

R: Revise la bandeja del sistema en la esquina inferior derecha para ver el icono del gateway. Si el puerto está ocupado, el programa cambiará automáticamente de puerto. Haga clic derecho en el icono y seleccione "Abrir página de configuración".

**P: ¿No se puede conectar al PLC?**

R: Primero haga clic en "Probar conexión" en la página de configuración del dispositivo para verificar IP, puerto, números de rack/slot. Siemens S7-1200/1500 usa rack=0, slot=1; S7-300/400 usa rack=0, slot=2.

**P: ¿MQTT no recibe datos?**

R: Verifique que la dirección y el puerto del servidor MQTT sean correctos y que MQTT esté habilitado. Consulte los logs en la página de configuración del sistema para diagnosticar errores de conexión.

**P: ¿Cómo importar puntos en lote?**

R: Descargue la plantilla Excel desde la página de configuración del dispositivo, rellénela e impórtela. El encabezado es fijo: Nombre del punto, Dirección, Tipo de dato, Factor, Desplazamiento, Unidad.

**P: ¿Cómo configurar el puerto serie Modbus RTU?**

R: Ingrese el nombre del puerto directamente, por ejemplo `COM3`, `COM4`. La velocidad en baudios predeterminada es 9600, la paridad predeterminada es Ninguna (N).

**P: ¿Qué intervalo de recolección es óptimo?**

R: El valor predeterminado es 1000 ms (1 segundo). Para PLCs rápidos, 500 ms es posible. Para dispositivos más lentos, se recomiendan 2000 ms+. Un intervalo demasiado corto puede causar timeouts de lectura.

---

Porque el 90% de los ingenieros de taller no necesitan cloud-native ni Docker — solo quieren una herramienta simple y fácil de usar que funcione.

---

## Licencia

Este proyecto es open-source bajo la licencia **Mozilla Public License 2.0 (MPL-2.0)**.

## Autor

**Tan Ce** — Desarrollador independiente | Explorador de IoT industrial

- 📝 Blog: [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 Email: huawei_network@foxmail.com
- 💬 Cuenta oficial de WeChat: **IT Online**

![Código QR WeChat](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce
