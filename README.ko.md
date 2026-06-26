# 산업용 데이터 수집 게이트웨이 v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [English](./README.en.md) | [日本語](./README.ja.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## 이게 뭔가요?

**단일 EXE, 더블클릭으로 실행, 의존성 제로, 완전 오픈소스 & 무료** 산업용 디바이스 데이터 수집 게이트웨이입니다.

제조업 현장 엔지니어, 공장 IT 담당자, 소규모 시스템 통합업체를 위해 설계되었습니다.

## 왜 만들었나요?

-某 상용 수집 게이트웨이는 대당 1만 위안(약 180만원)이나 해서, 무료로 만들었습니다
- 다른 오픈소스 프로젝트는 Docker가 필요해서 현장 엔지니어가 사용할 수 없습니다
- 해외 프로젝트는 중국어 문서가 없어 문제가 생겨도 해결할 수 없습니다

## 사용 방법

1. [`FactoryLink.exe` 다운로드](https://github.com/qinshihu/FactoryLink/releases/latest)

2. 더블클릭으로 실행 (우측 하단에 트레이 아이콘이 표시됩니다)

![트레이 아이콘](images/1(2).png)

3. 브라우저가 자동으로 설정 페이지를 엽니다 (기본값 `http://localhost:8000`)

![설정 페이지](images/1(1).png)

4. PLC IP, 포인트 테이블, MQTT 주소를 설정합니다

  ![디바이스 설정](images/1(4).png)

5. "수집 시작"을 클릭하면 끝입니다!

> 트레이 아이콘을 우클릭하면: 설정 페이지 열기, 수집 시작/중지, 프로그램 종료가 가능합니다.
> 
> Docker 배포도 지원합니다: [Docker 배포 가이드](#docker-배포)

## 지원 프로토콜

| 프로토콜 | 지원 모델 | 라이브러리 |
|---------|---------|----------|
| Modbus TCP | 모든 표준 Modbus TCP 디바이스 | pymodbus 3.x |
| Modbus RTU | 모든 표준 Modbus RTU 디바이스 (시리얼) | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0 (순수 Python) |
| Mitsubishi MC | FX5U / Q 시리즈 / L 시리즈 | pymcprotocol |

## 주요 기능

- **단일 EXE**: 더블클릭으로 실행, 런타임 환경 불필요
- **Web 설정 UI**: 브라우저로 설정 가능, 명령줄 지식 불필요
- **실시간 데이터 뷰**: WebSocket 푸시, 데이터 실시간 갱신
- **MQTT 전달**: 수집 데이터를 자동으로 MQTT 서버에 전달
- **Excel 가져오기**: Excel에서 포인트 설정 일괄 가져오기 (미리보기 확인 대화상자 포함)
- **AI 설정 도우미**: 자연어로 디바이스를 설명하면 AI가 자동으로 설정 생성 (OpenAI / Qwen / DeepSeek 지원, SSE 스트리밍 + 편집 가능 미리보기)
- **디바이스 연결 테스트**: 원클릭 PLC 연결 테스트
- **자동 재연결**: 네트워크 끊김 시 지수 백오프로 자동 재연결
- **부팅 시 자동 시작**: 원클릭 Windows 시작 프로그램 설정
- **시스템 트레이**: 백그라운드 실행, 트레이 아이콘 우클릭으로 조작
- **로그 뷰어**: Web UI에서 수집 로그 확인, 레벨 필터링 지원
- **핫 리로드**: 설정 변경 후 "적용" 클릭으로 자동 수집기 재시작
- **자동 백업**: 저장 시마다 `config.json.bak` 자동 생성
- **포트 충돌 처리**: 8000 사용 중이면 자동으로 8001, 8002...로 전환

## UI 개요

| 페이지 | 기능 |
|------|------|
| **홈** | 디바이스 카드 목록, 실시간 데이터 표시, 수집 시작/중지 버튼, 디바이스 온라인 상태, MQTT 연결 상태 |
| **디바이스 설정** | 디바이스 추가/편집/삭제, 프로토콜별 설정 항목, 포인트 테이블 CRUD, Excel 가져오기 (미리보기 확인)/템플릿 다운로드, 연결 테스트, **AI 설정 도우미** (자연어로 디바이스 설정 생성) |
| **시스템 설정** | MQTT 설정, 수집 간격, 재연결 전략, 부팅 시 자동 시작, **AI 설정** (API URL/Key/모델), 로그 뷰어 (레벨 필터링 지원) |

## 데이터 형식

### MQTT 데이터 토픽

```
{topic_prefix}/{device_id}
```

예: `factory/gateway-001/dev1`

### MQTT 데이터 페이로드

```json
{
  "gateway": "공장 1호 게이트웨이",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "온도1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "압력1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### 상태 토픽

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "연결 성공",
  "timestamp": 1719123456789
}
```

- status 값: `online` (정상 수집), `offline` (연결 끊김), `error` (이상)
- quality 값: `good` (정상), `bad` (읽기 실패), `uncertain` (데이터 의심)

## 포인트 데이터 유형

| 유형 | 설명 | 바이트 |
|------|------|-------|
| bool | 부울 | 1 bit |
| int16 | 16비트 부호 있는 정수 | 2 |
| uint16 | 16비트 부호 없는 정수 | 2 |
| int32 | 32비트 부호 있는 정수 | 4 |
| uint32 | 32비트 부호 없는 정수 | 4 |
| float | 32비트 부동소수점 | 4 |
| double | 64비트 부동소수점 | 8 |

> 실제 값 = 원시 값 × 배율 + 오프셋. 배율과 오프셋은 포인트 설정에서 지정합니다.

## 설정 파일

모든 설정은 EXE와 동일한 디렉토리의 `config.json`에 저장되며, 변경 시 자동으로 `config.json.bak`에 백업됩니다.

```json
{
  "gateway_name": "공장 1호 게이트웨이",
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
        {"name": "온도1", "address": "DB1.DBD0", "type": "float", "rate": 1.0, "offset": 0.0, "unit": "℃"}
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

- `collect_interval`: 수집 간격 (밀리초), 1000 = 1초마다
- `reconnect.max_retries`: 0 = 무제한 재시도
- 재시도 간격: 지수 백오프, 1초 → 2초 → 4초 → 8초 → 16초 → 32초 → 60초 (상한)

## 프로토콜 주소 형식

### Modbus

| 주소 범위 | 영역 | 예 |
|----------|------|-----|
| 40001-49999 | 유지 레지스터 | `40001` |
| 30001-39999 | 입력 레지스터 | `30001` |
| 10001-19999 | 이산 입력 | `10001` |
| 00001-09999 | 코일 | `00001` |

### Siemens S7

| 형식 | 설명 | 예 |
|------|------|-----|
| DBx.DBDy | DB 블록 더블워드 (32비트) | `DB1.DBD0` |
| DBx.DBXy.z | DB 블록 비트 | `DB1.DBX8.0` |
| DBx.DBWy | DB 블록 워드 (16비트) | `DB1.DBW0` |
| Mx.y | 메모리 비트 | `M0.0` |
| Ix.y | 입력 비트 | `I0.0` |
| Qx.y | 출력 비트 | `Q0.0` |

> S7-1200/1500: rack=0, slot=1; S7-300/400: rack=0, slot=2

### Mitsubishi MC

| 형식 | 설명 | 예 |
|------|------|-----|
| Dxxxx | 데이터 레지스터 | `D100` |
| Mxxxx | 내부 릴레이 | `M100` |
| Xx | 입력 릴레이 | `X0` |
| Yx | 출력 릴레이 | `Y0` |
| Wxxxx | 링크 레지스터 | `W100` |

## Excel 포인트 테이블 형식

| 포인트명 | 주소 | 데이터 유형 | 배율 | 오프셋 | 단위 |
|---------|------|-----------|------|------|------|
| 온도1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| 압력1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| 운전상태 | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- 첫 번째 행은 헤더 (고정 형식), 두 번째 행부터 포인트 데이터
- `.xlsx` 및 `.xls` 형식 지원
- 디바이스 설정 페이지에서 템플릿 다운로드 가능

## 소스에서 실행

```bash
# 1. 가상 환경 생성 (권장)
python -m venv venv
venv\Scripts\activate

# 2. Python 의존성 설치
pip install -r requirements.txt

# 3. 프론트엔드 빌드
cd frontend
npm install
npm run build
cd ..

# 4. 백엔드 시작
cd backend
python main.py
```

브라우저에서 `http://localhost:8000`을 엽니다.

## EXE 빌드

```bash
# 프론트엔드가 빌드되었는지 확인
cd frontend && npm run build && cd ..

# 빌드 스크립트 실행
build.bat
```

출력: `dist/FactoryLink.exe` (약 25MB)

## Docker 배포

EXE를 사용하지 않으려면 Docker로 실행할 수 있습니다 (서버, 산업용 PC, Raspberry Pi 배포에 적합).

### 빠른 시작

```bash
# 이미지 풀
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# 설정 및 로그 디렉토리 생성
mkdir -p /opt/factorylink/{logs,config}

# 컨테이너 실행
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### 매개변수 설명

| 매개변수 | 설명 |
|---------|------|
| `-p 8000:8000` | Web 설정 페이지 포트 매핑 |
| `-v /opt/factorylink/config:/app/config` | 설정 디렉토리 마운트 (config.json 저장 위치) |
| `-v /opt/factorylink/logs:/app/logs` | 로그 디렉토리 마운트 |
| `--restart always` | 컨테이너 비정상 종료 시 자동 재시작 |

### 최초 사용

1. 컨테이너 시작 후, 브라우저에서 `http://서버IP:8000` 열기
2. PLC 디바이스 및 MQTT 설정
3. "수집 시작" 클릭

> 참고: Docker 버전은 시스템 트레이 아이콘과 부팅 시 자동 시작 기능을 **지원하지 않습니다** (Windows 전용 기능).

### docker-compose 사용

`docker-compose.yml` 생성:

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

시작:

```bash
docker-compose up -d
```

## 기술 스택

- **백엔드**: Python 3.11+ / FastAPI / WebSocket / uvicorn
- **프론트엔드**: Vue 3 / Vite / Element Plus / xlsx
- **프로토콜 라이브러리**: pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**: paho-mqtt
- **패키징**: PyInstaller 6.x (`--onefile --windowed`)
- **시스템 트레이**: pystray + Pillow

## 프로젝트 구조

```
FactoryLink/
├── backend/
│   ├── main.py              # FastAPI 진입점 (WebSocket, 트레이, 포트 감지)
│   ├── config.py            # 설정 관리 (읽기/쓰기, 백업, 스레드 안전)
│   ├── logger.py            # 로그 관리 (10MB 순환 × 5, API 읽기)
│   ├── schemas.py           # Pydantic 데이터 모델
│   ├── collector/
│   │   ├── base.py          # 수집기 기본 클래스 (지수 백오프 재연결, 백그라운드 재연결 스레드)
│   │   ├── modbus.py        # Modbus TCP/RTU (pymodbus)
│   │   ├── s7.py            # Siemens S7 (python-snap7 3.0)
│   │   └── mitsubishi.py    # Mitsubishi MC (pymcprotocol)
│   └── forwarder/
│       └── mqtt.py          # MQTT 전달 (paho-mqtt)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 레이아웃 프레임워크 (내비게이션, 로고, 작성자 정보)
│   │   ├── router.js        # 라우트 설정
│   │   └── views/
│   │       ├── Home.vue          # 홈 페이지 (디바이스 카드, 실시간 데이터, WebSocket)
│   │       ├── DeviceConfig.vue  # 디바이스 설정 (CRUD, 포인트 관리, Excel 가져오기)
│   │       └── Settings.vue      # 시스템 설정 (MQTT, 수집, 재연결, 자동 시작, 로그)
│   └── dist/                # 컴파일된 정적 파일
├── build.bat                # PyInstaller 빌드 스크립트
├── requirements.txt         # Python 의존성 목록
├── Dockerfile               # Docker 이미지
└── README.md                # 이 파일
```

## 자주 묻는 질문

**Q: EXE를 더블클릭해도 아무 반응이 없나요?**

A: 우측 하단 시스템 트레이에 게이트웨이 아이콘이 있는지 확인하세요. 포트가 사용 중이면 자동으로 포트가 전환됩니다. 트레이 아이콘을 우클릭하여 "설정 페이지 열기"를 선택하세요.

**Q: PLC에 연결할 수 없나요?**

A: 먼저 디바이스 설정 페이지에서 "연결 테스트" 버튼을 클릭하여 IP, 포트, 랙/슬롯 번호가 올바른지 확인하세요. Siemens S7-1200/1500은 rack=0, slot=1, S7-300/400은 rack=0, slot=2입니다.

**Q: MQTT에서 데이터를 받을 수 없나요?**

A: MQTT 서버 주소와 포트가 올바른지, MQTT가 활성화되어 있는지 확인하세요. 시스템 설정 페이지의 로그에서 연결 오류를 확인하세요.

**Q: 포인트를 일괄 가져오려면 어떻게 하나요?**

A: 디바이스 설정 페이지에서 Excel 템플릿을 다운로드하고, 형식에 맞게 작성한 후 가져오세요. 헤더는 고정: 포인트명, 주소, 데이터 유형, 배율, 오프셋, 단위.

**Q: Modbus RTU 시리얼 포트는 어떻게 설정하나요?**

A: 포트 이름을 직접 입력하세요 (예: `COM3`, `COM4`). 기본 보레이트는 9600, 패리티는 None (N)입니다.

**Q: 수집 간격은 얼마가 적당한가요?**

A: 기본값은 1000ms (1초)입니다. 빠른 PLC는 500ms, 느린 디바이스는 2000ms 이상을 권장합니다. 너무 짧으면 읽기 타임아웃이 발생할 수 있습니다.

---

현장 엔지니어의 90%는 클라우드 네이티브나 Docker가 필요하지 않습니다. 그들이 원하는 것은 단순하고 사용하기 쉬우며 문제를 해결할 수 있는 도구뿐입니다.

---

## 라이선스

본 프로젝트는 **Mozilla Public License 2.0 (MPL-2.0)** 하에 오픈소스로 공개됩니다.

## 작성자

**탄처(Tan Ce)** — 독립 개발자 | 산업 IoT 탐험가

- 📝 블로그: [https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 이메일: huawei_network@foxmail.com
- 💬 WeChat 공식 계정: **IT Online**

![WeChat QR 코드](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © Tan Ce
