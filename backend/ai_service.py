"""
AI配置助手服务 - 通过大模型将自然语言转换为设备配置
支持 OpenAI 兼容接口（OpenAI / 通义千问 / DeepSeek 等）
"""
import json
import httpx
from typing import Optional, AsyncGenerator
from logger import logger

# 设备配置的 JSON Schema 描述，作为 System Prompt
SYSTEM_PROMPT = """你是一个工业设备配置专家。根据用户的自然语言描述，生成设备配置JSON。

## 支持的协议
- modbus_tcp: Modbus TCP，默认端口502
- modbus_rtu: Modbus RTU（串口），需要串口号、波特率等
- s7: 西门子S7系列（S7-1200/1500/300/400），默认机架0、插槽1
- mitsubishi: 三菱MC协议，默认端口5000

## 设备配置JSON格式
{
  "name": "设备名称",
  "protocol": "协议类型",
  "ip": "IP地址",
  "port": 端口号,
  "slave_id": 从站ID(Modbus),
  "rack": 机架号(S7),
  "slot": 插槽号(S7),
  "plc_type": "PLC型号(三菱)",
  "com_port": "串口号(Modbus RTU)",
  "baudrate": 波特率(Modbus RTU),
  "parity": "校验位(Modbus RTU): N/E/O",
  "databits": 数据位(Modbus RTU),
  "stopbits": 停止位(Modbus RTU),
  "enabled": true,
  "points": [
    {
      "name": "点位名称",
      "address": "地址",
      "type": "数据类型: bool/int16/uint16/int32/uint32/float/double",
      "rate": 倍率,
      "offset": 偏移量,
      "unit": "单位"
    }
  ]
}

## 地址格式说明
- Modbus: 保持寄存器40001-49999, 输入寄存器30001-39999, 线圈00001-09999, 离散输入10001-19999
- S7: DB块格式 DB1.DBD0(浮点), DB1.DBW0(字), DB1.DBX0.0(位)
- 三菱: D100(数据寄存器), X0(输入), Y0(输出), M0(内部继电器)

## 规则
1. 只返回JSON，不要任何解释文字
2. 如果用户没有指定点位，默认生成3-5个常见点位
3. 数据类型根据地址合理推断：DBD→float, DBW→int16, 4xxxx→uint16
4. 单位根据点位名称合理推断：温度→℃, 压力→MPa, 流量→m³/h, 转速→rpm, 液位→m
5. 如果信息不足，使用合理的默认值
6. 端口号：Modbus TCP默认502，三菱MC默认5000，S7默认102
7. 如果用户提到了具体型号（如S7-1200），protocol设为s7，plc_type留空
"""


class AIService:
    """AI配置助手服务"""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def parse_config(
        self,
        user_input: str,
        api_url: str,
        api_key: str,
        model: str
    ) -> dict:
        """将自然语言解析为设备配置JSON"""
        client = await self._get_client()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }

        try:
            response = await client.post(
                f"{api_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"].strip()

            # 提取JSON（处理可能的markdown代码块包裹）
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            config = json.loads(content)

            # 确保必要字段存在
            config.setdefault("enabled", True)
            if "points" not in config:
                config["points"] = []

            # 修正点位字段
            for point in config.get("points", []):
                point.setdefault("type", "float")
                point.setdefault("rate", 1.0)
                point.setdefault("offset", 0.0)
                point.setdefault("unit", "")

            logger.info(f"AI解析成功: {config.get('name', '未知设备')}, {len(config.get('points', []))}个点位")
            return {"success": True, "config": config}

        except httpx.HTTPStatusError as e:
            error_msg = f"AI API请求失败: HTTP {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg = "API Key无效，请检查AI设置"
            elif e.response.status_code == 404:
                error_msg = "API地址无效，请检查AI设置中的API地址"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

        except json.JSONDecodeError as e:
            logger.error(f"AI返回的JSON解析失败: {e}, 原始内容: {content}")
            return {"success": False, "message": f"AI返回格式异常，请重试"}

        except httpx.TimeoutException:
            logger.error("AI API请求超时")
            return {"success": False, "message": "AI API请求超时，请检查网络或API地址"}

        except Exception as e:
            logger.error(f"AI解析异常: {e}")
            return {"success": False, "message": f"AI解析失败: {str(e)}"}

    async def parse_config_stream(
        self,
        user_input: str,
        api_url: str,
        api_key: str,
        model: str
    ) -> AsyncGenerator[str, None]:
        """流式解析，逐步返回结果"""
        client = await self._get_client()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "stream": True
        }

        full_content = ""
        try:
            async with client.stream(
                "POST",
                f"{api_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_content += content
                                yield json.dumps({"type": "chunk", "content": content})
                        except json.JSONDecodeError:
                            continue

            # 流结束，尝试解析完整JSON
            clean = full_content.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            config = json.loads(clean)
            config.setdefault("enabled", True)
            if "points" not in config:
                config["points"] = []
            for point in config.get("points", []):
                point.setdefault("type", "float")
                point.setdefault("rate", 1.0)
                point.setdefault("offset", 0.0)
                point.setdefault("unit", "")

            yield json.dumps({"type": "done", "config": config})

        except httpx.HTTPStatusError as e:
            error_msg = f"AI API请求失败: HTTP {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg = "API Key无效，请检查AI设置"
            yield json.dumps({"type": "error", "message": error_msg})

        except json.JSONDecodeError:
            yield json.dumps({"type": "error", "message": "AI返回格式异常，请重试"})

        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)})


# 全局单例
ai_service = AIService()
