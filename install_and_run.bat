@echo off
chcp 65001 > nul
echo .
echo ================================================
echo 🎨 批量图片水印工具 - 快速启动
echo ================================================
echo .

echo 正在检查 Python 环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 环境正常
echo .

echo 正在安装依赖...
pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖安装可能出现问题，继续执行...
) else (
    echo ✅ 依赖安装完成
)

echo .
echo ================================================
echo 🚀 启动程序...
echo ================================================
echo .

python watermark_gui.py

pause
