FROM python:3.11

LABEL maintainer="谭策 | IT Online"
LABEL project="FactoryLink - 工业数据采集网关"
LABEL version="1.0.0"

WORKDIR /app

# 使用 Docker 专用依赖文件（不含 pystray/Pillow/openpyxl）
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/

EXPOSE 8000

WORKDIR /app/backend
CMD ["python", "main.py"]
