"""
三菱MC协议采集器
使用pymcprotocol库，支持FX5U、Q系列、L系列
"""
import struct
from typing import Optional

from collector.base import BaseCollector
from logger import gateway_logger


class MitsubishiCollector(BaseCollector):
    """三菱MC协议采集器"""

    def __init__(self, device_config: dict, reconnect_config: dict):
        super().__init__(device_config, reconnect_config)
        self._client = None

    def _do_connect(self) -> bool:
        try:
            from pymcprotocol import Type3E
            ip = self.device_config.get("ip", "127.0.0.1")
            port = self.device_config.get("port", 5000)
            self._client = Type3E()
            self._client.connect(ip, port)
            return True
        except ImportError:
            self._logger.error("pymcprotocol库未安装，请执行: pip install pymcprotocol")
            return False
        except Exception as e:
            self._logger.error(f"三菱MC连接失败: {e}")
            return False

    def _do_disconnect(self):
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def _do_read(self, point: dict) -> Optional[dict]:
        if not self._client:
            return None

        address = point.get("address", "")
        data_type = point.get("type", "int16")
        rate = point.get("rate", 1.0)
        offset = point.get("offset", 0.0)
        point_name = point.get("name", "")

        try:
            if data_type == "bool":
                # 位读取：batchread_bitunits(headdevice, readsize)
                values = self._client.batchread_bitunits(address, 1)
                if values and len(values) > 0:
                    raw_value = bool(values[0])
                else:
                    return None
            elif data_type in ("int16", "uint16"):
                values = self._client.batchread_wordunits(address, 1)
                if values and len(values) > 0:
                    raw = values[0]
                    if data_type == "int16" and raw > 32767:
                        raw -= 65536
                    raw_value = raw
                else:
                    return None
            elif data_type in ("int32", "uint32", "float"):
                values = self._client.batchread_wordunits(address, 2)
                if values and len(values) >= 2:
                    raw = (values[0] & 0xFFFF) | ((values[1] & 0xFFFF) << 16)
                    if data_type == "int32":
                        if raw > 0x7FFFFFFF:
                            raw -= 0x100000000
                        raw_value = raw
                    elif data_type == "uint32":
                        raw_value = raw
                    elif data_type == "float":
                        raw_value = round(struct.unpack('<f', struct.pack('<I', raw))[0], 6)
                    else:
                        raw_value = raw
                else:
                    return None
            elif data_type == "double":
                values = self._client.batchread_wordunits(address, 4)
                if values and len(values) >= 4:
                    lo = (values[0] & 0xFFFF) | ((values[1] & 0xFFFF) << 16)
                    hi = (values[2] & 0xFFFF) | ((values[3] & 0xFFFF) << 16)
                    raw = lo | (hi << 32)
                    raw_value = round(struct.unpack('<d', struct.pack('<Q', raw))[0], 6)
                else:
                    return None
            else:
                values = self._client.batchread_wordunits(address, 1)
                if values and len(values) > 0:
                    raw_value = values[0]
                else:
                    return None

            # 应用倍率
            if isinstance(raw_value, (int, float)):
                value = raw_value * rate + offset
            else:
                value = raw_value

            return {
                "name": point_name,
                "value": value,
                "unit": point.get("unit", ""),
                "quality": "good"
            }
        except ImportError:
            self._logger.error("pymcprotocol库未安装")
            return None
        except Exception as e:
            self._logger.error(f"读取三菱MC点位 {point_name} 失败: {e}")
            return None
