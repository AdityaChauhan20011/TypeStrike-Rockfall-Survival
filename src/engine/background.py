"""
Dynamic Parallax Background and Visual Atmosphere for TypeStrike
Renders multi-layered starfields, distant volcanic mountain peaks,
animated perspective cyber grid floor, floating embers, and screen-shake offsets.
"""

import math
import random
from typing import List, Tuple
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG_DARK, COLOR_ACCENT_CYAN, COLOR_ACCENT_MAGENTA


class Star:
    def __init__(self, x: float, y: float, speed: float, radius: float, brightness: float):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.brightness = brightness
        self.twinkle_speed = random.uniform(1.5, 4.0)

    def update(self, dt: float):
        self.y += self.speed * dt
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.uniform(0, SCREEN_WIDTH)


class Ember:
    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(SCREEN_HEIGHT - 120, SCREEN_HEIGHT)
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(-35, -90)
        self.life = random.uniform(2.0, 5.0)
        self.max_life = self.life
        self.radius = random.uniform(1.0, 2.5)

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or self.y < 0:
            self.__init__()


class Background:
    """Manages parallax atmospheric rendering and screen shake."""

    def __init__(self):
        # 1. Star layers
        self.stars: List[Star] = []
        for _ in range(70):
            # Slow distant stars
            self.stars.append(Star(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT), random.uniform(10, 25), 1.2, random.uniform(0.4, 0.8)))
        for _ in range(40):
            # Faster medium stars
            self.stars.append(Star(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT), random.uniform(35, 75), 1.8, random.uniform(0.7, 1.0)))

        # 2. Floating embers
        self.embers: List[Ember] = [Ember() for _ in range(25)]

        # 3. Ground perspective cyber grid
        self.grid_offset_y = 0.0
        self.ground_y = SCREEN_HEIGHT - 90

        # 4. Screen shake
        self.shake_magnitude = 0.0
        self.shake_duration = 0.0
        self.shake_offset = (0, 0)

        # 5. Damage vignette flash
        self.damage_flash_timer = 0.0

    def trigger_shake(self, magnitude: float = 8.0, duration: float = 0.3):
        """Applies dynamic camera screen shake."""
        self.shake_magnitude = max(self.shake_magnitude, magnitude)
        self.shake_duration = max(self.shake_duration, duration)

    def trigger_damage_flash(self, duration: float = 0.35):
        self.damage_flash_timer = duration

    def update(self, dt: float, game_speed: float = 1.0):
        # Update stars
        for star in self.stars:
            star.update(dt * game_speed)

        # Update embers
        for ember in self.embers:
            ember.update(dt)

        # Scroll cyber grid
        self.grid_offset_y = (self.grid_offset_y + 60.0 * dt * game_speed) % 40.0

        # Update damage flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)

        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            decay = self.shake_duration / max(0.01, self.shake_duration + dt)
            self.shake_magnitude *= decay
            self.shake_offset = (
                random.uniform(-self.shake_magnitude, self.shake_magnitude),
                random.uniform(-self.shake_magnitude, self.shake_magnitude),
            )
            if self.shake_duration <= 0:
                self.shake_magnitude = 0.0
                self.shake_offset = (0, 0)
        else:
            self.shake_offset = (0, 0)

    def render(self, surface: pygame.Surface):
        # Base deep space background
        surface.fill(COLOR_BG_DARK)

        # Draw stars
        t = pygame.time.get_ticks() / 1000.0
        for star in self.stars:
            twinkle = 0.7 + 0.3 * math.sin(t * star.twinkle_speed + star.x)
            alpha = int(255 * star.brightness * twinkle)
            color = (int(200 * twinkle), int(220 * twinkle), int(255 * twinkle))
            pygame.draw.circle(surface, color, (int(star.x), int(star.y)), int(star.radius))

        # Distant mountain silhouettes
        self._render_distant_mountains(surface)

        # Perspective cyber-grid on ground
        self._render_cyber_grid(surface)

        # Floating embers
        for ember in self.embers:
            alpha = max(0, min(255, int(255 * (ember.life / ember.max_life))))
            ember_col = (255, int(120 + 80 * (ember.life / ember.max_life)), 40)
            pygame.draw.circle(surface, ember_col, (int(ember.x), int(ember.y)), int(ember.radius))

        # Damage vignette red flash
        if self.damage_flash_timer > 0:
            vig_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(140 * (self.damage_flash_timer / 0.35))
            vig_surf.fill((255, 20, 40, alpha))
            surface.blit(vig_surf, (0, 0))

    def _render_distant_mountains(self, surface: pygame.Surface):
        """Draws layered mountain silhouettes on the horizon."""
        horizon_y = self.ground_y - 30
        
        # Back mountain layer (dark violet-gray)
        pts_back = [
            (0, horizon_y),
            (140, horizon_y - 80),
            (320, horizon_y - 45),
            (560, horizon_y - 110),
            (780, horizon_y - 65),
            (1020, horizon_y - 95),
            (1280, horizon_y - 50),
            (1280, horizon_y),
        ]
        pygame.draw.polygon(surface, (16, 20, 36), pts_back)

        # Front mountain ridge (dark cyan-gray)
        pts_front = [
            (0, horizon_y),
            (210, horizon_y - 55),
            (440, horizon_y - 30),
            (690, horizon_y - 70),
            (930, horizon_y - 40),
            (1150, horizon_y - 60),
            (1280, horizon_y - 35),
            (1280, horizon_y),
        ]
        pygame.draw.polygon(surface, (22, 28, 48), pts_front)

    def _render_cyber_grid(self, surface: pygame.Surface):
        """Draws an animated retro-futuristic perspective ground grid."""
        ground_top = self.ground_y
        ground_h = SCREEN_HEIGHT - ground_top
        grid_surf = pygame.Surface((SCREEN_WIDTH, ground_h), pygame.SRCALPHA)

        # Base floor fill
        pygame.draw.rect(grid_surf, (14, 18, 30), (0, 0, SCREEN_WIDTH, ground_h))
        
        # Horizon neon dividing line
        pygame.draw.line(grid_surf, COLOR_ACCENT_CYAN, (0, 0), (SCREEN_WIDTH, 0), 2)

        # Horizontal perspective grid lines
        num_h_lines = 7
        for i in range(num_h_lines):
            # Exponential spacing for perspective depth
            factor = (i + (self.grid_offset_y / 40.0)) / num_h_lines
            line_y = int((factor ** 2.2) * ground_h)
            alpha = int(40 + 160 * (line_y / ground_h))
            col = (*COLOR_ACCENT_CYAN[:3], alpha)
            pygame.draw.line(grid_surf, col, (0, line_y), (SCREEN_WIDTH, line_y), 1)

        # Converging perspective vertical lines towards horizon center
        vanishing_x = SCREEN_WIDTH // 2
        vanishing_y = -30
        for x_floor in range(-200, SCREEN_WIDTH + 300, 70):
            col = (*COLOR_ACCENT_CYAN[:3], 45)
            pygame.draw.line(grid_surf, col, (vanishing_x, vanishing_y), (x_floor, ground_h), 1)

        surface.blit(grid_surf, (0, ground_top))
