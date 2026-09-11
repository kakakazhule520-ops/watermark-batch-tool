#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
这是一个用来将 watermark_gui.py 转换为 .exe 文件的脚本
使用方法：python build_exe.py

如果提示找不到 pyinstaller，先运行：
pip install pyinstaller
"""

import os
import sys
import subprocess

print("="*50)
print("🔨 开始构建 EXE 文件")
print("="*50)

# 检查 pyinstaller 是否安装
try:
    import PyInstaller
except ImportError:
    print("❌ 未找到 PyInstaller，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# 构建命令
command = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",  # 单一可执行文件
    "--windowed",  # 不显示控制台窗口
    "--name=水印工具",  # 程序名称
    "--icon=watermark_icon.ico",  # 图标（可选）
    "watermark_gui.py"
]

print("\n执行构建命令...")
print(" ".join(command))
print()

try:
    result = subprocess.run(command, check=True)
    print("\n" + "="*50)
    print("✅ EXE 文件构建成功！")
    print("="*50)
    print("\n📍 文件位置: ./dist/水印工具.exe")
    print("\n💡 提示: 将 exe 文件复制到其他地方使用，确保 requirements.txt 和图片文件夹在相同位置。")
except subprocess.CalledProcessError as e:
    print("\n" + "="*50)
    print("❌ 构建失败")
    print("="*50)
    print(f"错误信息: {e}")
    sys.exit(1)
