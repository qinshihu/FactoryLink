"""
日志管理模块 - 文件轮转、API读取
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from datetime import datetime


def get_log_dir() -> Path:
    """获取日志目录"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "logs"
    return Path(__file__).parent.parent / "logs"


class GatewayLogger:
    """网关日志管理器"""

    def __init__(self):
        self.log_dir = get_log_dir()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "gateway.log"
        self._logger: Optional[logging.Logger] = None
        self._setup()

    def _setup(self):
        """配置日志系统"""
        self._logger = logging.getLogger("gateway")
        self._logger.setLevel(logging.INFO)

        # 避免重复添加handler
        if self._logger.handlers:
            return

        # 文件handler（轮转：10MB×5个文件）
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)

        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_formatter)
        self._logger.addHandler(console_handler)

    def get_logger(self, name: str = "gateway") -> logging.Logger:
        """获取指定名称的logger"""
        return logging.getLogger(name)

    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        if level.upper() in level_map:
            self._logger.setLevel(level_map[level.upper()])

    def read_logs(self, level: Optional[str] = None, lines: int = 200) -> list:
        """读取最近的日志行，支持按级别筛选"""
        if not self.log_file.exists():
            return []

        result = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            # 取最近N行
            recent = all_lines[-lines:]

            for line in recent:
                line = line.strip()
                if not line:
                    continue
                if level:
                    level_tag = f"[{level.upper()}]"
                    if level_tag not in line:
                        continue
                result.append(line)
        except Exception:
            pass

        return result


gateway_logger = GatewayLogger()
logger = gateway_logger.get_logger()
