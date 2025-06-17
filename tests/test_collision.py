"""
Tests for collision detection
"""
import unittest
import pygame
import sys
import os
import math

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sprites import Ball, Paddle, Brick
from src.settings import WHITE, RED

class TestCollision(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.paddle = Paddle()
        self.ball = Ball()
        self.brick = Brick(100, 100, "1")
    
    def tearDown(self):
        """Tear down test fixtures"""
        pygame.quit()
    
    def test_ball_paddle_collision(self):
        """Test ball-paddle collision detection and angle calculation"""
        # Position ball directly above paddle
        self.ball.rect.centerx = self.paddle.rect.centerx
        self.ball.rect.bottom = self.paddle.rect.top
        self.ball.dy = 5  # Moving downward
        
        # Check collision detection
        collision = self.ball.check_paddle_collision(self.paddle)
        self.assertTrue(collision)
        
        # Ball should now be moving upward
        self.assertLess(self.ball.dy, 0)
        
        # Test collision from left edge of paddle
        self.ball.rect.centerx = self.paddle.rect.left + 10
        self.ball.rect.bottom = self.paddle.rect.top
        self.ball.dy = 5  # Moving downward
        
        collision = self.ball.check_paddle_collision(self.paddle)
        self.assertTrue(collision)
        
        # Ball should be moving up and left
        self.assertLess(self.ball.dy, 0)
        self.assertLess(self.ball.dx, 0)
        
        # Test collision from right edge of paddle
        self.ball.rect.centerx = self.paddle.rect.right - 10
        self.ball.rect.bottom = self.paddle.rect.top
        self.ball.dy = 5  # Moving downward
        
        collision = self.ball.check_paddle_collision(self.paddle)
        self.assertTrue(collision)
        
        # Ball should be moving up and right
        self.assertLess(self.ball.dy, 0)
        self.assertGreater(self.ball.dx, 0)
    
    def test_ball_brick_collision_bottom(self):
        """Test ball-brick collision from bottom"""
        # Position ball below brick
        self.ball.rect.centerx = self.brick.rect.centerx
        self.ball.rect.top = self.brick.rect.bottom + 1
        self.ball.dy = -5  # Moving upward
        
        # Check collision detection
        collision = self.ball.check_brick_collision(self.brick)
        self.assertTrue(collision)
        
        # Ball should now be moving downward
        self.assertGreater(self.ball.dy, 0)
    
    def test_ball_brick_collision_top(self):
        """Test ball-brick collision from top"""
        # Position ball above brick
        self.ball.rect.centerx = self.brick.rect.centerx
        self.ball.rect.bottom = self.brick.rect.top - 1
        self.ball.dy = 5  # Moving downward
        
        # Check collision detection
        collision = self.ball.check_brick_collision(self.brick)
        self.assertTrue(collision)
        
        # Ball should now be moving upward
        self.assertLess(self.ball.dy, 0)
    
    def test_ball_brick_collision_left(self):
        """Test ball-brick collision from left"""
        # Position ball to the left of brick
        self.ball.rect.right = self.brick.rect.left - 1
        self.ball.rect.centery = self.brick.rect.centery
        self.ball.dx = 5  # Moving right
        
        # Check collision detection
        collision = self.ball.check_brick_collision(self.brick)
        self.assertTrue(collision)
        
        # Ball should now be moving left
        self.assertLess(self.ball.dx, 0)
    
    def test_ball_brick_collision_right(self):
        """Test ball-brick collision from right"""
        # Position ball to the right of brick
        self.ball.rect.left = self.brick.rect.right + 1
        self.ball.rect.centery = self.brick.rect.centery
        self.ball.dx = -5  # Moving left
        
        # Check collision detection
        collision = self.ball.check_brick_collision(self.brick)
        self.assertTrue(collision)
        
        # Ball should now be moving right
        self.assertGreater(self.ball.dx, 0)
    
    def test_no_collision(self):
        """Test no collision when objects are far apart"""
        # Position ball far from brick and paddle
        self.ball.rect.centerx = 400
        self.ball.rect.centery = 300
        
        # Check collision detection
        paddle_collision = self.ball.check_paddle_collision(self.paddle)
        brick_collision = self.ball.check_brick_collision(self.brick)
        
        self.assertFalse(paddle_collision)
        self.assertFalse(brick_collision)

if __name__ == '__main__':
    unittest.main()
