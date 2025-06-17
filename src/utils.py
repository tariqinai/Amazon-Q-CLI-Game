"""
Utility functions for the game
"""
import pygame
import os

def load_image(filename, scale=1):
    """Load an image from the assets folder"""
    path = os.path.join('assets', 'images', filename)
    try:
        image = pygame.image.load(path)
        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        return pygame.Surface((50, 50))

def load_sound(filename):
    """Load a sound from the assets folder"""
    path = os.path.join('assets', 'sounds', filename)
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Error loading sound {path}: {e}")
        return None
