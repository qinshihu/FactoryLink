"""
采集器基类 - 定义统一接口和重连机制
"""
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable
from datetime import datetime

from logger import gateway_logger


class BaseCollector(ABC):
    """采集器基类，所有协议采集器继承此类"""

    def __init__(self, device_config: dict, reconnect_config: dict):
        self.device_config = device_config
        self.device_id = device_config.get("id", "")
        self.device_name = device_config.get("name", "")
        self.points = device_config.get("points", [])
        self.reconnect_config = reconnect_config
        self._connected = False
        self._running = False
        self._reconnecting = False
        self._logger = gateway_logger.get_logger(f"collector.{self.device_id}")
        self._status_callbacks: List[Callable] = []

    def on_status_change(self, callback: Callable):
        """注册状态变化回调"""
        self._status_callbacks.append(callback)

    def _notify_status(self, status: str, message: str = ""):
        """通知状态变化"""
        for cb in self._status_callbacks:
            try:
                cb(self.device_id, status, message)
            except Exception:
                pass

    @abstractmethod
    def _do_connect(self) -> bool:
        """实际连接操作，子类实现"""
        pass

    @abstractmethod
    def _do_disconnect(self):
        """实际断开操作，子类实现"""
        pass

    @abstractmethod
    def _do_read(self, point: dict) -> Optional[dict]:
        """
        读取单个点位，子类实现
        返回: {"name": "xxx", "value": xxx, "unit": "xxx", "quality": "good"}
        失败返回 None
        """
        pass

    def connect(self) -> bool:
        """连接设备，含重试逻辑"""
        max_retries = self.reconnect_config.get("max_retries", 0)
        base_delay = self.reconnect_config.get("base_delay", 1)
        max_delay = self.reconnect_config.get("max_delay", 60)
        retry_count = 0

        while True:
            try:
                self._logger.info(f"正在连接设备 {self.device_name}...")
                if self._do_connect():
                    self._connected = True
                    self._notify_status("online", "连接成功")
                    self._logger.info(f"设备 {self.device_name} 连接成功")
                    return True
            except Exception as e:
                self._logger.warning(f"设备 {self.device_name} 连接失败: {e}")

            # 检查是否超过最大重试次数
            if max_retries > 0 and retry_count >= max_retries:
                self._logger.error(f"设备 {self.device_name} 已达最大重试次数 {max_retries}，放弃连接")
                self._notify_status("error", f"连接失败，已达最大重试次数")
                return False

            # 指数退避
            delay = min(base_delay * (2 ** retry_count), max_delay)
            self._logger.info(f"设备 {self.device_name} {delay}秒后重试 (第{retry_count + 1}次)")
            self._notify_status("offline", f"连接失败，{delay}秒后重试")
            time.sleep(delay)
            retry_count += 1

    def disconnect(self):
        """断开连接"""
        self._reconnecting = False
        try:
            self._do_disconnect()
        except Exception as e:
            self._logger.warning(f"断开连接异常: {e}")
        self._connected = False
        self._notify_status("offline", "已断开")

    def _start_background_reconnect(self):
        """启动后台重连线程（不阻塞采集循环）"""
        if self._reconnecting:
            return
        self._reconnecting = True
        threading.Thread(target=self._background_reconnect, daemon=True).start()

    def _background_reconnect(self):
        """后台重连逻辑"""
        max_retries = self.reconnect_config.get("max_retries", 0)
        base_delay = self.reconnect_config.get("base_delay", 1)
        max_delay = self.reconnect_config.get("max_delay", 60)
        retry_count = 0

        while not self._connected and self._reconnecting:
            try:
                self._logger.info(f"后台重连设备 {self.device_name}...")
                if self._do_connect():
                    self._connected = True
                    self._notify_status("online", "重连成功")
                    self._logger.info(f"设备 {self.device_name} 重连成功")
                    break
            except Exception as e:
                self._logger.warning(f"后台重连失败: {e}")

            if max_retries > 0 and retry_count >= max_retries:
                self._logger.error(f"设备 {self.device_name} 后台重连已达最大次数")
                self._notify_status("error", "重连失败，已达最大重试次数")
                break

            delay = min(base_delay * (2 ** retry_count), max_delay)
            time.sleep(delay)
            retry_count += 1

        self._reconnecting = False

    def read(self) -> Dict:
        """读取所有点位数据（不阻塞，断连时后台重连）"""
        timestamp = int(datetime.now().timestamp() * 1000)

        if not self._connected:
            self._start_background_reconnect()
            return self._build_error_data(timestamp, "设备未连接")

        values = {}
        all_bad = True
        for point in self.points:
            point_name = point.get("name", "")
            unit = point.get("unit", "")
            try:
                result = self._do_read(point)
                if result:
                    values[point_name] = {
                        "value": result.get("value"),
                        "unit": unit,
                        "quality": "good"
                    }
                    all_bad = False
                else:
                    values[point_name] = {
                        "value": None,
                        "unit": unit,
                        "quality": "bad"
                    }
            except Exception as e:
                self._logger.error(f"读取点位 {point_name} 失败: {e}")
                values[point_name] = {
                    "value": None,
                    "unit": unit,
                    "quality": "bad"
                }

        # 所有点位都读取失败，标记为断连并触发后台重连
        if all_bad and len(self.points) > 0:
            self._connected = False
            self._notify_status("offline", "所有点位读取失败")
            self._start_background_reconnect()

        return {
            "gateway": "",
            "device_id": self.device_id,
            "device_name": self.device_name,
            "timestamp": timestamp,
            "values": values
        }

    def _build_error_data(self, timestamp: int, message: str) -> Dict:
        """构建错误数据"""
        values = {}
        for point in self.points:
            values[point.get("name", "")] = {
                "value": None,
                "unit": point.get("unit", ""),
                "quality": "bad"
            }
        return {
            "gateway": "",
            "device_id": self.device_id,
            "device_name": self.device_name,
            "timestamp": timestamp,
            "values": values
        }

    def test_connection(self) -> tuple:
        """测试连接，返回 (成功, 消息, 耗时毫秒)"""
        start = time.time()
        try:
            if self._do_connect():
                elapsed = int((time.time() - start) * 1000)
                self._do_disconnect()
                return True, f"连接成功，耗时 {elapsed}ms", elapsed
            else:
                elapsed = int((time.time() - start) * 1000)
                return False, f"连接失败，耗时 {elapsed}ms", elapsed
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return False, f"连接异常: {str(e)}", elapsed

    @property
    def is_connected(self) -> bool:
        return self._connected
