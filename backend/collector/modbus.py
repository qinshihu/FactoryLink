"""
Modbus TCP/RTU 协议采集器
"""
import struct
from typing import Optional

from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from collector.base import BaseCollector
from logger import gateway_logger


class ModbusCollector(BaseCollector):
    """Modbus协议采集器，支持TCP和RTU"""

    def __init__(self, device_config: dict, reconnect_config: dict):
        super().__init__(device_config, reconnect_config)
        self.protocol = device_config.get("protocol", "modbus_tcp")
        self._client = None

    def _create_client(self):
        """根据协议类型创建客户端"""
        if self.protocol == "modbus_rtu":
            com_port = self.device_config.get("com_port") or self.device_config.get("port", "COM1")
            return ModbusSerialClient(
                port=com_port,
                baudrate=self.device_config.get("baudrate", 9600),
                parity=self.device_config.get("parity", "N"),
                stopbits=self.device_config.get("stopbits", 1),
                bytesize=self.device_config.get("databits", 8),
                timeout=3
            )
        else:
            # modbus_tcp
            return ModbusTcpClient(
                host=self.device_config.get("ip", "127.0.0.1"),
                port=self.device_config.get("port", 502),
                timeout=3
            )

    def _do_connect(self) -> bool:
        self._client = self._create_client()
        return self._client.connect()

    def _do_disconnect(self):
        if self._client:
            self._client.close()
            self._client = None

    def _parse_address(self, address: str) -> tuple:
        """
        解析Modbus地址
        支持格式: 40001(保持寄存器), 30001(输入寄存器), 10001(线圈), 00001(离散输入)
        返回: (function_code, register_address, count)
        """
        addr = int(address)
        if 40001 <= addr <= 49999:
            return (3, addr - 40001, 1)  # 保持寄存器
        elif 30001 <= addr <= 39999:
            return (4, addr - 30001, 1)  # 输入寄存器
        elif 1 <= addr <= 9999:
            return (1, addr - 1, 1)  # 线圈
        elif 10001 <= addr <= 19999:
            return (2, addr - 10001, 1)  # 离散输入
        else:
            return (3, addr, 1)  # 默认按保持寄存器处理

    def _read_register(self, func_code: int, reg_addr: int, count: int, data_type: str) -> Optional[dict]:
        """读取寄存器并根据数据类型解析"""
        slave_id = self.device_config.get("slave_id", 1)

        try:
            if func_code == 3:
                result = self._client.read_holding_registers(reg_addr, count=count, device_id=slave_id)
            elif func_code == 4:
                result = self._client.read_input_registers(reg_addr, count=count, device_id=slave_id)
            elif func_code == 1:
                result = self._client.read_coils(reg_addr, count=count, device_id=slave_id)
            elif func_code == 2:
                result = self._client.read_discrete_inputs(reg_addr, count=count, device_id=slave_id)
            else:
                return None

            if result.isError():
                return None

            # 线圈和离散输入使用 .bits，寄存器使用 .registers
            if func_code in (1, 2):
                bits = result.bits
                return self._decode_bits(bits, data_type)
            else:
                registers = result.registers
                return self._decode_registers(registers, data_type)
        except Exception:
            return None

    def _decode_bits(self, bits: list, data_type: str):
        """解码位数据（线圈/离散输入）"""
        if not bits:
            return None
        if data_type == "bool":
            return bool(bits[0])
        # 多位组合为整数
        value = 0
        for i, bit in enumerate(bits[:16]):
            if bit:
                value |= (1 << i)
        if data_type == "int16" and value > 32767:
            value -= 65536
        return value

    def _decode_registers(self, registers: list, data_type: str):
        """将Modbus寄存器值解码为对应数据类型"""
        if not registers:
            return None

        if data_type in ("bool",):
            return bool(registers[0])

        if data_type in ("int16",):
            val = registers[0]
            if val > 32767:
                val -= 65536
            return val

        if data_type in ("uint16",):
            return registers[0]

        if data_type in ("int32", "uint32", "float"):
            if len(registers) < 2:
                return None
            raw = (registers[0] << 16) | registers[1]
            raw_bytes = struct.pack('>I', raw)

            if data_type == "int32":
                return struct.unpack('>i', raw_bytes)[0]
            elif data_type == "uint32":
                return struct.unpack('>I', raw_bytes)[0]
            elif data_type == "float":
                return round(struct.unpack('>f', raw_bytes)[0], 6)

        if data_type == "double":
            if len(registers) < 4:
                return None
            raw = (registers[0] << 48) | (registers[1] << 32) | (registers[2] << 16) | registers[3]
            raw_bytes = struct.pack('>Q', raw)
            return round(struct.unpack('>d', raw_bytes)[0], 6)

        # 默认按int16处理
        return registers[0]

    def _do_read(self, point: dict) -> Optional[dict]:
        address = point.get("address", "")
        data_type = point.get("type", "int16")
        rate = point.get("rate", 1.0)
        offset = point.get("offset", 0.0)
        point_name = point.get("name", "")

        func_code, reg_addr, count = self._parse_address(address)

        # 根据数据类型调整寄存器数量
        type_reg_count = {
            "bool": 1, "int16": 1, "uint16": 1,
            "int32": 2, "uint32": 2, "float": 2,
            "double": 4
        }
        count = type_reg_count.get(data_type, 1)

        raw_value = self._read_register(func_code, reg_addr, count, data_type)
        if raw_value is None:
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
