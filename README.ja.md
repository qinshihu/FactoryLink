# 産業用データ収集ゲートウェイ v1.0.0

[![Docker Build](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/docker-build.yml)
[![Release Build](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml/badge.svg)](https://github.com/qinshihu/FactoryLink/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](./LICENSE)

[中文](./README.md) | [English](./README.en.md) | [한국어](./README.ko.md) | [Deutsch](./README.de.md) | [Français](./README.fr.md) | [Español](./README.es.md) | [Русский](./README.ru.md) | [Português](./README.pt.md)

## これは何？

**単一EXE、ダブルクリックで実行、依存関係ゼロ、完全オープンソース＆無料**の産業用デバイスデータ収集ゲートウェイです。

製造業の現場エンジニア、工場IT担当者、小規模システムインテグレーター向けに設計されています。

## なぜ作ったのか？

- 某社の収集ゲートウェイは1台1万元（約20万円）もするので、無料のものを作りました
- 他のオープンソースプロジェクトはDockerが必要で、現場のエンジニアには使えません
- 海外のプロジェクトには中国語のドキュメントがなく、問題が起きても解決できません

## 使い方

1. [`FactoryLink.exe`をダウンロード](https://github.com/qinshihu/FactoryLink/releases/latest)

2. ダブルクリックで実行（右下にトレイアイコンが表示されます）

![トレイアイコン](images/1(2).png)

3. ブラウザが自動的に設定ページを開きます（デフォルト `http://localhost:8000`）

![設定ページ](images/1(1).png)

4. PLCのIP、ポイントテーブル、MQTTアドレスを設定します

![デバイス設定](images/1(4).png)

5. 「収集開始」をクリックすれば完了です！

> トレイアイコンを右クリックすると：設定ページを開く、収集の開始/停止、プログラムの終了ができます。
> 
> Dockerでのデプロイも可能です：[Dockerデプロイガイド](#dockerデプロイ)

## 対応プロトコル

| プロトコル | 対応機種 | ライブラリ |
|-----------|---------|----------|
| Modbus TCP | すべての標準Modbus TCPデバイス | pymodbus 3.x |
| Modbus RTU | すべての標準Modbus RTUデバイス（シリアル） | pymodbus 3.x |
| Siemens S7 | S7-1200 / S7-1500 / S7-300 / S7-400 | python-snap7 3.0（純粋Python） |
| Mitsubishi MC | FX5U / Qシリーズ / Lシリーズ | pymcprotocol |

## 主な機能

- **単一EXE**：ダブルクリックで実行、ランタイム環境不要
- **Web設定画面**：ブラウザで設定可能、コマンドライン知識不要
- **リアルタイムデータ表示**：WebSocketプッシュ、データがリアルタイム更新
- **MQTT転送**：収集データを自動的にMQTTサーバーに転送
- **Excelインポート**：Excelからポイント設定を一括インポート（プレビュー確認ダイアログ付き）
- **AI設定アシスタント**：自然言語でデバイスを説明すると、AIが自動的に設定を生成（OpenAI / Qwen / DeepSeek対応、SSEストリーミング + 編集可能プレビュー）
- **デバイス接続テスト**：ワンクリックでPLCの接続性をテスト
- **自動再接続**：ネットワーク切断時に指数バックオフで自動再接続
- **起動時自動実行**：ワンクリックでWindows起動時に自動起動
- **システムトレイ**：バックグラウンド実行、トレイアイコン右クリックで操作
- **ログビューア**：Web画面で収集ログを表示、レベルフィルタリング対応
- **ホットリロード**：設定変更後「適用」をクリックで自動的にコレクター再起動
- **自動バックアップ**：保存時に自動で`config.json.bak`を生成
- **ポート競合処理**：8000が使用中の場合、自動的に8001、8002...に切り替え

## 画面説明

| ページ | 機能 |
|------|------|
| **ホーム** | デバイスカード一覧、リアルタイムデータ表示、収集開始/停止ボタン、デバイスオンライン状態、MQTT接続状態 |
| **デバイス設定** | デバイスの追加/編集/削除、プロトコル別設定項目、ポイントテーブルCRUD、Excelインポート（プレビュー確認）/テンプレートダウンロード、接続テスト、**AI設定アシスタント**（自然言語でデバイス設定を生成） |
| **システム設定** | MQTT設定、収集間隔、再接続戦略、起動時自動実行、**AI設定**（API URL/Key/モデル）、ログ表示（レベルフィルタリング対応） |

## データ形式

### MQTTデータトピック

```
{topic_prefix}/{device_id}
```

例：`factory/gateway-001/dev1`

### MQTTデータペイロード

```json
{
  "gateway": "工場1号ゲートウェイ",
  "device_id": "dev1",
  "device_name": "Siemens S7-1200",
  "timestamp": 1719123456789,
  "values": {
    "温度1": {"value": 25.5, "unit": "℃", "quality": "good"},
    "圧力1": {"value": 1.2, "unit": "MPa", "quality": "good"}
  }
}
```

### ステータストピック

```
{topic_prefix}/{device_id}/status
```

```json
{
  "device_id": "dev1",
  "status": "online",
  "message": "接続成功",
  "timestamp": 1719123456789
}
```

- status値：`online`（正常収集）、`offline`（切断）、`error`（異常）
- quality値：`good`（正常）、`bad`（読み取り失敗）、`uncertain`（データ不確実）

## ポイントデータ型

| 型 | 説明 | バイト数 |
|----|------|---------|
| bool | ブール値 | 1 bit |
| int16 | 16ビット符号付き整数 | 2 |
| uint16 | 16ビット符号なし整数 | 2 |
| int32 | 32ビット符号付き整数 | 4 |
| uint32 | 32ビット符号なし整数 | 4 |
| float | 32ビット浮動小数点 | 4 |
| double | 64ビット浮動小数点 | 8 |

> 実際の値 = 生の値 × 倍率 + オフセット。倍率とオフセットはポイント設定で指定します。

## 設定ファイル

すべての設定はEXEと同じディレクトリの`config.json`に保存され、変更時に自動的に`config.json.bak`にバックアップされます。

```json
{
  "gateway_name": "工場1号ゲートウェイ",
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
  },
  "ai": {
    "enabled": false,
    "api_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo"
  }
}
```

- `collect_interval`：収集間隔（ミリ秒）、1000 = 1秒ごと
- `reconnect.max_retries`：0 = 無制限リトライ
- リトライ間隔：指数バックオフ、1秒 → 2秒 → 4秒 → 8秒 → 16秒 → 32秒 → 60秒（上限）

## プロトコルアドレス形式

### Modbus

| アドレス範囲 | 領域 | 例 |
|-------------|------|-----|
| 40001-49999 | 保持レジスタ | `40001` |
| 30001-39999 | 入力レジスタ | `30001` |
| 10001-19999 | ディスクリート入力 | `10001` |
| 00001-09999 | コイル | `00001` |

### Siemens S7

| 形式 | 説明 | 例 |
|------|------|-----|
| DBx.DBDy | DBブロックダブルワード（32ビット） | `DB1.DBD0` |
| DBx.DBXy.z | DBブロックビット | `DB1.DBX8.0` |
| DBx.DBWy | DBブロックワード（16ビット） | `DB1.DBW0` |
| Mx.y | メモリビット | `M0.0` |
| Ix.y | 入力ビット | `I0.0` |
| Qx.y | 出力ビット | `Q0.0` |

> S7-1200/1500：rack=0, slot=1；S7-300/400：rack=0, slot=2

### Mitsubishi MC

| 形式 | 説明 | 例 |
|------|------|-----|
| Dxxxx | データレジスタ | `D100` |
| Mxxxx | 内部リレー | `M100` |
| Xx | 入力リレー | `X0` |
| Yx | 出力リレー | `Y0` |
| Wxxxx | リンクレジスタ | `W100` |

## Excelポイントテーブル形式

| ポイント名 | アドレス | データ型 | 倍率 | オフセット | 単位 |
|-----------|---------|---------|------|----------|------|
| 温度1 | DB1.DBD0 | float | 1.0 | 0 | ℃ |
| 圧力1 | DB1.DBD4 | float | 1.0 | 0 | MPa |
| 運転状態 | DB1.DBX8.0 | bool | 1.0 | 0 | - |

- 1行目はヘッダー（固定形式）、2行目以降がポイントデータ
- `.xlsx`および`.xls`形式に対応
- デバイス設定ページでテンプレートをダウンロード可能

## ソースから実行

```bash
# 1. 仮想環境を作成（推奨）
python -m venv venv
venv\Scripts\activate

# 2. Python依存関係をインストール
pip install -r requirements.txt

# 3. フロントエンドをビルド
cd frontend
npm install
npm run build
cd ..

# 4. バックエンドを起動
cd backend
python main.py
```

ブラウザで`http://localhost:8000`を開きます。

## EXEのビルド

```bash
# フロントエンドがビルドされていることを確認
cd frontend && npm run build && cd ..

# ビルドスクリプトを実行
build.bat
```

出力：`dist/FactoryLink.exe`（約25MB）

## Dockerデプロイ

EXEを使いたくない場合は、Dockerで実行することもできます（サーバー、産業用PC、Raspberry Piでのデプロイに適しています）。

### クイックスタート

```bash
# イメージをプル
docker pull registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest

# 設定とログ用のディレクトリを作成
mkdir -p /opt/factorylink/{logs,config}

# コンテナを実行
docker run -d \
  --name factorylink \
  --restart always \
  -p 8000:8000 \
  -v /opt/factorylink/config:/app/config \
  -v /opt/factorylink/logs:/app/logs \
  registry.cn-hangzhou.aliyuncs.com/huluwa666/tsq-images-hub:factorylink-latest
```

### パラメータ説明

| パラメータ | 説明 |
|-----------|------|
| `-p 8000:8000` | Web設定ページのポートをマッピング |
| `-v /opt/factorylink/config:/app/config` | 設定ディレクトリをマウント（config.jsonはここに保存） |
| `-v /opt/factorylink/logs:/app/logs` | ログディレクトリをマウント |
| `--restart always` | コンテナ異常終了時に自動再起動 |

### 初回使用

1. コンテナ起動後、ブラウザで`http://サーバーのIP:8000`を開く
2. PLCデバイスとMQTTを設定
3. 「収集開始」をクリック

> 注意：Docker版はシステムトレイアイコンと起動時自動実行機能に**対応していません**（Windows専用機能）。

### docker-composeの使用

`docker-compose.yml`を作成：

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

起動：

```bash
docker-compose up -d
```

## 技術スタック

- **バックエンド**：Python 3.11+ / FastAPI / WebSocket / uvicorn
- **フロントエンド**：Vue 3 / Vite / Element Plus / xlsx
- **プロトコルライブラリ**：pymodbus 3.x / python-snap7 3.0 / pymcprotocol
- **MQTT**：paho-mqtt
- **パッケージング**：PyInstaller 6.x（`--onefile --windowed`）
- **システムトレイ**：pystray + Pillow

## プロジェクト構造

```
FactoryLink/
├── backend/
│   ├── main.py              # FastAPIエントリポイント（WebSocket、トレイ、ポート検出）
│   ├── config.py            # 設定管理（読み書き、バックアップ、スレッドセーフ）
│   ├── logger.py            # ログ管理（10MBローテーション×5、API読み取り）
│   ├── schemas.py           # Pydanticデータモデル
│   ├── collector/
│   │   ├── base.py          # コレクター基底クラス（指数バックオフ再接続、バックグラウンド再接続スレッド）
│   │   ├── modbus.py        # Modbus TCP/RTU（pymodbus）
│   │   ├── s7.py            # Siemens S7（python-snap7 3.0）
│   │   └── mitsubishi.py    # Mitsubishi MC（pymcprotocol）
│   └── forwarder/
│       └── mqtt.py          # MQTT転送（paho-mqtt）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # レイアウトフレームワーク（ナビゲーション、ロゴ、作者情報）
│   │   ├── router.js        # ルート設定
│   │   └── views/
│   │       ├── Home.vue          # ホームページ（デバイスカード、リアルタイムデータ、WebSocket）
│   │       ├── DeviceConfig.vue  # デバイス設定（CRUD、ポイント管理、Excelインポート）
│   │       └── Settings.vue      # システム設定（MQTT、収集、再接続、自動起動、ログ）
│   └── dist/                # コンパイル済み静的ファイル
├── build.bat                # PyInstallerビルドスクリプト
├── requirements.txt         # Python依存関係リスト
├── Dockerfile               # Dockerイメージ
└── README.md                # このファイル
```

## よくある質問

**Q: EXEをダブルクリックしても何も起きません？**

A: 右下のシステムトレイにゲートウェイアイコンがあるか確認してください。ポートが使用中の場合は自動的にポートが切り替わります。トレイアイコンを右クリックして「設定ページを開く」を選択してください。

**Q: PLCに接続できません？**

A: まずデバイス設定ページで「接続テスト」ボタンをクリックし、IP、ポート、ラック/スロット番号が正しいか確認してください。Siemens S7-1200/1500はrack=0, slot=1、S7-300/400はrack=0, slot=2です。

**Q: MQTTでデータを受信できません？**

A: MQTTサーバーのアドレスとポートが正しいか、MQTTが有効になっているか確認してください。システム設定ページのログで接続エラーを確認してください。

**Q: ポイントを一括インポートするには？**

A: デバイス設定ページでExcelテンプレートをダウンロードし、フォーマットに従って入力してインポートしてください。ヘッダーは固定：ポイント名、アドレス、データ型、倍率、オフセット、単位。

**Q: Modbus RTUのシリアルポートはどう設定しますか？**

A: ポート名を直接入力してください（例：`COM3`、`COM4`）。デフォルトのボーレートは9600、パリティはNone（N）です。

**Q: 収集間隔はどのくらいが適切ですか？**

A: デフォルトは1000ms（1秒）です。高速なPLCなら500ms、遅いデバイスなら2000ms以上を推奨します。短すぎると読み取りタイムアウトが発生する可能性があります。

---

現場エンジニアの90%はクラウドネイティブもDockerも必要としていません。彼らが求めているのは、シンプルで使いやすく、問題を解決できるツールだけです。

---

## ライセンス

本プロジェクトは**Mozilla Public License 2.0 (MPL-2.0)**の下でオープンソース公開されています。

## 作者

**譚策（タン・ツェ）** — 独立系開発者 | 産業用IoTエクスプローラー

- 📝 ブログ：[https://www.zjzwfw.cloud/](https://www.zjzwfw.cloud/)
- 📧 メール：huawei_network@foxmail.com
- 💬 WeChat公式アカウント：**IT Online**

![WeChat QRコード](images/公众号背面.png)

---

[MPL-2.0](./LICENSE) © 譚策
