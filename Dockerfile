FROM python:3.11-slim

LABEL maintainer="谭策 | IT Online"
LABEL project="FactoryLink - 工业数据采集网关"
LABEL version="1.0.0"

WORKDIR /app

# 安装系统依赖（Pillow 需要，虽然 Docker 不用托盘但 openpyxl 等可能间接依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 使用 Docker 专用依赖文件（不含 pystray/Pillow，Docker 不需要托盘图标）
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/

EXPOSE 8000

WORKDIR /app/backend
CMD ["python", "main.py"]
