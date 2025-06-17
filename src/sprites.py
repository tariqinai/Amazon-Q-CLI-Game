"""
Game sprites (Paddle, Ball, Brick, PowerUp)
"""
import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from settings import *

def draw_rounded_rect(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], 
                     corner_radius: int) -> None:
    """Draw a rounded rectangle"""
    if corner_radius <= 0:
        pygame.draw.rect(surface, color, rect)
        return
        
    # Draw main rectangle
    pygame.draw.rect(surface, color, rect.inflate(-corner_radius*2, -corner_radius*2))
    
    # Draw four corner circles
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.bottom - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius, rect.bottom - corner_radius), corner_radius)
    
    # Draw four connecting rectangles
    pygame.draw.rect(surface, color, pygame.Rect(rect.left + corner_radius, rect.top, 
                                               rect.width - corner_radius*2, corner_radius))
    pygame.draw.rect(surface, color, pygame.Rect(rect.left + corner_radius, rect.bottom - corner_radius, 
                                               rect.width - corner_radius*2, corner_radius))
    pygame.draw.rect(surface, color, pygame.Rect(rect.left, rect.top + corner_radius, 
                                               corner_radius, rect.height - corner_radius*2))
    pygame.draw.rect(surface, color, pygame.Rect(rect.right - corner_radius, rect.top + corner_radius, 
                                               corner_radius, rect.height - corner_radius*2))

class Paddle(pygame.sprite.Sprite):
    def __init__(self) -> None:
        """Initialize the paddle"""
        super().__init__()
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PADDLE_SPEED
        self.velocity = 0
        
        # Power-up states
        self.is_wide = False
        self.is_sticky = False
        self.wide_timer = 0
        self.sticky_timer = 0
    
    def update(self) -> None:
        """Update paddle position based on keyboard input"""
        keys = pygame.key.get_pressed()
        self.velocity = 0
        
        if keys[pygame.K_LEFT]:
            self.velocity = -self.speed
            # Apply acceleration for smoother movement
            if self.velocity > -self.speed:
                self.velocity -= 0.5
        if keys[pygame.K_RIGHT]:
            self.velocity = self.speed
            # Apply acceleration for smoother movement
            if self.velocity < self.speed:
                self.velocity += 0.5
            
        # Update position
        self.rect.x += self.velocity
        
        # Keep paddle on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Handle power-up timers
        current_time = pygame.time.get_ticks()
        
        # Wide paddle timer
        if self.is_wide and current_time > self.wide_timer:
            self.is_wide = False
            self.width = PADDLE_WIDTH
            self._resize_paddle()
            
        # Sticky paddle timer
        if self.is_sticky and current_time > self.sticky_timer:
            self.is_sticky = False
    
    def apply_powerup(self, powerup_type: str) -> None:
        """Apply a power-up effect to the paddle"""
        current_time = pygame.time.get_ticks()
        
        if powerup_type == "WIDE":
            self.is_wide = True
            self.wide_timer = current_time + POWERUP_DURATION["WIDE"]
            self.width = WIDE_PADDLE_WIDTH
            self._resize_paddle()
            
        elif powerup_type == "STICKY":
            self.is_sticky = True
            self.sticky_timer = current_time + POWERUP_DURATION["STICKY"]
    
    def _resize_paddle(self) -> None:
        """Resize the paddle while maintaining position"""
        center = self.rect.centerx
        bottom = self.rect.bottom
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = center
        self.rect.bottom = bottom
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the paddle"""
        # Draw paddle with rounded corners
        draw_rounded_rect(surface, self.rect, WHITE, 5)


class Ball(pygame.sprite.Sprite):
    def __init__(self, x: int = None, y: int = None) -> None:
        """Initialize the ball"""
        super().__init__()
        self.radius = BALL_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        
        # Position
        if x is None or y is None:
            self.rect.centerx = SCREEN_WIDTH // 2
            self.rect.centery = SCREEN_HEIGHT // 2
        else:
            self.rect.centerx = x
            self.rect.centery = y
            
        # Speed and direction
        self.speed = BALL_SPEED
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = -self.speed
        
        # State
        self.is_active = False
        self.is_stuck = False
        self.stick_offset = 0
        self.is_slow = False
        self.slow_timer = 0
        
        # Trail effect
        self.trail = []
        self.trail_length = 5
    
    def update(self, paddle: Paddle = None) -> None:
        """Update ball position and handle collisions"""
        # Store position for trail effect if active
        if self.is_active:
            self.trail.append((self.rect.centerx, self.rect.centery))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
                
        # Handle slow-motion timer
        current_time = pygame.time.get_ticks()
        if self.is_slow and current_time > self.slow_timer:
            self.is_slow = False
            self.speed = BALL_SPEED
            self._adjust_velocity()
        
        # If ball is stuck to paddle, update position with paddle
        if self.is_stuck and paddle:
            self.rect.centerx = paddle.rect.centerx + self.stick_offset
            self.rect.bottom = paddle.rect.top
            return
            
        # If ball is not active, don't move
        if not self.is_active:
            return
            
        # Calculate actual speed (considering slow-motion)
        actual_speed = self.speed * 0.5 if self.is_slow else self.speed
        
        # Move the ball
        self.rect.x += self.dx * (actual_speed / BALL_SPEED)
        self.rect.y += self.dy * (actual_speed / BALL_SPEED)
        
        # Wall collision
        if self.rect.left <= 0:
            self.rect.left = 0
            self.dx = abs(self.dx)
            return True  # Collision occurred
            
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.dx = -abs(self.dx)
            return True  # Collision occurred
            
        if self.rect.top <= 0:
            self.rect.top = 0
            self.dy = abs(self.dy)
            return True  # Collision occurred
            
        return False  # No collision
    
    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Check for collision with paddle and update direction"""
        if self.rect.colliderect(paddle.rect) and self.dy > 0:
            # Calculate reflection angle based on where ball hit the paddle
            # Center of paddle = straight up, edges = sharper angle
            relative_x = (self.rect.centerx - paddle.rect.centerx) / (paddle.width / 2)
            # Limit the angle to avoid too horizontal bounces
            relative_x = max(-0.8, min(0.8, relative_x))
            
            # Calculate new direction
            angle = relative_x * (math.pi / 3)  # Max 60 degrees
            self.dx = math.sin(angle) * self.speed
            self.dy = -math.cos(angle) * self.speed
            
            # Position ball above paddle to prevent multiple collisions
            self.rect.bottom = paddle.rect.top - 1
            
            # Handle sticky paddle
            if paddle.is_sticky:
                self.is_stuck = True
                self.stick_offset = self.rect.centerx - paddle.rect.centerx
                
            return True
        return False
    
    def check_brick_collision(self, brick: 'Brick') -> bool:
        """Check for collision with brick and update direction"""
        if not self.rect.colliderect(brick.rect):
            return False
            
        # Determine which side of the brick was hit
        # Calculate distances from ball center to brick edges
        left_dist = abs(self.rect.right - brick.rect.left)
        right_dist = abs(self.rect.left - brick.rect.right)
        top_dist = abs(self.rect.bottom - brick.rect.top)
        bottom_dist = abs(self.rect.top - brick.rect.bottom)
        
        # Find the minimum distance to determine collision side
        min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
        
        # Adjust ball direction based on collision side
        if min_dist == left_dist:
            self.dx = -abs(self.dx)  # Hit from right, bounce left
            self.rect.right = brick.rect.left - 1
        elif min_dist == right_dist:
            self.dx = abs(self.dx)  # Hit from left, bounce right
            self.rect.left = brick.rect.right + 1
        elif min_dist == top_dist:
            self.dy = -abs(self.dy)  # Hit from bottom, bounce up
            self.rect.bottom = brick.rect.top - 1
        elif min_dist == bottom_dist:
            self.dy = abs(self.dy)  # Hit from top, bounce down
            self.rect.top = brick.rect.bottom + 1
            
        return True
    
    def launch(self) -> None:
        """Launch the ball if it's stuck or inactive"""
        if self.is_stuck or not self.is_active:
            self.is_stuck = False
            self.is_active = True
            # Set initial direction slightly randomized
            angle = random.uniform(-math.pi/4, math.pi/4)  # -45 to 45 degrees
            self.dx = math.sin(angle) * self.speed
            self.dy = -math.cos(angle) * self.speed
    
    def apply_powerup(self, powerup_type: str) -> None:
        """Apply a power-up effect to the ball"""
        current_time = pygame.time.get_ticks()
        
        if powerup_type == "SLOW":
            self.is_slow = True
            self.slow_timer = current_time + POWERUP_DURATION["SLOW"]
    
    def _adjust_velocity(self) -> None:
        """Adjust velocity to maintain direction but change speed"""
        if self.dx == 0 and self.dy == 0:
            return
            
        # Calculate current direction
        magnitude = math.sqrt(self.dx**2 + self.dy**2)
        if magnitude == 0:
            return
            
        # Normalize and scale to new speed
        self.dx = (self.dx / magnitude) * self.speed
        self.dy = (self.dy / magnitude) * self.speed
    
    def reset(self, x: int = None, y: int = None) -> None:
        """Reset the ball to initial state"""
        if x is None or y is None:
            self.rect.centerx = SCREEN_WIDTH // 2
            self.rect.centery = SCREEN_HEIGHT // 2
        else:
            self.rect.centerx = x
            self.rect.centery = y
            
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = -self.speed
        self.is_active = False
        self.is_stuck = False
        self.is_slow = False
        self.trail = []
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ball with trail effect"""
        # Draw trail
        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / (self.trail_length + 1))
            size = int(self.radius * (i + 1) / (self.trail_length + 1))
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (255, 255, 255, alpha), (size, size), size)
            surface.blit(trail_surf, (x - size, y - size))
            
        # Draw ball with glow effect
        glow_radius = self.radius * 1.5
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 255, 100), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))
        
        # Draw main ball
        pygame.draw.circle(surface, WHITE, self.rect.center, self.radius)


class Brick(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, brick_type: str) -> None:
        """Initialize a brick"""
        super().__init__()
        self.brick_type = BRICK_TYPES[brick_type]
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hits_left = self.brick_type.hits
        self.points = self.brick_type.points
        self.is_breakable = self.hits_left > 0
        self._draw_brick()
    
    def _draw_brick(self) -> None:
        """Draw the brick with a 3D effect"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw main brick with rounded corners
        draw_rounded_rect(self.image, pygame.Rect(0, 0, self.width, self.height), 
                         self.brick_type.color, BRICK_CORNER_RADIUS)
        
        # Add 3D effect
        # Top and left edges (lighter)
        pygame.draw.line(self.image, self.brick_type.highlight_color, 
                       (BRICK_CORNER_RADIUS, 2), (self.width - BRICK_CORNER_RADIUS, 2), 2)
        pygame.draw.line(self.image, self.brick_type.highlight_color, 
                       (2, BRICK_CORNER_RADIUS), (2, self.height - BRICK_CORNER_RADIUS), 2)
        
        # Bottom and right edges (darker)
        pygame.draw.line(self.image, self.brick_type.edge_color, 
                       (BRICK_CORNER_RADIUS, self.height - 2), 
                       (self.width - BRICK_CORNER_RADIUS, self.height - 2), 2)
        pygame.draw.line(self.image, self.brick_type.edge_color, 
                       (self.width - 2, BRICK_CORNER_RADIUS), 
                       (self.width - 2, self.height - BRICK_CORNER_RADIUS), 2)
    
    def hit(self) -> bool:
        """Register a hit on the brick and return True if broken"""
        if not self.is_breakable:
            return False
            
        self.hits_left -= 1
        
        # Update appearance based on remaining hits
        if self.hits_left > 0:
            # Darken the brick to show damage
            darker_color = tuple(max(0, c - 50) for c in self.brick_type.color)
            self.image.fill((0, 0, 0, 0))  # Clear
            draw_rounded_rect(self.image, pygame.Rect(0, 0, self.width, self.height), 
                            darker_color, BRICK_CORNER_RADIUS)
            return False
        else:
            return True
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the brick"""
        surface.blit(self.image, self.rect)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, powerup_type: str) -> None:
        """Initialize a power-up"""
        super().__init__()
        self.type = powerup_type
        self.color = POWERUPS[powerup_type].color
        self.size = POWERUP_SIZE
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = POWERUP_SPEED
        self.angle = 0  # For rotation effect
        self._draw_powerup()
    
    def _draw_powerup(self) -> None:
        """Draw the power-up with a distinctive look"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw rounded square
        draw_rounded_rect(self.image, pygame.Rect(0, 0, self.size, self.size), 
                         self.color, 8)
        
        # Add icon based on power-up type
        if self.type == "WIDE":
            # Draw wide paddle icon
            pygame.draw.rect(self.image, WHITE, (5, self.size//2 + 2, self.size - 10, 5))
        elif self.type == "STICKY":
            # Draw sticky paddle icon
            pygame.draw.rect(self.image, WHITE, (5, self.size//2 + 5, self.size - 10, 5))
            pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2 - 5), 5)
        elif self.type == "MULTI":
            # Draw multi-ball icon
            pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2), 5)
            pygame.draw.circle(self.image, WHITE, (self.size//2 - 7, self.size//2 + 5), 4)
            pygame.draw.circle(self.image, WHITE, (self.size//2 + 7, self.size//2 + 5), 4)
        elif self.type == "SLOW":
            # Draw slow-motion icon
            pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2), 8, 2)
            pygame.draw.line(self.image, WHITE, (self.size//2, self.size//2), 
                           (self.size//2, self.size//2 - 6), 2)
            pygame.draw.line(self.image, WHITE, (self.size//2, self.size//2), 
                           (self.size//2 + 4, self.size//2), 2)
    
    def update(self) -> None:
        """Update power-up position and rotation"""
        self.rect.y += self.speed
        self.angle = (self.angle + 2) % 360
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the power-up with rotation and glow effect"""
        # Draw glow effect
        glow_radius = int(self.size * 1.5)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*self.color, 100)  # Semi-transparent color
        pygame.draw.rect(glow_surf, glow_color, 
                       (glow_radius - self.size//2, glow_radius - self.size//2, 
                        self.size, self.size), 0, 8)
        surface.blit(glow_surf, 
                   (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))
        
        # Rotate image
        rotated = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated.get_rect(center=self.rect.center)
        
        # Draw power-up
        surface.blit(rotated, rotated_rect)
