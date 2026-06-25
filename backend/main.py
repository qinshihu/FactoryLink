"""
FastAPI主入口 - Web服务、WebSocket、托盘图标、采集调度
"""
import sys
import os
import json
import time
import asyncio
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import uvicorn

# 将backend目录加入路径
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import config_manager
from logger import gateway_logger, logger
from schemas import (
    ApiResponse, DeviceConfig, MqttConfig, GatewayConfig,
    TestConnectionRequest, TestConnectionResponse, LogQuery,
    AIParseRequest, AIConfig
)
from collector.base import BaseCollector
from collector.modbus import ModbusCollector
from collector.s7 import S7Collector
from collector.mitsubishi import MitsubishiCollector
from forwarder.mqtt import mqtt_forwarder
from ai_service import ai_service


# ==================== FastAPI应用 ====================
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global _main_event_loop
    _main_event_loop = asyncio.get_running_loop()
    logger.info("主事件循环已注册")
    yield
    # 清理资源
    stop_collecting()
    logger.info("应用已关闭")


app = FastAPI(title="工业数据采集网关", version="1.0.0", lifespan=lifespan)

# 采集器管理
collectors: Dict[str, BaseCollector] = {}
collector_lock = threading.Lock()
collect_thread: Optional[threading.Thread] = None
collect_running = False

# WebSocket连接管理
ws_connections: list = []
ws_lock = threading.Lock()
_main_event_loop = None  # 主事件循环引用，用于跨线程调度


def get_frontend_dir() -> Path:
    """获取前端静态文件目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后
        base = Path(sys._MEIPASS)
    else:
        base = backend_dir.parent
    return base / "frontend" / "dist"


# ==================== 采集器工厂 ====================
def create_collector(device_config: dict) -> Optional[BaseCollector]:
    """根据设备配置创建对应的采集器"""
    protocol = device_config.get("protocol", "")
    reconnect_config = config_manager.get_reconnect_config()

    collector_map = {
        "modbus_tcp": ModbusCollector,
        "modbus_rtu": ModbusCollector,
        "s7": S7Collector,
        "mitsubishi": MitsubishiCollector,
    }

    collector_class = collector_map.get(protocol)
    if not collector_class:
        logger.error(f"不支持的协议: {protocol}")
        return None

    return collector_class(device_config, reconnect_config)


def on_device_status_change(device_id: str, status: str, message: str):
    """设备状态变化回调"""
    status_data = {
        "type": "status",
        "device_id": device_id,
        "status": status,
        "message": message,
        "timestamp": int(time.time() * 1000)
    }
    # 使用 run_coroutine_threadsafe 调度到主事件循环
    if _main_event_loop and _main_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_ws(status_data), _main_event_loop)

    # 转发到MQTT
    mqtt_forwarder.publish_status(device_id, status, message)


async def broadcast_ws(data: dict):
    """向所有WebSocket连接广播数据"""
    dead_connections = []
    with ws_lock:
        for ws in ws_connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead_connections.append(ws)
        for ws in dead_connections:
            if ws in ws_connections:
                ws_connections.remove(ws)


# ==================== 采集线程 ====================
def collect_loop():
    """采集主循环"""
    global collect_running
    logger.info("采集线程启动")

    while collect_running:
        interval = config_manager.get_collect_interval() / 1000.0
        gateway_name = config_manager.get("gateway_name", "")

        with collector_lock:
            for device_id, collector in list(collectors.items()):
                if not collector.is_connected:
                    continue
                try:
                    data = collector.read()
                    data["gateway"] = gateway_name

                    # 推送到WebSocket（跨线程安全调度）
                    ws_data = {"type": "data", **data}
                    if _main_event_loop and _main_event_loop.is_running():
                        asyncio.run_coroutine_threadsafe(broadcast_ws(ws_data), _main_event_loop)

                    # 转发到MQTT
                    mqtt_forwarder.publish_data(data)
                except Exception as e:
                    logger.error(f"采集设备 {device_id} 失败: {e}")

        time.sleep(interval)

    logger.info("采集线程停止")


def start_collecting():
    """启动采集"""
    global collect_running, collect_thread

    if collect_running:
        return

    # 根据配置创建采集器
    devices = config_manager.get_devices()
    with collector_lock:
        collectors.clear()
        for device in devices:
            if not device.get("enabled", True):
                continue
            collector = create_collector(device)
            if collector:
                collector.on_status_change(on_device_status_change)
                collectors[device["id"]] = collector

    # 连接所有设备
    for device_id, collector in collectors.items():
        threading.Thread(target=collector.connect, daemon=True).start()

    # 启动采集线程
    collect_running = True
    collect_thread = threading.Thread(target=collect_loop, daemon=True)
    collect_thread.start()
    logger.info(f"采集已启动，共 {len(collectors)} 个设备")


def stop_collecting():
    """停止采集"""
    global collect_running

    collect_running = False
    with collector_lock:
        for collector in collectors.values():
            collector.disconnect()
        collectors.clear()

    # 断开MQTT
    mqtt_forwarder.disconnect()
    logger.info("采集已停止")


def restart_collecting():
    """重启采集（配置热加载）"""
    stop_collecting()
    # 重新连接MQTT
    mqtt_config = config_manager.get_mqtt_config()
    mqtt_forwarder.configure(mqtt_config)
    mqtt_forwarder.connect()
    start_collecting()


# ==================== 系统托盘 ====================
def create_tray_icon(port: int):
    """创建系统托盘图标"""
    try:
        import pystray
        from PIL import Image, ImageDraw

        # 创建简单的托盘图标（16x16绿色方块）
        image = Image.new('RGB', (64, 64), color='green')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        draw.rectangle([24, 24, 40, 40], fill='green')

        def open_browser(icon, item):
            webbrowser.open(f"http://localhost:{port}")

        def start_collect(icon, item):
            start_collecting()

        def stop_collect(icon, item):
            stop_collecting()

        def quit_app(icon, item):
            stop_collecting()
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("打开配置页面", open_browser, default=True),
            pystray.MenuItem("启动采集", start_collect),
            pystray.MenuItem("停止采集", stop_collect),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", quit_app),
        )

        icon = pystray.Icon("gateway", image, f"工业数据采集网关 (端口:{port})", menu)

        # 在新线程中运行托盘图标
        threading.Thread(target=icon.run, daemon=True).start()
        logger.info("系统托盘图标已创建")
        return icon
    except ImportError:
        logger.warning("pystray或Pillow未安装，跳过托盘图标")
        return None
    except Exception as e:
        logger.warning(f"创建托盘图标失败: {e}")
        return None


# ==================== 端口检测 ====================
def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """查找可用端口"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port


# ==================== API路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return ApiResponse(success=True, message="网关运行中")


# ---- 配置管理 ----

@app.get("/api/config")
async def get_config():
    """获取完整配置"""
    return ApiResponse(data=config_manager.get_all())


@app.put("/api/config")
async def update_config(config: GatewayConfig):
    """更新完整配置并保存"""
    config_manager.update(config.model_dump())
    config_manager.save()
    return ApiResponse(success=True, message="配置已保存")


@app.post("/api/config/reload")
async def reload_config():
    """重新加载配置（从文件读取）"""
    config_manager.load()
    return ApiResponse(success=True, message="配置已重新加载")


@app.post("/api/config/apply")
async def apply_config():
    """应用配置（保存并重启采集）"""
    config_manager.save()
    threading.Thread(target=restart_collecting, daemon=True).start()
    return ApiResponse(success=True, message="配置已应用，采集器正在重启")


# ---- 设备管理 ----

@app.get("/api/devices")
async def get_devices():
    """获取设备列表"""
    return ApiResponse(data=config_manager.get_devices())


@app.post("/api/devices")
async def add_device(device: DeviceConfig):
    """添加设备"""
    device_dict = device.model_dump()
    config_manager.add_device(device_dict)
    config_manager.save()
    return ApiResponse(success=True, message="设备已添加", data=device_dict)


@app.put("/api/devices/{device_id}")
async def update_device(device_id: str, device: DeviceConfig):
    """更新设备"""
    device_dict = device.model_dump()
    device_dict["id"] = device_id
    if config_manager.update_device(device_id, device_dict):
        config_manager.save()
        return ApiResponse(success=True, message="设备已更新")
    return ApiResponse(success=False, message="设备不存在")


@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    """删除设备"""
    if config_manager.remove_device(device_id):
        config_manager.save()
        return ApiResponse(success=True, message="设备已删除")
    return ApiResponse(success=False, message="设备不存在")


@app.post("/api/devices/test")
async def test_connection(req: TestConnectionRequest):
    """测试设备连接"""
    device_dict = req.device.model_dump()
    reconnect_config = config_manager.get_reconnect_config()
    collector = create_collector(device_dict)
    if not collector:
        return TestConnectionResponse(
            success=False,
            message=f"不支持的协议: {device_dict.get('protocol')}"
        )

    success, message, elapsed = collector.test_connection()
    return TestConnectionResponse(success=success, message=message, elapsed_ms=elapsed)


# ---- 采集控制 ----

@app.post("/api/collect/start")
async def api_start_collect():
    """启动采集"""
    # 先连接MQTT
    mqtt_config = config_manager.get_mqtt_config()
    mqtt_forwarder.configure(mqtt_config)
    mqtt_forwarder.connect()

    threading.Thread(target=start_collecting, daemon=True).start()
    return ApiResponse(success=True, message="采集已启动")


@app.post("/api/collect/stop")
async def api_stop_collect():
    """停止采集"""
    threading.Thread(target=stop_collecting, daemon=True).start()
    return ApiResponse(success=True, message="采集已停止")


@app.get("/api/collect/status")
async def get_collect_status():
    """获取采集状态"""
    with collector_lock:
        device_statuses = []
        for device_id, collector in collectors.items():
            device_statuses.append({
                "device_id": device_id,
                "device_name": collector.device_name,
                "connected": collector.is_connected
            })
    return ApiResponse(data={
        "running": collect_running,
        "devices": device_statuses,
        "mqtt_connected": mqtt_forwarder.is_connected
    })


# ---- MQTT配置 ----

@app.get("/api/mqtt")
async def get_mqtt_config():
    """获取MQTT配置"""
    return ApiResponse(data=config_manager.get_mqtt_config())


@app.put("/api/mqtt")
async def update_mqtt_config(config: MqttConfig):
    """更新MQTT配置"""
    config_manager.set("mqtt", config.model_dump())
    config_manager.save()
    return ApiResponse(success=True, message="MQTT配置已保存")


# ---- 日志 ----

@app.get("/api/logs")
async def get_logs(level: Optional[str] = None, lines: int = 200):
    """获取日志"""
    logs = gateway_logger.read_logs(level=level, lines=lines)
    return ApiResponse(data=logs)


@app.post("/api/logs/level")
async def set_log_level(level: str = "INFO"):
    """设置日志级别"""
    gateway_logger.set_level(level)
    return ApiResponse(success=True, message=f"日志级别已设置为 {level}")


# ---- Excel导入 ----

@app.post("/api/devices/import-excel")
async def import_excel(file: UploadFile = File(...)):
    """导入Excel点位表，解析并返回点位列表"""
    import io
    import openpyxl

    if not file.filename:
        return ApiResponse(success=False, message="未选择文件")

    # 检查文件类型
    ext = Path(file.filename).suffix.lower()
    if ext not in ('.xlsx', '.xls'):
        return ApiResponse(success=False, message="仅支持 .xlsx 或 .xls 格式的Excel文件")

    try:
        contents = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(contents), read_only=True)
        ws = wb.active

        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            wb.close()
            return ApiResponse(success=False, message="Excel文件至少需要包含表头和一行数据")

        # 第一行为表头
        header = [str(h).strip() if h else '' for h in rows[0]]
        points = []

        # 映射中文/英文表头到字段名
        field_map = {
            '点位名称': 'name', '名称': 'name', 'name': 'name',
            '地址': 'address', 'address': 'address',
            '数据类型': 'type', '类型': 'type', 'type': 'type',
            '倍率': 'rate', 'rate': 'rate',
            '偏移': 'offset', '偏移量': 'offset', 'offset': 'offset',
            '单位': 'unit', 'unit': 'unit',
        }

        # 找到各字段对应的列索引
        col_index = {}
        for i, h in enumerate(header):
            key = field_map.get(h.lower() if h else '')
            if key:
                col_index[key] = i

        if 'name' not in col_index or 'address' not in col_index:
            wb.close()
            return ApiResponse(success=False, message='Excel表头必须包含"点位名称"和"地址"列')

        valid_types = {'bool', 'int16', 'uint16', 'int32', 'uint32', 'float', 'double'}

        for row in rows[1:]:
            if not row or all(c is None for c in row):
                continue

            name = str(row[col_index['name']]).strip() if col_index.get('name') is not None and len(row) > col_index['name'] and row[col_index['name']] is not None else ''
            address = str(row[col_index['address']]).strip() if col_index.get('address') is not None and len(row) > col_index['address'] and row[col_index['address']] is not None else ''

            if not name or not address:
                continue

            data_type = str(row[col_index['type']]).strip().lower() if col_index.get('type') is not None and len(row) > col_index['type'] and row[col_index['type']] is not None else 'float'
            if data_type not in valid_types:
                data_type = 'float'

            rate = 1.0
            if col_index.get('rate') is not None and len(row) > col_index['rate']:
                try:
                    rate = float(row[col_index['rate']])
                except (ValueError, TypeError):
                    rate = 1.0

            offset = 0.0
            if col_index.get('offset') is not None and len(row) > col_index['offset']:
                try:
                    offset = float(row[col_index['offset']])
                except (ValueError, TypeError):
                    offset = 0.0

            unit = str(row[col_index['unit']]).strip() if col_index.get('unit') is not None and len(row) > col_index['unit'] and row[col_index['unit']] is not None else ''

            points.append({
                "name": name,
                "address": address,
                "type": data_type,
                "rate": rate,
                "offset": offset,
                "unit": unit
            })

        wb.close()

        if not points:
            return ApiResponse(success=False, message="未解析到有效点位数据，请检查Excel格式")

        logger.info(f"Excel导入成功: {file.filename}, 解析到 {len(points)} 个点位")
        return ApiResponse(success=True, message=f"成功导入 {len(points)} 个点位", data={"points": points})

    except openpyxl.utils.exceptions.InvalidFileException:
        return ApiResponse(success=False, message="文件格式无效，请确认是有效的Excel文件")
    except Exception as e:
        logger.error(f"Excel导入失败: {e}")
        return ApiResponse(success=False, message=f"Excel解析失败: {str(e)}")


# ---- AI配置助手 ----

@app.get("/api/ai/config")
async def get_ai_config():
    """获取AI配置"""
    ai_config = config_manager.get("ai", {})
    return ApiResponse(data=ai_config)


@app.put("/api/ai/config")
async def update_ai_config(config: AIConfig):
    """更新AI配置"""
    config_manager.set("ai", config.model_dump())
    config_manager.save()
    return ApiResponse(success=True, message="AI配置已保存")


@app.post("/api/ai/parse")
async def ai_parse_config(req: AIParseRequest):
    """AI解析自然语言为设备配置"""
    # 优先使用请求中的配置，否则使用全局配置
    ai_config = config_manager.get("ai", {})
    api_url = req.api_url or ai_config.get("api_url", "https://api.openai.com/v1")
    api_key = req.api_key or ai_config.get("api_key", "")
    model = req.model or ai_config.get("model", "gpt-3.5-turbo")

    if not api_key:
        return ApiResponse(success=False, message="请先在系统设置中配置AI API Key")

    result = await ai_service.parse_config(req.input, api_url, api_key, model)
    if result["success"]:
        return ApiResponse(success=True, message="解析成功", data=result["config"])
    else:
        return ApiResponse(success=False, message=result["message"])


@app.post("/api/ai/parse-stream")
async def ai_parse_config_stream(req: AIParseRequest):
    """AI解析自然语言为设备配置（SSE流式输出）"""
    ai_config = config_manager.get("ai", {})
    api_url = req.api_url or ai_config.get("api_url", "https://api.openai.com/v1")
    api_key = req.api_key or ai_config.get("api_key", "")
    model = req.model or ai_config.get("model", "gpt-3.5-turbo")

    if not api_key:
        async def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': '请先在系统设置中配置AI API Key'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    async def event_stream():
        async for chunk in ai_service.parse_config_stream(req.input, api_url, api_key, model):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---- 开机自启动 ----

@app.post("/api/system/autostart")
async def set_autostart(enabled: bool = True):
    """设置开机自启动"""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "工业数据采集网关"

        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.executable

        if enabled:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            return ApiResponse(success=True, message="已设置开机自启动")
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return ApiResponse(success=True, message="已取消开机自启动")
    except Exception as e:
        return ApiResponse(success=False, message=f"设置失败: {str(e)}")


@app.get("/api/system/autostart")
async def get_autostart():
    """检查开机自启动状态"""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "工业数据采集网关"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, app_name)
            enabled = True
        except FileNotFoundError:
            enabled = False
        winreg.CloseKey(key)
        return ApiResponse(data={"enabled": enabled})
    except Exception:
        return ApiResponse(data={"enabled": False})


# ---- WebSocket ----

@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket数据推送端点"""
    await websocket.accept()
    with ws_lock:
        ws_connections.append(websocket)
    logger.info(f"WebSocket客户端连接，当前连接数: {len(ws_connections)}")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        with ws_lock:
            if websocket in ws_connections:
                ws_connections.remove(websocket)
        logger.info(f"WebSocket客户端断开，当前连接数: {len(ws_connections)}")


# ==================== 静态文件服务 ====================
frontend_dir = get_frontend_dir()

if frontend_dir.exists() and (frontend_dir / "index.html").exists():
    # 挂载静态资源
    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """服务前端页面（SPA模式）"""
        file_path = frontend_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # SPA fallback
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "前端文件未找到，请先编译前端项目"}
        )
else:
    @app.get("/")
    async def root():
        return {
            "success": True,
            "message": "工业数据采集网关API服务已启动",
            "docs": "/docs",
            "note": "前端文件未找到，请先编译前端项目: cd frontend && npm run build"
        }


# ==================== 启动入口 ====================
def main():
    """主启动函数"""
    print("=" * 50)
    print("  工业数据采集网关 v1.0.0")
    print("=" * 50)

    # 查找可用端口
    port = find_available_port(8000)
    if port != 8000:
        print(f"端口8000已被占用，使用端口: {port}")

    # 创建托盘图标
    tray_icon = create_tray_icon(port)

    # 自动打开浏览器
    def open_browser_delayed():
        time.sleep(1)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser_delayed, daemon=True).start()

    print(f"配置页面: http://localhost:{port}")
    print(f"API文档:   http://localhost:{port}/docs")
    print("右键托盘图标可进行操作")
    print("=" * 50)

    # 启动服务（--windowed模式下sys.stdout为None，禁用uvicorn默认日志配置）
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        log_config=None
    )


if __name__ == "__main__":
    main()
