#!/usr/bin/env python3
"""
Brick Breaker Game - Main Entry Point
"""
import pygame
import sys
import os
from settings import *

def main() -> None:
    """Main function to run the game"""
    # Initialize pygame
    pygame.init()
    
    # Try to initialize the mixer, but continue if it fails
    try:
        pygame.mixer.init()
    except pygame.error:
        print("Warning: Audio device not available. Game will run without sound.")
    
    pygame.display.set_caption("Brick Breaker")
    
    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Create a default font before importing game
    default_font = pygame.font.Font(None, FONT_SIZE)
    
    # Import game after pygame is initialized
    from game import Game
    
    # Create game instance
    game = Game(screen)
    game.font = default_font  # Ensure we have a valid font
    
    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Pass events to game
            game.handle_events(event)
        
        # Fill the screen with background color
        screen.fill(BG_COLOR)
        
        # Update and render game
        game.update()
        game.render()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
