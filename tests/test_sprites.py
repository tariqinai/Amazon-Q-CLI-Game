"""
Tests for the sprites module
"""
import unittest
import pygame
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sprites import Paddle, Ball, Brick
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED

class TestSprites(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def tearDown(self):
        """Tear down test fixtures"""
        pygame.quit()
    
    def test_paddle_initialization(self):
        """Test that the paddle initializes correctly"""
        paddle = Paddle()
        self.assertIsNotNone(paddle)
        self.assertEqual(paddle.rect.centerx, SCREEN_WIDTH // 2)
    
    def test_ball_initialization(self):
        """Test that the ball initializes correctly"""
        ball = Ball()
        self.assertIsNotNone(ball)
        self.assertEqual(ball.rect.centerx, SCREEN_WIDTH // 2)
    
    def test_brick_initialization(self):
        """Test that a brick initializes correctly"""
        brick = Brick(100, 50, RED)
        self.assertIsNotNone(brick)
        self.assertEqual(brick.rect.x, 100)
        self.assertEqual(brick.rect.y, 50)

if __name__ == '__main__':
    unittest.main()
