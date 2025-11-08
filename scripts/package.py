#!/usr/bin/env python3
"""
游戏打包脚本
用于将 Python 游戏打包为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

class GamePackager:
    def __init__(self):
        self.game_name = "MyPythonGame"
        self.version = "1.0.0"
        self.author = "Your Name"
        
    def clean_previous_builds(self):
        """清理之前的构建文件"""
        build_dirs = ['build', 'dist', f'{self.game_name}.spec']
        for dir_name in build_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"已清理: {dir_name}")
    
    def check_dependencies(self):
        """检查必要的依赖"""
        try:
            import PyInstaller
            return True
        except ImportError:
            print("错误: 未找到 PyInstaller，请安装: pip install pyinstaller")
            return False
    
    def package_game(self, onefile=True, console=False):
        """打包游戏主函数"""
        if not self.check_dependencies():
            return False
            
        self.clean_previous_builds()
        
        # 构建 PyInstaller 命令
        cmd = [
            'pyinstaller',
            '--name', self.game_name,
            '--add-data', 'assets:assets',
            '--icon', 'assets/icon.ico' if os.path.exists('assets/icon.ico') else '',
            '--noconfirm'
        ]
        
        if onefile:
            cmd.append('--onefile')
        if not console:
            cmd.append('--windowed')
            
        cmd.append('game.py')
        
        # 移除空参数
        cmd = [arg for arg in cmd if arg]
        
        print(f"开始打包: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("打包成功！")
            
            # 显示输出信息
            if result.stdout:
                print("输出:", result.stdout)
                
            self._post_package_cleanup()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"打包失败: {e}")
            if e.stderr:
                print("错误输出:", e.stderr)
            return False
    
    def _post_package_cleanup(self):
        """打包后清理"""
        # 保留 dist 目录，清理其他临时文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists(f'{self.game_name}.spec'):
            os.remove(f'{self.game_name}.spec')
            
        print("清理完成，可执行文件在 dist/ 目录")
    
    def create_installer(self):
        """创建安装器（可选）"""
        # 这里可以集成 NSIS、Inno Setup 等创建安装程序
        print("安装器创建功能待实现")
    
    def build_for_multiple_platforms(self):
        """跨平台构建（需要相应环境）"""
        platforms = {
            'windows': '--onefile --console',
            'mac': '--onefile --windowed', 
            'linux': '--onefile'
        }
        
        print("跨平台构建需要分别在对应系统中运行")

def main():
    """主函数"""
    packager = GamePackager()
    
    print(f"=== {packager.game_name} 打包工具 ===")
    print("1. 单文件打包（推荐）")
    print("2. 带控制台窗口打包")
    print("3. 多文件打包")
    print("4. 清理构建文件")
    
    try:
        choice = input("请选择操作 (1-4): ").strip()
        
        if choice == '1':
            packager.package_game(onefile=True, console=False)
        elif choice == '2':
            packager.package_game(onefile=True, console=True)
        elif choice == '3':
            packager.package_game(onefile=False, console=False)
        elif choice == '4':
            packager.clean_previous_builds()
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()