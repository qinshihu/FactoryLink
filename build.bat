@echo off
chcp 65001 >nul
echo ============================================
echo   工业数据采集网关 - 打包脚本
echo ============================================
echo.

echo [1/3] 正在安装前端依赖...
cd /d "%~dp0frontend"
call npm install
if %errorlevel% neq 0 (
    echo 前端依赖安装失败！
    pause
    exit /b 1
)

echo.
echo [2/3] 正在编译前端...
call npm run build
if %errorlevel% neq 0 (
    echo 前端编译失败！
    pause
    exit /b 1
)

cd /d "%~dp0"

echo.
echo [3/3] 正在打包后端...
pyinstaller --onefile ^
    --windowed ^
    --add-data "frontend/dist;frontend/dist" ^
    --hidden-import pymodbus ^
    --hidden-import snap7 ^
    --hidden-import pymcprotocol ^
    --hidden-import paho.mqtt.client ^
    --hidden-import uvicorn ^
    --hidden-import fastapi ^
    --hidden-import websockets ^
    --hidden-import pystray ^
    --name "工业数据采集网关" ^
    --icon "icon.ico" ^
    backend/main.py

if %errorlevel% neq 0 (
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo   打包完成！
echo   输出文件: dist/工业数据采集网关.exe
echo ============================================
pause
