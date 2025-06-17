"""
Game class to manage game state
"""
import pygame
import json
import random
import os
import math
import time
from typing import List, Dict, Tuple, Optional
from settings import *
from sprites import Paddle, Ball, Brick, PowerUp

class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        """Initialize the game"""
        self.screen = screen
        self.running = True
        self.paused = False
        
        # Game objects
        self.paddle = Paddle()
        self.balls = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = []  # Particle effects
        
        # Game state
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 0
        self.level_complete = False
        self.game_over = False
        self.ball_was_active = False  # Track if ball was active to properly count lives
        self.original_ball = None  # Track the original ball to only count lives for it
        
        # Visual effects
        self.shake_amount = 0
        self.shake_time = 0
        self.background_stars = self._create_stars(STAR_COUNT)
        
        # Load sounds
        self.sounds = {}
        self._load_sounds()
        
        # Load font
        self._load_font()
        
        # Show instructions at start
        self.show_instructions = True
        
        # Create initial ball and position it
        self.create_ball(is_original=True)
        self._position_ball_on_paddle()
        
        # Load first level
        self._load_level_bricks(self.level)
    
    def _create_stars(self, count: int) -> List[Tuple[int, int, int, float]]:
        """Create a starfield background"""
        stars = []
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.uniform(0.5, 1.0)
            stars.append((x, y, size, brightness))
        return stars
    
    def _create_meteors(self, count: int) -> List[Dict]:
        """Create meteors for animated background"""
        meteors = []
        for _ in range(count):
            # Start meteors off-screen
            x = random.randint(-100, SCREEN_WIDTH + 100)
            y = random.randint(-100, -20)
            size = random.randint(2, 8)
            speed = random.uniform(METEOR_SPEED_MIN, METEOR_SPEED_MAX)
            angle = random.uniform(math.pi/4, math.pi*3/4)  # Downward trajectory
            meteors.append({
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'angle': angle,
                'trail': []
            })
        return meteors
    
    def _create_nebulas(self, count: int) -> List[Dict]:
        """Create nebula clouds for background"""
        nebulas = []
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(100, 300)
            color = random.choice([
                (30, 0, 60, 30),   # Purple
                (0, 30, 60, 30),   # Blue
                (60, 20, 0, 30)    # Orange
            ])
            drift_x = random.uniform(-NEBULA_DRIFT_SPEED, NEBULA_DRIFT_SPEED)
            drift_y = random.uniform(-NEBULA_DRIFT_SPEED, NEBULA_DRIFT_SPEED)
            nebulas.append({
                'x': x,
                'y': y,
                'size': size,
                'color': color,
                'drift_x': drift_x,
                'drift_y': drift_y,
                'points': self._generate_nebula_points(size)
            })
        return nebulas
    
    def _generate_nebula_points(self, size: int) -> List[Tuple[float, float]]:
        """Generate points for a nebula cloud"""
        points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            distance = size * 0.5 * random.uniform(0.7, 1.3)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            points.append((x, y))
        return points
    
    def _load_sounds(self) -> None:
        """Load game sound effects"""
        # Check if mixer is initialized
        if not pygame.mixer.get_init():
            print("Sound system not available. Running without sound.")
            return
            
        for name, file in SOUNDS.items():
            try:
                # Use absolute path from project root
                sound_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sounds', file)
                if os.path.exists(sound_path):
                    self.sounds[name] = pygame.mixer.Sound(sound_path)
                else:
                    print(f"Warning: Sound file not found: {sound_path}")
            except pygame.error as e:
                print(f"Warning: Could not load sound {file}: {e}")
    
    def _load_font(self) -> None:
        """Load game font"""
        try:
            # Use absolute path from project root
            font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'fonts', FONT_NAME)
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, FONT_SIZE)
            else:
                print(f"Warning: Font file not found: {font_path}")
                self.font = pygame.font.Font(None, FONT_SIZE)
        except (pygame.error, FileNotFoundError) as e:
            # Fallback to default font
            print(f"Warning: Could not load font: {e}")
            self.font = pygame.font.Font(None, FONT_SIZE)
    
    def create_ball(self, x: int = None, y: int = None, is_original: bool = False) -> Ball:
        """Create a new ball and add it to the balls group"""
        ball = Ball(x, y)
        self.balls.add(ball)
        
        # If this is the original ball, track it
        if is_original:
            self.original_ball = ball
            
        return ball
    
    def _position_ball_on_paddle(self) -> None:
        """Position the ball on the paddle"""
        if len(self.balls.sprites()) > 0 and self.paddle:
            for ball in self.balls:
                if not ball.is_active:  # Only position inactive balls
                    ball.rect.centerx = self.paddle.rect.centerx
                    ball.rect.bottom = self.paddle.rect.top
    
    def _load_level_bricks(self, level_index: int) -> None:
        """Load bricks for a level from JSON file"""
        if level_index >= len(LEVEL_FILES):
            # Game completed - show victory screen
            self.level_complete = True
            return
            
        # Clear existing bricks
        self.bricks.empty()
        
        try:
            # Load level data from JSON file with absolute path
            level_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), LEVEL_FILES[level_index])
            if not os.path.exists(level_path):
                print(f"Warning: Level file not found: {level_path}")
                self._create_default_level()
                return
                
            with open(level_path, 'r') as f:
                level_data = json.load(f)
                
            # Create bricks based on layout
            layout = level_data.get('layout', [])
            
            # Calculate the total width of the level
            max_row_length = max(len(row) for row in layout)
            level_width = max_row_length * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING
            
            # Calculate the starting x position to center the level
            start_x = (SCREEN_WIDTH - level_width) // 2
            
            for row_idx, row in enumerate(layout):
                for col_idx, brick_type in enumerate(row):
                    if brick_type.strip():  # Skip empty spaces
                        x = start_x + col_idx * (BRICK_WIDTH + BRICK_PADDING)
                        y = row_idx * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_PADDING + 50
                        if brick_type in BRICK_TYPES:
                            brick = Brick(x, y, brick_type)
                            self.bricks.add(brick)
                        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading level {level_index}: {e}")
            # Create a default level if loading fails
            self._create_default_level()
    
    def _create_default_level(self) -> None:
        """Create a default level if loading fails"""
        # Calculate the total width of the level
        level_width = BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING
        
        # Calculate the starting x position to center the level
        start_x = (SCREEN_WIDTH - level_width) // 2
        
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y = row * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_PADDING + 50
                brick_type = str(row + 1)  # Use row number + 1 for brick type (1-5)
                if brick_type in BRICK_TYPES:
                    brick = Brick(x, y, brick_type)
                    self.bricks.add(brick)
    
    def _add_particles(self, x: int, y: int, color: Tuple[int, int, int], count: int = 10) -> None:
        """Add particle effects at the given position"""
        for _ in range(count):
            # Random velocity
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size and lifetime
            size = random.randint(2, 5)
            lifetime = random.randint(20, 40)
            
            # Add particle
            self.particles.append({
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'size': size,
                'color': color,
                'lifetime': lifetime
            })
    
    def _update_particles(self) -> None:
        """Update particle effects"""
        # Update existing particles
        for particle in self.particles[:]:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity
            particle['vy'] += 0.05
            
            # Decrease lifetime
            particle['lifetime'] -= 1
            
            # Remove if lifetime is over
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def _draw_particles(self) -> None:
        """Draw particle effects"""
        for particle in self.particles:
            # Calculate alpha based on remaining lifetime
            alpha = int(255 * (particle['lifetime'] / 40))
            
            # Create a surface with alpha
            surf = pygame.Surface((particle['size'], particle['size']))
            surf.set_alpha(alpha)
            surf.fill(particle['color'])
            
            # Draw the particle
            self.screen.blit(surf, (particle['x'] - particle['size'] // 2, 
                                   particle['y'] - particle['size'] // 2))
    
    def _draw_starfield(self) -> None:
        """Draw the starfield background"""
        for x, y, size, brightness in self.background_stars:
            # Twinkle effect
            current_brightness = brightness * (0.8 + 0.2 * math.sin(time.time() * 2 + x * y))
            color = (int(255 * current_brightness),) * 3  # White with varying brightness
            pygame.draw.circle(self.screen, color, (x, y), size)
    
    def _apply_screen_shake(self) -> None:
        """Apply screen shake effect"""
        if self.shake_amount > 0:
            # Decrease shake amount over time
            current_time = pygame.time.get_ticks()
            if current_time > self.shake_time:
                self.shake_amount = 0
            else:
                # Calculate shake offset
                dx = random.randint(-self.shake_amount, self.shake_amount)
                dy = random.randint(-self.shake_amount, self.shake_amount)
                
                # Create a copy of the screen
                screen_copy = self.screen.copy()
                
                # Clear the screen
                self.screen.fill(BG_COLOR)
                
                # Draw the copy with offset
                self.screen.blit(screen_copy, (dx, dy))
    
    def update(self) -> None:
        """Update game state"""
        # Don't update if paused, game over, or showing instructions
        if self.paused or self.show_instructions:
            return
            
        if self.game_over:
            # Only handle rendering when game is over
            return
            
        # Update paddle
        self.paddle.update()
        
        # Update ball positions on paddle if not active
        self._position_ball_on_paddle()
        
        # Check if any balls are active
        any_active_balls = False
        original_ball_active = False
        
        # Update balls
        for ball in self.balls:
            # Update ball position
            wall_collision = ball.update(self.paddle)
            
            # Check for wall collision sound
            if wall_collision and 'bounce' in self.sounds:
                self._play_sound('bounce')
            
            # Check for paddle collision
            if ball.check_paddle_collision(self.paddle) and 'bounce' in self.sounds:
                self._play_sound('bounce')
                # Add particles for visual effect
                self._add_particles(ball.rect.centerx, ball.rect.bottom, WHITE, 5)
            
            # Check for brick collisions
            for brick in self.bricks:
                if ball.check_brick_collision(brick):
                    if brick.is_breakable:
                        if brick.hit():
                            # Brick broken
                            self.score += brick.points
                            self.bricks.remove(brick)
                            
                            # Visual effects
                            self._add_particles(brick.rect.centerx, brick.rect.centery, 
                                              brick.brick_type.color, 15)
                            self.shake_amount = 3
                            self.shake_time = pygame.time.get_ticks() + 100
                            
                            # Play sound
                            self._play_sound('brick_break')
                            
                            # Chance to spawn power-up
                            if random.random() < POWERUP_DROP_CHANCE:
                                self._spawn_powerup(brick.rect.centerx, brick.rect.centery)
                        else:
                            # Brick hit but not broken
                            self._play_sound('bounce')
                            # Add fewer particles for a hit
                            self._add_particles(brick.rect.centerx, brick.rect.centery, 
                                              brick.brick_type.color, 5)
                    else:
                        # Unbreakable brick
                        self._play_sound('bounce')
            
            # Check if ball is below screen
            if ball.rect.top > SCREEN_HEIGHT:
                # Only count as a lost ball if it was active
                if ball.is_active:
                    # Remove the ball
                    self.balls.remove(ball)
                    
                    # Track if this was the original ball
                    if ball == self.original_ball:
                        self.original_ball = None
            else:
                if ball.is_active:
                    any_active_balls = True
                    if ball == self.original_ball:
                        original_ball_active = True
        
        # Check if all balls are lost
        if len(self.balls) == 0:
            # Only lose a life when all balls are gone
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self._play_sound('game_over')
                # Add lots of particles for game over
                for _ in range(5):
                    self._add_particles(random.randint(0, SCREEN_WIDTH),
                                      random.randint(0, SCREEN_HEIGHT),
                                      (255, 100, 100), 20)
            else:
                # Create a new original ball if we still have lives
                self.original_ball = self.create_ball(is_original=True)
                self._position_ball_on_paddle()
        
        # Update power-ups
        for powerup in self.powerups:
            powerup.update()
            
            # Check for paddle collision
            if powerup.rect.colliderect(self.paddle.rect):
                self._apply_powerup(powerup.type)
                self.powerups.remove(powerup)
                self._play_sound('powerup')
                # Add particles for power-up collection
                self._add_particles(powerup.rect.centerx, powerup.rect.centery, 
                                  powerup.color, 15)
            
            # Remove if below screen
            if powerup.rect.top > SCREEN_HEIGHT:
                self.powerups.remove(powerup)
        
        # Update particles
        self._update_particles()
        
        # Check for level completion
        if len(self.bricks) == 0 or all(not brick.is_breakable for brick in self.bricks):
            self.level_complete = True
            self._play_sound('level_complete')
    
    def _play_sound(self, sound_name: str) -> None:
        """Play a sound if available"""
        if sound_name in self.sounds and pygame.mixer.get_init():
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Silently fail if sound can't be played
    
    def _spawn_powerup(self, x: int, y: int) -> None:
        """Spawn a random power-up at the given position"""
        # Choose a random power-up type based on relative chances
        powerup_types = list(POWERUPS.keys())
        powerup_chances = [POWERUPS[p].chance for p in powerup_types]
        
        # Normalize chances
        total_chance = sum(powerup_chances)
        if total_chance > 0:
            normalized_chances = [c / total_chance for c in powerup_chances]
            powerup_type = random.choices(powerup_types, weights=normalized_chances, k=1)[0]
            
            # Create and add the power-up
            powerup = PowerUp(x, y, powerup_type)
            self.powerups.add(powerup)
    
    def _apply_powerup(self, powerup_type: str) -> None:
        """Apply a power-up effect"""
        if powerup_type == "WIDE" or powerup_type == "STICKY":
            self.paddle.apply_powerup(powerup_type)
        elif powerup_type == "MULTI":
            # Create two additional balls
            for _ in range(2):
                if self.balls:
                    # Get position of an existing ball
                    existing_ball = self.balls.sprites()[0]
                    new_ball = Ball(existing_ball.rect.centerx, existing_ball.rect.centery)
                    new_ball.is_active = True
                    self.balls.add(new_ball)
        elif powerup_type == "SLOW":
            # Apply slow-motion to all balls
            for ball in self.balls:
                ball.apply_powerup(powerup_type)
    
    def render(self) -> None:
        """Render game objects"""
        # Draw background
        self.screen.fill(BG_COLOR)
        self._draw_starfield()
        
        # Draw paddle with shadow
        shadow_surf = pygame.Surface((self.paddle.width, self.paddle.height))
        shadow_surf.fill(BLACK)
        shadow_surf.set_alpha(100)
        self.screen.blit(shadow_surf, (self.paddle.rect.x + 5, self.paddle.rect.y + 5))
        self.paddle.draw(self.screen)
        
        # Draw balls with glow effect
        for ball in self.balls:
            ball.draw(self.screen)
        
        # Draw bricks with shadow
        for brick in self.bricks:
            # Draw shadow
            shadow_surf = pygame.Surface((brick.width, brick.height))
            shadow_surf.fill(BLACK)
            shadow_surf.set_alpha(50)
            self.screen.blit(shadow_surf, (brick.rect.x + 3, brick.rect.y + 3))
            brick.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw particles
        self._draw_particles()
        
        # Draw HUD
        self._draw_hud()
        
        # Draw game state screens
        if self.show_instructions:
            self._draw_instructions()
        elif self.game_over:
            self._draw_game_over()
        elif self.level_complete:
            self._draw_level_complete()
        
        # Apply screen shake
        self._apply_screen_shake()
    
    def _draw_hud(self) -> None:
        """Draw heads-up display (score, lives)"""
        # Draw score with shadow
        score_text = f"SCORE: {self.score}"
        shadow_surf = self.font.render(score_text, True, BLACK)
        score_surf = self.font.render(score_text, True, WHITE)
        self.screen.blit(shadow_surf, (22, 22))
        self.screen.blit(score_surf, (20, 20))
        
        # Draw lives (ensure it's never negative)
        lives_display = max(0, self.lives)
        lives_text = f"LIVES: {lives_display}"
        shadow_surf = self.font.render(lives_text, True, BLACK)
        lives_surf = self.font.render(lives_text, True, WHITE)
        self.screen.blit(shadow_surf, (SCREEN_WIDTH - lives_surf.get_width() - 18, 22))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 20, 20))
        
        # Draw level
        level_text = f"LEVEL: {self.level + 1}"
        shadow_surf = self.font.render(level_text, True, BLACK)
        level_surf = self.font.render(level_text, True, WHITE)
        self.screen.blit(shadow_surf, (SCREEN_WIDTH // 2 - level_surf.get_width() // 2 + 2, 22))
        self.screen.blit(level_surf, (SCREEN_WIDTH // 2 - level_surf.get_width() // 2, 20))
    
    def _draw_game_over(self) -> None:
        """Draw game over message"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text with glow
        game_over_text = "GAME OVER"
        
        # Draw glow
        for i in range(5, 0, -1):
            glow_surf = self.font.render(game_over_text, True, (128, 0, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            glow_surf.set_alpha(50)
            self.screen.blit(glow_surf, (glow_rect.x - i, glow_rect.y - i))
        
        # Draw main text
        game_over_surf = self.font.render(game_over_text, True, (255, 100, 100))
        game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(game_over_surf, game_over_rect)
        
        # Draw restart text with animation
        restart_text = "Press R to restart"
        restart_surf = self.font.render(restart_text, True, WHITE)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        
        # Pulsating effect
        scale = 1.0 + 0.1 * math.sin(time.time() * 4)
        scaled_width = int(restart_surf.get_width() * scale)
        scaled_height = int(restart_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(restart_surf, (scaled_width, scaled_height))
        scaled_rect = scaled_surf.get_rect(center=restart_rect.center)
        
        self.screen.blit(scaled_surf, scaled_rect)
    
    def _draw_level_complete(self) -> None:
        """Draw level complete message"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Draw level complete text with glow
        level_complete_text = "LEVEL COMPLETE!"
        
        # Draw glow
        for i in range(5, 0, -1):
            glow_surf = self.font.render(level_complete_text, True, (0, 128, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            glow_surf.set_alpha(50)
            self.screen.blit(glow_surf, (glow_rect.x - i, glow_rect.y - i))
        
        # Draw main text
        level_complete_surf = self.font.render(level_complete_text, True, (100, 255, 100))
        level_complete_rect = level_complete_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(level_complete_surf, level_complete_rect)
        
        # Draw next level text with animation
        next_text = "Press SPACE to continue"
        next_surf = self.font.render(next_text, True, WHITE)
        next_rect = next_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        
        # Pulsating effect
        scale = 1.0 + 0.1 * math.sin(time.time() * 4)
        scaled_width = int(next_surf.get_width() * scale)
        scaled_height = int(next_surf.get_height() * scale)
        scaled_surf = pygame.transform.scale(next_surf, (scaled_width, scaled_height))
        scaled_rect = scaled_surf.get_rect(center=next_rect.center)
        
        self.screen.blit(scaled_surf, scaled_rect)
    
    def _draw_instructions(self) -> None:
        """Draw game instructions"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Draw title with glow
        title_text = "BRICK BREAKER"
        
        # Draw glow
        for i in range(5, 0, -1):
            glow_surf = self.font.render(title_text, True, (128, 128, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            glow_surf.set_alpha(50)
            self.screen.blit(glow_surf, (glow_rect.x - i, glow_rect.y - i))
        
        # Draw main title
        title_surf = self.font.render(title_text, True, (255, 255, 100))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_surf, title_rect)
        
        # Draw instructions
        instructions = [
            "Use LEFT/RIGHT arrows to move paddle",
            "Press SPACE to launch ball",
            "Break all bricks to complete the level",
            "",
            "Press SPACE to start"
        ]
        
        for i, line in enumerate(instructions):
            text_surf = self.font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30 + i * 30))
            
            # Add shadow
            shadow_surf = self.font.render(line, True, BLACK)
            shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT // 2 - 30 + i * 30 + 2))
            self.screen.blit(shadow_surf, shadow_rect)
            
            self.screen.blit(text_surf, text_rect)
        
        # Draw animated "Press SPACE" text
        if instructions[-1] == "Press SPACE to start":
            space_surf = self.font.render(instructions[-1], True, WHITE)
            space_rect = space_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30 + (len(instructions) - 1) * 30))
            
            # Pulsating effect
            scale = 1.0 + 0.1 * math.sin(time.time() * 4)
            scaled_width = int(space_surf.get_width() * scale)
            scaled_height = int(space_surf.get_height() * scale)
            scaled_surf = pygame.transform.scale(space_surf, (scaled_width, scaled_height))
            scaled_rect = scaled_surf.get_rect(center=space_rect.center)
            
            self.screen.blit(scaled_surf, scaled_rect)
    
    def handle_events(self, event: pygame.event.Event) -> None:
        """Handle game events"""
        if event.type == pygame.KEYDOWN:
            # Show instructions screen
            if self.show_instructions and event.key == pygame.K_SPACE:
                self.show_instructions = False
                return
                
            # Launch ball with space
            if event.key == pygame.K_SPACE:
                if self.level_complete:
                    self.next_level()
                else:
                    for ball in self.balls:
                        ball.launch()
            
            # Pause game with P
            elif event.key == pygame.K_p:
                self.paused = not self.paused
            
            # Restart game with R
            elif event.key == pygame.K_r:
                self.reset()
    
    def next_level(self) -> None:
        """Advance to the next level"""
        self.level += 1
        if self.level >= len(LEVEL_FILES):
            # Game completed
            self.level = 0  # Start over with level 1
        
        # Reset level state
        self.level_complete = False
        self.powerups.empty()
        self.particles = []
        self.ball_was_active = False
        
        # Reset balls
        self.balls.empty()
        self.original_ball = self.create_ball(is_original=True)
        self._position_ball_on_paddle()
        
        # Load new level bricks
        self._load_level_bricks(self.level)
    
    def reset(self) -> None:
        """Reset the game state"""
        # Reset game state
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 0
        self.game_over = False
        self.level_complete = False
        self.show_instructions = False  # Skip instructions on restart
        self.paused = False
        self.ball_was_active = False
        self.particles = []
        self.shake_amount = 0
        
        # Reset game objects
        self.paddle = Paddle()
        self.balls.empty()
        self.powerups.empty()
        
        # Create a new ball
        self.original_ball = self.create_ball(is_original=True)
        self._position_ball_on_paddle()
        
        # Load the first level bricks
        self._load_level_bricks(self.level)
