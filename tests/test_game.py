"""
Tests for the game module
"""
import unittest
import pygame
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game import Game
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class TestGame(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game = Game(self.screen)
    
    def tearDown(self):
        """Tear down test fixtures"""
        pygame.quit()
    
    def test_game_initialization(self):
        """Test that the game initializes correctly"""
        self.assertIsNotNone(self.game)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, 3)
        self.assertEqual(self.game.level, 1)

if __name__ == '__main__':
    unittest.main()
