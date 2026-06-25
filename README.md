# 工业数据采集网关 v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[English](./README.en.md) | [日本語](./README.ja.md) | [한국어](./README.ko.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## 这是什么？

一个**单EXE、双击就能跑、零依赖、完全开源免费**的工业设备数据采集网关。

专门给国内制造业的一线工程师、工厂IT、小集成商使用。

## 为什么做这个？

- 某讯的采集网关卖1万块钱一台，我做个免费的给大家用
- 其他开源项目都要Docker，车间工程师根本不会用
- 所有国外项目都没有中文文档，出了问题找不到人问

## 怎么用？

1. [下载 `工业数据采集网关.exe`](https://github.com/qinshihu/FactoryLink/releases/latest)

2. 双击运行（右下角会出现托盘图标）

![托盘图标](images/1(2).png)

3. 浏览器自动打开配置页面（默认 `http://localhost:8000`）

![配置页面](images/1(1).png)

4. 配置你的PLC IP、点位表、MQTT地址

  ![设备配置](images/1(4).png)

5. 点"启动采集"，完事了

> 右键托盘图标可以：打开配置页面、启动/停止采集、退出程序。
> 
> 也可以用 Docker 部署：[Docker 部署说明](#docker-部署)

## 支持的协议

| 协议 | 支持型号 | 依赖库 |
|------|---------|--------|
| Modbus TCP | 所有标准Modbus TCP设备 | pymodbus 3.x |
| Modbus RTU | 所有标准Modbus RTU设备（串口） | pymodbus 3.x |
| 西门子S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0（纯Python） |
| 三菱MC | FX5U / Q系列 / L系列 | pymcprotocol |

## 核心功能

- **单EXE启动**：双击运行，不需要装任何运行环境
- **Web配置界面**：浏览器打开就能配置，不需要懂命令行
- **实时数据查看**：WebSocket推送，数据实时刷新
- **MQTT转发**：自动将采集数据转发到MQTT服务器
- **Excel导入**：支持从Excel表格批量导入点位配置
- **设备连接测试**：一键测试PLC连通性
- **断线重连**：网络断开自动重连，指数退避策略
- **开机自启动**：一键设置Windows开机自启动
- **系统托盘**：后台运行，右键托盘图标操作
- **日志查看**：Web界面直接查看采集日志，支持按级别筛选
- **配置热加载**：改完配置点"应用"，自动重启采集器
- **配置自动备份**：每次保存自动生成 `config.json.bak`
- **端口冲突处理**：8000被占用自动换8001、8002...

## 界面说明

| 页面 | 功能 |
|------|------|
| **首页** | 设备卡片列表、实时数据展示、采集启停按钮、设备在线状态、MQTT连接状态 |
| **设备配置** | 添加/编辑/删除设备、按协议显示配置项、点位表格增删改、Excel导入/模板下载、测试连接 |
| **系统设置** | MQTT配置、采集间隔、重连策略、开机自启动、日志查看（支持级别筛选） |

## 数据格式

### MQTT数据Topic

```
{topic_prefix}/{device_id}
```

示例：`factory/gateway-001/dev1`

### MQTT数据报文

```json
{
  "gateway": "车间1号网关",
  "device_id": "dev1",
  "device_name": "西门子S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "温度1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "压力1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### 状态Topic

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "连接成功",
  "timestamp": 1719123456789
}
```

- status取值：`online`（正常采集）、`offline`（断线）、`error`（异常）
- quality取值：`good`（正常）、`bad`（读取失败）、`uncertain`（数据可疑）

## 点位数据类型

| 类型 | 说明 | 字节数 |
|------|------|--------|
| bool | 布尔量 | 1 bit |
| int16 | 16位有符号整数 | 2 |
| uint16 | 16位无符号整数 | 2 |
| int32 | 32位有符号整数 | 4 |
| uint32 | 32位无符号整数 | 4 |
| float | 32位浮点数 | 4 |
| double | 64位浮点数 | 8 |

> 实际值 = 原始值 × 倍率 + 偏移量。倍率和偏移量在点位配置中设置。

## 配置文件

所有配置保存在与EXE同目录的 `config.json` 文件中，修改后自动备份为 `config.json.bak`。

```json
{
  "gateway_name": "车间1号网关",
  "devices": [
    {
      "id": "dev1",
      "name": "西门子S7-1200",
      "protocol": "s7",
      "ip": "192.168.1.100",
      "rack": 0,
      "slot": 1,
      "enabled": true,
      "points": [
        {"name": "温度1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
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

- `collect_interval`：采集间隔，单位毫秒，1000 = 每秒采集一次
- `reconnect.max_retries`：0 = 无限重试
- 重试间隔：指数退避，1s → 2s → 4s → 8s → 16s → 32s → 60s（封顶）

## 协议地址格式

### Modbus

| 地址范围 | 区域 | 示例 |
|---------|------|------|
| 40001-49999 | 保持寄存器 | `40001` |
| 30001-39999 | 输入寄存器 | `30001` |
| 10001-19999 | 离散输入 | `10001` |
| 00001-09999 | 线圈 | `00001` |

### 西门子S7

| 格式 | 说明 | 示例 |
|------|------|------|
| DBx.DBDy | DB块双字（32位） | `DB1.DBD0` |
| DBx.DBXy.z | DB块位 | `DB1.DBX8.0` |
| DBx.DBWy | DB块字（16位） | `DB1.DBW0` |
| Mx.y | 内存位 | `M0.0` |
| Ix.y | 输入位 | `I0.0` |
| Qx.y | 输出位 | `Q0.0` |

> S7-1200/1500：rack=0, slot=1；S7-300/400：rack=0, slot=2

### 三菱MC

| 格式 | 说明 | 示例 |
|------|------|------|
| Dxxxx | 数据寄存器 | `D100` |
| Mxxxx | 内部继电器 | `M100` |
| Xx | 输入继电器 | `X0` |
| Yx | 输出继电器 | `Y0` |
| Wxxxx | 链接寄存器 | `W100` |

## Excel点位表格式

| 点位名称 | 地址 | 数据类型 | 倍率 | 偏移 | 单位 |
|---------|------|---------|------|------|------|
| 温度1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| 压力1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| 运行状态 | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- 第一行为表头（固定格式），第二行开始为点位数据
- 支持 `.xlsx` 和 `.xls` 格式
- 在设备配置页可下载模板

## 从源码运行

```bash
# 1. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 编译前端
cd frontend
npm install
npm run build
cd ..

# 4. 启动后端
cd backend
python main.py
```

浏览器打开 `http://localhost:8000`。

## 打包成EXE

```bash
# 确保前端已编译
cd frontend && npm run build && cd ..

# 执行打包
build.bat
```

输出文件：`dist/工业数据采集网关.exe`（约25MB）

## Docker 部署

如果不想用 EXE，也可以用 Docker 方式运行（适合部署在服务器、工控机、树莓派上）。

### 快速启动

```bash
# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# 创建目录存放配置和日志
mkdir -p /opt/factorylink/{logs,config}

# 运行容器
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-p 8000:8000` | 映射 Web 配置页面端口 |
| `-v /opt/factorylink/config:/app/config` | 挂载配置目录（config.json 保存在这里） |
| `-v /opt/factorylink/logs:/app/logs` | 挂载日志目录 |
| `--restart always` | 容器异常退出自动重启 |

### 首次使用

1. 容器启动后，浏览器打开 `http://你的服务器IP:8000`
2. 配置 PLC 设备和 MQTT
3. 点击"启动采集"

> 注意：Docker 版本**不支持**系统托盘图标和开机自启动功能（这两个是 Windows 专属）。

### 使用 docker-compose

创建 `docker-compose.yml`：

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

启动：

```bash
docker-compose up -d
```

## 技术栈

- **后端**：Python 3.11+ / FastAPI / WebSocket / uvicorn
- **前端**：Vue 3 / Vite / Element Plus / xlsx
- **协议库**：pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**：paho-mqtt
- **打包**：PyInstaller 6.x（`--onefile --windowed`）
- **托盘**：pystray + Pillow

## 项目结构

```
FactoryLink/
├── backend/
│   ├── main.py              # FastAPI入口（WebSocket、托盘、端口检测）
│   ├── config.py            # 配置管理（读写、备份、线程安全）
│   ├── logger.py            # 日志管理（10MB轮转×5、API读取）
│   ├── schemas.py           # Pydantic数据模型
│   ├── collector/
│   │   ├── base.py          # 采集器基类（指数退避重连、后台重连线程）
│   │   ├── modbus.py        # Modbus TCP/RTU（pymodbus）
│   │   ├── s7.py            # 西门子S7（python-snap7 3.0）
│   │   └── mitsubishi.py    # 三菱MC（pymcprotocol）
│   └── forwarder/
│       └── mqtt.py          # MQTT转发（paho-mqtt）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 布局框架（导航、Logo、作者信息）
│   │   ├── router.js        # 路由配置
│   │   └── views/
│   │       ├── Home.vue          # 首页（设备卡片、实时数据、WebSocket）
│   │       ├── DeviceConfig.vue  # 设备配置（增删改、点位管理、Excel导入）
│   │       └── Settings.vue      # 系统设置（MQTT、采集、重连、自启动、日志）
│   └── dist/                # 编译后的静态文件
├── build.bat                # PyInstaller打包脚本
├── requirements.txt         # Python依赖清单
├── Dockerfile               # Docker镜像
└── README.md                # 本文件
```

## 常见问题

**Q: 双击EXE没反应？**

A: 查看右下角系统托盘是否有网关图标。如果端口被占用，程序会自动换端口，右键托盘图标选择"打开配置页面"。

**Q: 连接PLC失败？**

A: 先在设备配置页点"测试连接"按钮，确认IP、端口、机架号/插槽号是否正确。西门子S7-1200/1500用rack=0,slot=1，S7-300/400用rack=0,slot=2。

**Q: MQTT收不到数据？**

A: 检查MQTT服务器地址、端口是否正确，确认MQTT已启用。查看系统设置页的日志，排查连接错误。

**Q: 如何批量导入点位？**

A: 在设备配置页下载Excel模板，按格式填写后导入。表头固定为：点位名称、地址、数据类型、倍率、偏移、单位。

**Q: Modbus RTU串口号怎么填？**

A: 直接填串口号，如 `COM3`、`COM4`。波特率默认9600，校验位默认无校验(N)。

**Q: 采集间隔设多少合适？**

A: 默认1000ms（1秒）。PLC响应快可以设500ms，慢的设备建议2000ms以上。太短可能导致读取超时。

---

因为90%的车间工程师，他们不需要什么云原生，不需要什么Docker，他们就想要一个简单、好用、能解决问题的工具。

---

## 许可证

本项目采用 **Mozilla Public License 2.0 (MPL-2.0)** 许可证开源。

## 作者

**谭策** — 独立开发者 | 工业物联网领域探索者

- 📝 博客：[https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 邮箱：huawei_network@foxmail.com
- 💬 微信公众号：**IT Online**

<img src="images/公众号背面.png" width="300" alt="公众号背面">

---

[MPL-2.0](./LICENSE) © 谭策
