"""
Game settings and constants
"""
from dataclasses import dataclass
from typing import Tuple, Dict, List
import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 60, 60)
DARK_RED = (180, 30, 30)
GREEN = (60, 220, 60)
DARK_GREEN = (30, 180, 30)
BLUE = (60, 60, 220)
DARK_BLUE = (30, 30, 180)
YELLOW = (220, 220, 60)
DARK_YELLOW = (180, 180, 30)
ORANGE = (255, 140, 0)
DARK_ORANGE = (220, 110, 0)
PURPLE = (180, 60, 220)
DARK_PURPLE = (140, 30, 180)
CYAN = (60, 220, 220)
DARK_CYAN = (30, 180, 180)
PINK = (255, 105, 180)
DARK_PINK = (220, 70, 150)
GOLD = (255, 215, 0)
DARK_GOLD = (218, 165, 32)

# Background colors
BG_COLOR = (10, 10, 30)
BG_GRADIENT_TOP = (20, 20, 60)
BG_GRADIENT_BOTTOM = (5, 5, 20)

# Font settings
FONT_NAME = "PressStart2P.ttf"
FONT_SIZE = 24

# Game settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 15
WIDE_PADDLE_WIDTH = 160
BALL_RADIUS = 10
BALL_SPEED = 7
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_PADDING = 5
BRICK_CORNER_RADIUS = 8  # Rounded corners for bricks
INITIAL_LIVES = 3

# Power-up settings
POWERUP_SIZE = 30
POWERUP_SPEED = 3
POWERUP_DURATION = {
    "WIDE": 20000,  # 20 seconds
    "STICKY": 15000,  # 15 seconds
    "SLOW": 10000,  # 10 seconds
}
POWERUP_DROP_CHANCE = 0.2  # 20% chance

# Background settings
STAR_COUNT = 150
METEOR_COUNT = 5
METEOR_SPEED_MIN = 2
METEOR_SPEED_MAX = 5
NEBULA_COUNT = 3
NEBULA_DRIFT_SPEED = 0.2
STAR_TWINKLE_SPEED = 2

@dataclass
class PowerUpType:
    """Power-up type with properties"""
    id: str
    color: Tuple[int, int, int]
    glow_color: Tuple[int, int, int]
    chance: float  # Relative chance within the drop chance

# Power-up types
POWERUPS = {
    "WIDE": PowerUpType("WIDE", RED, (255, 100, 100), 0.25),       # Wider paddle
    "STICKY": PowerUpType("STICKY", BLUE, (100, 100, 255), 0.25),  # Sticky paddle
    "MULTI": PowerUpType("MULTI", GREEN, (100, 255, 100), 0.25),   # Multi-ball
    "SLOW": PowerUpType("SLOW", YELLOW, (255, 255, 100), 0.25),    # Slow-motion
}

@dataclass
class BrickType:
    """Brick type with properties"""
    id: str
    color: Tuple[int, int, int]
    edge_color: Tuple[int, int, int]  # Darker color for edges
    highlight_color: Tuple[int, int, int]  # Lighter color for highlights
    points: int
    hits: int  # Hits required to break

# Brick types with standard colors - increasing hits for each row
BRICK_TYPES = {
    "1": BrickType("1", RED, DARK_RED, (255, 150, 150), 10, 1),
    "2": BrickType("2", ORANGE, DARK_ORANGE, (255, 200, 150), 20, 2),
    "3": BrickType("3", YELLOW, DARK_YELLOW, (255, 255, 150), 30, 3),
    "4": BrickType("4", GREEN, DARK_GREEN, (150, 255, 150), 40, 4),
    "5": BrickType("5", BLUE, DARK_BLUE, (150, 150, 255), 50, 5),
    "6": BrickType("6", PURPLE, DARK_PURPLE, (200, 150, 255), 60, 6),
    "7": BrickType("7", CYAN, DARK_CYAN, (150, 255, 255), 70, 7),
    "X": BrickType("X", GOLD, DARK_GOLD, (255, 240, 150), 0, -1),  # Unbreakable brick
}

# Sound effects
SOUNDS = {
    "bounce": "bounce.wav",
    "brick_break": "brick_break.wav",
    "powerup": "powerup.wav",
    "game_over": "game_over.wav",
    "level_complete": "level_complete.wav",
}

# Level file paths
LEVEL_FILES = [
    "levels/level1.json",
    "levels/level2.json",
    "levels/level3.json",
]
