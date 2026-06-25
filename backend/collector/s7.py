"""
西门子S7协议采集器
使用python-snap7 3.0纯Python实现，无需DLL依赖
"""
import struct
from typing import Optional

from collector.base import BaseCollector
from logger import gateway_logger


class S7Collector(BaseCollector):
    """西门子S7协议采集器，支持S7-1200/1500/300/400"""

    def __init__(self, device_config: dict, reconnect_config: dict):
        super().__init__(device_config, reconnect_config)
        self._client = None

    def _do_connect(self) -> bool:
        try:
            from snap7 import Client
            self._client = Client()
            self._client.connect(
                self.device_config.get("ip", "127.0.0.1"),
                self.device_config.get("rack", 0),
                self.device_config.get("slot", 1)
            )
            return self._client.get_connected()
        except ImportError:
            self._logger.error("python-snap7库未安装，请执行: pip install python-snap7")
            return False
        except Exception as e:
            self._logger.error(f"S7连接失败: {e}")
            return False

    def _do_disconnect(self):
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None

    def _parse_address(self, address: str) -> tuple:
        """
        解析S7地址，严格匹配已知格式，无法识别时抛出异常
        支持格式:
          DB1.DBD0  -> (area='DB', db_number=1, start=0, bit_offset=0, data_type='float')
          DB1.DBX0.0 -> (area='DB', db_number=1, start=0, bit_offset=0, data_type='bool')
          DB1.DBW0  -> (area='DB', db_number=1, start=0, bit_offset=0, data_type='int16')
          M0.0      -> (area='M', db_number=0, start=0, bit_offset=0, data_type='bool')
          I0.0      -> (area='I', db_number=0, start=0, bit_offset=0, data_type='bool')
          Q0.0      -> (area='Q', db_number=0, start=0, bit_offset=0, data_type='bool')
        """
        import re

        # DB地址: DB{num}.DB{D|X|W|B}{offset} 或 DB{num}.DBX{byte}.{bit}
        db_pattern = r'^DB(\d+)\.(DB[XDWB])(\d+)(?:\.(\d+))?$'
        db_match = re.match(db_pattern, address, re.IGNORECASE)
        if db_match:
            db_number = int(db_match.group(1))
            type_prefix = db_match.group(2).upper()
            byte_offset = int(db_match.group(3))
            bit_offset = int(db_match.group(4)) if db_match.group(4) else 0
            type_hint = {
                "DBX": "bool", "DBB": "uint16",
                "DBW": "int16", "DBD": "float",
            }.get(type_prefix, "float")
            return ("DB", db_number, byte_offset, bit_offset, type_hint)

        # M/I/Q/E/A地址: {M|I|Q|E|A}{byte}.{bit}
        io_pattern = r'^([MIQEAmiquea])(\d+)(?:\.(\d+))?$'
        io_match = re.match(io_pattern, address)
        if io_match:
            area_prefix = io_match.group(1).upper()
            byte_offset = int(io_match.group(2))
            bit_offset = int(io_match.group(3)) if io_match.group(3) else 0
            return (area_prefix, 0, byte_offset, bit_offset, "bool")

        # 无法识别的格式
        raise ValueError(f"无法识别的S7地址格式: {address}，支持格式: DB1.DBD0, DB1.DBX0.0, M0.0, I0.0, Q0.0")

    def _do_read(self, point: dict) -> Optional[dict]:
        if not self._client:
            return None

        address = point.get("address", "")
        data_type = point.get("type", "float")
        rate = point.get("rate", 1.0)
        offset = point.get("offset", 0.0)
        point_name = point.get("name", "")

        try:
            area, db_number, start, bit_offset, _ = self._parse_address(address)

            # 根据数据类型确定读取长度
            type_sizes = {
                "bool": 1,
                "int16": 2,
                "uint16": 2,
                "int32": 4,
                "uint32": 4,
                "float": 4,
                "double": 8,
            }
            size = type_sizes.get(data_type, 4)

            # 读取数据
            if area == "DB":
                data = self._client.db_read(db_number, start, size)
            elif area == "M":
                data = self._client.mb_read(start, size)
            elif area in ("I", "E"):
                data = self._client.eb_read(start, size)
            elif area in ("Q", "A"):
                data = self._client.ab_read(start, size)
            else:
                data = self._client.db_read(db_number, start, size)

            if data is None:
                return None

            # 解析数据
            value = self._decode_data(data, data_type, bit_offset)

            # 应用倍率
            if isinstance(value, (int, float)):
                value = value * rate + offset

            return {
                "name": point_name,
                "value": value,
                "unit": point.get("unit", ""),
                "quality": "good"
            }
        except ImportError:
            self._logger.error("python-snap7库未安装")
            return None
        except Exception as e:
            self._logger.error(f"读取S7点位 {point_name} 失败: {e}")
            return None

    def _decode_data(self, data: bytes, data_type: str, bit_offset: int = 0):
        """解码S7读取的原始数据"""
        if data_type == "bool":
            return bool(data[0] & (1 << bit_offset))
        elif data_type == "int16":
            return struct.unpack('>h', data[:2])[0]
        elif data_type == "uint16":
            return struct.unpack('>H', data[:2])[0]
        elif data_type == "int32":
            return struct.unpack('>i', data[:4])[0]
        elif data_type == "uint32":
            return struct.unpack('>I', data[:4])[0]
        elif data_type == "float":
            return round(struct.unpack('>f', data[:4])[0], 6)
        elif data_type == "double":
            return round(struct.unpack('>d', data[:8])[0], 6)
        elif data_type == "string":
            return data.decode('ascii', errors='ignore').rstrip('\x00')
        else:
            return struct.unpack('>f', data[:4])[0]
