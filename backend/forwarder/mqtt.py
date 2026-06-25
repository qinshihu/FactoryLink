"""
MQTT数据转发模块
"""
import json
import threading
from typing import Optional

from logger import gateway_logger


class MqttForwarder:
    """MQTT数据转发器"""

    def __init__(self):
        self._client = None
        self._connected = False
        self._config: dict = {}
        self._logger = gateway_logger.get_logger("mqtt")
        self._lock = threading.Lock()

    def configure(self, config: dict):
        """更新MQTT配置"""
        self._config = config

    def connect(self) -> bool:
        """连接MQTT服务器"""
        if not self._config.get("enabled", False):
            self._logger.info("MQTT未启用，跳过连接")
            return False

        host = self._config.get("host", "")
        if not host:
            self._logger.warning("MQTT服务器地址为空")
            return False

        try:
            import paho.mqtt.client as mqtt

            with self._lock:
                if self._client:
                    try:
                        self._client.disconnect()
                    except Exception:
                        pass

                client_id = self._config.get("client_id", "gateway-001")
                self._client = mqtt.Client(client_id=client_id)

                # 设置认证
                username = self._config.get("username", "")
                password = self._config.get("password", "")
                if username:
                    self._client.username_pw_set(username, password)

                port = self._config.get("port", 1883)
                self._client.connect(host, port, keepalive=60)
                self._client.loop_start()
                self._connected = True
                self._logger.info(f"MQTT连接成功: {host}:{port}")
                return True
        except ImportError:
            self._logger.error("paho-mqtt库未安装，请执行: pip install paho-mqtt")
            return False
        except Exception as e:
            self._logger.error(f"MQTT连接失败: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """断开MQTT连接"""
        with self._lock:
            if self._client:
                try:
                    self._client.loop_stop()
                    self._client.disconnect()
                except Exception:
                    pass
                self._client = None
            self._connected = False

    def publish_data(self, data: dict):
        """发布采集数据"""
        with self._lock:
            if not self._connected or not self._client:
                return
            client = self._client
            qos = self._config.get("qos", 1)
            topic_prefix = self._config.get("topic_prefix", "factory/data")

        try:
            device_id = data.get("device_id", "unknown")

            # 数据Topic
            data_topic = f"{topic_prefix}/{device_id}"
            payload = json.dumps(data, ensure_ascii=False)
            client.publish(data_topic, payload, qos=qos)

            # 状态Topic
            status_topic = f"{topic_prefix}/{device_id}/status"
            status_payload = json.dumps({
                "device_id": device_id,
                "status": "online",
                "timestamp": data.get("timestamp", 0)
            })
            client.publish(status_topic, status_payload, qos=qos)
        except Exception as e:
            self._logger.error(f"MQTT发布失败: {e}")

    def publish_status(self, device_id: str, status: str, message: str = ""):
        """发布设备状态"""
        with self._lock:
            if not self._connected or not self._client:
                return
            client = self._client
            qos = self._config.get("qos", 1)
            topic_prefix = self._config.get("topic_prefix", "factory/data")

        try:
            import time
            status_topic = f"{topic_prefix}/{device_id}/status"

            payload = json.dumps({
                "device_id": device_id,
                "status": status,
                "message": message,
                "timestamp": int(time.time() * 1000)
            })
            client.publish(status_topic, payload, qos=qos)
        except Exception as e:
            self._logger.error(f"MQTT状态发布失败: {e}")

    @property
    def is_connected(self) -> bool:
        return self._connected


# 全局单例
mqtt_forwarder = MqttForwarder()
