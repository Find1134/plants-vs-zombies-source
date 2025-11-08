import unittest
import pygame
from game import Game, Config

class TestGame(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        pygame.init()
        
    def test_config(self):
        """测试配置"""
        self.assertEqual(Config.SCREEN_WIDTH, 800)
        self.assertEqual(Config.SCREEN_HEIGHT, 600)
        
    def test_game_initialization(self):
        """测试游戏初始化"""
        game = Game()
        # 初始化测试代码
        
    def tearDown(self):
        """测试后清理"""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()