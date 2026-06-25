"""
配置管理模块 - 读写config.json，支持自动备份
"""
import json
import os
import shutil
import sys
import threading
from pathlib import Path
from typing import Optional

# 默认配置
DEFAULT_CONFIG = {
    "gateway_name": "默认网关",
    "devices": [],
    "mqtt": {
        "host": "",
        "port": 1883,
        "client_id": "gateway-001",
        "topic_prefix": "factory/data",
        "username": "",
        "password": "",
        "qos": 1,
        "enabled": False
    },
    "collect_interval": 1000,
    "reconnect": {
        "max_retries": 0,
        "base_delay": 1,
        "max_delay": 60
    },
    "ai": {
        "enabled": False,
        "api_url": "https://api.openai.com/v1",
        "api_key": "",
        "model": "gpt-3.5-turbo"
    }
}


def get_config_dir() -> Path:
    """获取配置文件所在目录（与EXE同目录）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def get_config_path() -> Path:
    """获取config.json完整路径"""
    return get_config_dir() / "config.json"


class ConfigManager:
    """配置管理器，线程安全"""

    def __init__(self):
        self._lock = threading.Lock()
        self._config: dict = {}
        self._config_path = get_config_path()
        self.load()

    def load(self) -> dict:
        """从文件加载配置，不存在则创建默认配置"""
        with self._lock:
            if self._config_path.exists():
                try:
                    with open(self._config_path, 'r', encoding='utf-8') as f:
                        self._config = json.load(f)
                except (json.JSONDecodeError, IOError):
                    self._config = DEFAULT_CONFIG.copy()
                    self._save_internal()
            else:
                self._config = DEFAULT_CONFIG.copy()
                self._save_internal()
            return self._config

    def _save_internal(self):
        """内部保存方法（不加锁，由调用方加锁）"""
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def save(self):
        """保存配置并自动备份"""
        with self._lock:
            # 先备份旧配置
            bak_path = self._config_path.with_suffix('.json.bak')
            if self._config_path.exists():
                shutil.copy2(self._config_path, bak_path)
            self._save_internal()

    def get_all(self) -> dict:
        """获取全部配置"""
        with self._lock:
            return json.loads(json.dumps(self._config))

    def get(self, key: str, default=None):
        """获取指定配置项"""
        with self._lock:
            return self._config.get(key, default)

    def set(self, key: str, value):
        """设置指定配置项"""
        with self._lock:
            self._config[key] = value

    def update(self, data: dict):
        """批量更新配置"""
        with self._lock:
            self._config.update(data)

    def get_devices(self) -> list:
        """获取设备列表"""
        return self.get("devices", [])

    def get_device(self, device_id: str) -> Optional[dict]:
        """根据ID获取设备配置"""
        devices = self.get_devices()
        for d in devices:
            if d.get("id") == device_id:
                return d
        return None

    def add_device(self, device: dict):
        """添加设备"""
        with self._lock:
            devices = self._config.get("devices", [])
            devices.append(device)
            self._config["devices"] = devices

    def update_device(self, device_id: str, device: dict):
        """更新设备配置"""
        with self._lock:
            devices = self._config.get("devices", [])
            for i, d in enumerate(devices):
                if d.get("id") == device_id:
                    devices[i] = device
                    self._config["devices"] = devices
                    return True
            return False

    def remove_device(self, device_id: str) -> bool:
        """删除设备"""
        with self._lock:
            devices = self._config.get("devices", [])
            new_devices = [d for d in devices if d.get("id") != device_id]
            if len(new_devices) != len(devices):
                self._config["devices"] = new_devices
                return True
            return False

    def get_mqtt_config(self) -> dict:
        """获取MQTT配置"""
        return self.get("mqtt", {})

    def get_collect_interval(self) -> int:
        """获取采集间隔（毫秒）"""
        return self.get("collect_interval", 1000)

    def get_reconnect_config(self) -> dict:
        """获取重连配置"""
        return self.get("reconnect", {"max_retries": 0, "base_delay": 1, "max_delay": 60})


# 全局单例
config_manager = ConfigManager()
