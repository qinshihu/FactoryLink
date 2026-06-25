"""
Pydantic数据模型 - API请求/响应模型
"""
from typing import Optional, List, Any, Union
from pydantic import BaseModel, Field


class PointConfig(BaseModel):
    """点位配置"""
    name: str = Field(..., description="点位名称")
    address: str = Field(..., description="点位地址")
    type: str = Field(default="float", description="数据类型")
    rate: float = Field(default=1.0, description="倍率")
    offset: float = Field(default=0.0, description="偏移量")
    unit: str = Field(default="", description="单位")


class DeviceConfig(BaseModel):
    """设备配置"""
    id: str = Field(..., description="设备ID")
    name: str = Field(..., description="设备名称")
    protocol: str = Field(..., description="协议类型: modbus_tcp/modbus_rtu/s7/mitsubishi")
    enabled: bool = Field(default=True, description="是否启用")
    # 通用网络字段
    ip: Optional[str] = Field(default=None, description="IP地址")
    port: Optional[Union[int, str]] = Field(default=None, description="端口号(TCP)或串口号(RTU)")
    # Modbus RTU 串口字段
    com_port: Optional[str] = Field(default=None, description="串口号")
    baudrate: Optional[int] = Field(default=None, description="波特率")
    parity: Optional[str] = Field(default="N", description="校验位")
    databits: Optional[int] = Field(default=8, description="数据位")
    stopbits: Optional[int] = Field(default=1, description="停止位")
    slave_id: Optional[int] = Field(default=1, description="从站ID")
    # S7 特有字段
    rack: Optional[int] = Field(default=0, description="机架号")
    slot: Optional[int] = Field(default=1, description="插槽号")
    # 三菱MC 特有字段
    plc_type: Optional[str] = Field(default=None, description="PLC型号")
    # 点位列表
    points: List[PointConfig] = Field(default_factory=list, description="点位列表")


class MqttConfig(BaseModel):
    """MQTT配置"""
    host: str = Field(default="", description="MQTT服务器地址")
    port: int = Field(default=1883, description="MQTT端口")
    client_id: str = Field(default="gateway-001", description="客户端ID")
    topic_prefix: str = Field(default="factory/data", description="Topic前缀")
    username: str = Field(default="", description="用户名")
    password: str = Field(default="", description="密码")
    qos: int = Field(default=1, description="QoS级别")
    enabled: bool = Field(default=False, description="是否启用")


class ReconnectConfig(BaseModel):
    """重连配置"""
    max_retries: int = Field(default=0, description="最大重试次数，0=无限")
    base_delay: int = Field(default=1, description="基础延迟（秒）")
    max_delay: int = Field(default=60, description="最大延迟（秒）")


class GatewayConfig(BaseModel):
    """网关完整配置"""
    gateway_name: str = Field(default="默认网关", description="网关名称")
    devices: List[DeviceConfig] = Field(default_factory=list, description="设备列表")
    mqtt: MqttConfig = Field(default_factory=MqttConfig, description="MQTT配置")
    collect_interval: int = Field(default=1000, description="采集间隔（毫秒）")
    reconnect: ReconnectConfig = Field(default_factory=ReconnectConfig, description="重连配置")


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool = True
    message: str = ""
    data: Any = None


class PointValue(BaseModel):
    """点位值"""
    value: Any
    unit: str = ""
    quality: str = "good"


class DeviceData(BaseModel):
    """设备采集数据"""
    gateway: str = ""
    device_id: str = ""
    device_name: str = ""
    timestamp: int = 0
    values: dict = Field(default_factory=dict)


class DeviceStatus(BaseModel):
    """设备状态"""
    device_id: str
    status: str = "offline"  # online/offline/error
    timestamp: int = 0
    message: str = ""


class LogQuery(BaseModel):
    """日志查询参数"""
    level: Optional[str] = None
    lines: int = Field(default=200, ge=1, le=1000)


class TestConnectionRequest(BaseModel):
    """测试连接请求"""
    device: DeviceConfig


class TestConnectionResponse(BaseModel):
    """测试连接响应"""
    success: bool
    message: str
    elapsed_ms: int = 0


class AIParseRequest(BaseModel):
    """AI解析请求"""
    input: str = Field(..., description="用户的自然语言描述")
    api_url: Optional[str] = Field(default=None, description="AI API地址")
    api_key: Optional[str] = Field(default=None, description="AI API Key")
    model: Optional[str] = Field(default=None, description="模型名称")


class AIParseResponse(BaseModel):
    """AI解析响应"""
    success: bool
    message: str = ""
    config: Optional[dict] = None


class AIConfig(BaseModel):
    """AI配置"""
    enabled: bool = Field(default=False, description="是否启用AI助手")
    api_url: str = Field(default="https://api.openai.com/v1", description="AI API地址")
    api_key: str = Field(default="", description="AI API Key")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
