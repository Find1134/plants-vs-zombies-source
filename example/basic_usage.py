#!/usr/bin/env python3
"""
基础使用示例
展示如何运行和测试游戏
"""

import os
import sys
import subprocess
from pathlib import Path

def add_game_to_path():
    """将游戏目录添加到 Python 路径"""
    game_dir = Path(__file__).parent
    if str(game_dir) not in sys.path:
        sys.path.insert(0, str(game_dir))

class GameDemo:
    """游戏演示类"""
    
    @staticmethod
    def run_game():
        """直接运行游戏"""
        print("=== 运行游戏 ===")
        try:
            # 导入并运行游戏
            add_game_to_path()
            from game import Game
            
            game = Game()
            print("游戏初始化成功，开始运行...")
            game.run()
            
        except ImportError as e:
            print(f"导入游戏失败: {e}")
            print("请确保 game.py 在当前目录")
        except Exception as e:
            print(f"游戏运行错误: {e}")
    
    @staticmethod
    def test_game_features():
        """测试游戏功能"""
        print("\n=== 测试游戏功能 ===")
        
        try:
            add_game_to_path()
            from game import Game, Config
            
            # 测试配置
            print(f"游戏配置: {Config.SCREEN_WIDTH}x{Config.SCREEN_HEIGHT}")
            print(f"帧率: {Config.FPS}")
            
            # 测试初始化
            game = Game()
            print("游戏实例创建成功")
            
            # 这里可以添加更多测试...
            
        except Exception as e:
            print(f"功能测试失败: {e}")
    
    @staticmethod
    def check_dependencies():
        """检查依赖"""
        print("\n=== 检查依赖 ===")
        
        dependencies = {
            'pygame': 'pygame',
            'numpy': 'numpy', 
            'PIL': 'Pillow'
        }
        
        missing_deps = []
        
        for name, package in dependencies.items():
            try:
                __import__(package)
                print(f"✅ {name}: 已安装")
            except ImportError:
                print(f"❌ {name}: 未安装")
                missing_deps.append(package)
        
        if missing_deps:
            print(f"\n缺少依赖，请运行: pip install {' '.join(missing_deps)}")
            return False
        else:
            print("所有依赖已安装！")
            return True
    
    @staticmethod
    def show_game_info():
        """显示游戏信息"""
        print("\n=== 游戏信息 ===")
        
        try:
            add_game_to_path()
            from game import Config
            
            info = {
                "游戏名称": getattr(Config, 'GAME_TITLE', '未知'),
                "屏幕分辨率": f"{Config.SCREEN_WIDTH}x{Config.SCREEN_HEIGHT}",
                "目标帧率": Config.FPS,
                "版本": getattr(Config, 'VERSION', '1.0.0')
            }
            
            for key, value in info.items():
                print(f"{key}: {value}")
                
        except Exception as e:
            print(f"获取游戏信息失败: {e}")

def command_line_interface():
    """命令行界面"""
    demo = GameDemo()
    
    print("🎮 Python 游戏使用示例")
    print("=" * 40)
    
    while True:
        print("\n请选择操作:")
        print("1. 检查依赖")
        print("2. 显示游戏信息") 
        print("3. 运行游戏")
        print("4. 测试功能")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            demo.check_dependencies()
        elif choice == '2':
            demo.show_game_info()
        elif choice == '3':
            demo.run_game()
        elif choice == '4':
            demo.test_game_features()
        elif choice == '5':
            print("再见！")
            break
        else:
            print("无效选择，请重新输入")

# 快速启动函数
def quick_start():
    """快速启动游戏"""
    print("🚀 快速启动游戏中...")
    
    demo = GameDemo()
    
    if demo.check_dependencies():
        demo.show_game_info()
        input("\n按 Enter 键开始游戏...")
        demo.run_game()

if __name__ == "__main__":
    # 如果有命令行参数，使用快速启动
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_start()
    else:
        command_line_interface()