#!/usr/bin/env python3
"""
游戏构建脚本
"""

import os
import shutil
import subprocess

def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    try:
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--name', 'MyGame',
            '--add-data', 'assets:assets',
            'game.py'
        ], check=True)
        print("构建成功！")
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")

if __name__ == "__main__":
    build_executable()