"""
Particle and Visual FX System for TypeStrike
Handles explosion fragments, smoke, sparks, laser muzzle flashes,
and animated floating score/notification texts.
"""

import math
import random
from typing import List, Tuple
import pygame
from src.config import COLOR_ACCENT_CYAN, COLOR_ACCENT_GOLD, COLOR_ACCENT_MAGENTA, COLOR_ACCENT_RED, COLOR_WHITE


class Particle:
    """A single dynamic physics particle with velocity, color fade, and lifespan."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        radius: float,
        color: Tuple[int, int, int],
        lifespan: float,
        drag: float = 0.96,
        gravity: float = 120.0,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.lifespan = lifespan
        self.max_lifespan = lifespan
        self.drag = drag
        self.gravity = gravity
        self.is_alive = True

    def update(self, dt: float):
        if not self.is_alive:
            return
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.is_alive = False
            return

        self.vx *= (self.drag ** (dt * 60))
        self.vy *= (self.drag ** (dt * 60))
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def render(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        life_ratio = max(0.0, self.lifespan / self.max_lifespan)
        curr_radius = max(1, int(self.radius * life_ratio))
        
        # Color fade / alpha
        alpha = int(255 * life_ratio)
        temp_surf = pygame.Surface((curr_radius * 2 + 2, curr_radius * 2 + 2), pygame.SRCALPHA)
        draw_color = (*self.color[:3], alpha)
        pygame.draw.circle(temp_surf, draw_color, (curr_radius + 1, curr_radius + 1), curr_radius)
        surface.blit(temp_surf, (int(self.x - curr_radius - 1), int(self.y - curr_radius - 1)))


class FloatingText:
    """Animated text popups that rise and fade out (e.g., +150, STREAK x3, SHIELD!)."""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        font: pygame.font.Font,
        lifespan: float = 1.0,
        vy: float = -45.0,
    ):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.lifespan = lifespan
        self.max_lifespan = lifespan
        self.vy = vy
        self.is_alive = True

    def update(self, dt: float):
        if not self.is_alive:
            return
        self.lifespan -= dt
        if self.lifespan <= 0:
            self.is_alive = False
            return
        self.y += self.vy * dt

    def render(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        life_ratio = max(0.0, self.lifespan / self.max_lifespan)
        alpha = int(255 * min(1.0, life_ratio * 1.5))
        
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        
        # Draw with dark drop shadow for maximum clarity
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_surf.set_alpha(int(alpha * 0.7))
        surface.blit(shadow_surf, (int(self.x - text_surf.get_width() // 2 + 2), int(self.y + 2)))
        surface.blit(text_surf, (int(self.x - text_surf.get_width() // 2), int(self.y)))


class ParticleManager:
    """Manages active particles and floating text instances."""

    def __init__(self):
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []

    def reset(self):
        self.particles.clear()
        self.floating_texts.clear()

    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.is_alive]

    def render(self, surface: pygame.Surface):
        for p in self.particles:
            p.render(surface)
        for ft in self.floating_texts:
            ft.render(surface)

    def spawn_rock_explosion(self, x: float, y: float, rock_color: Tuple[int, int, int], count: int = 24):
        """Creates a vibrant shattering explosion burst of rock fragments and glowing sparks."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 320)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(20, 80)
            radius = random.uniform(2.5, 6.0)
            color_choice = random.choice([rock_color, COLOR_ACCENT_GOLD, COLOR_WHITE, (255, 160, 40)])
            life = random.uniform(0.4, 0.9)
            self.particles.append(Particle(x, y, vx, vy, radius, color_choice, life))

    def spawn_laser_sparks(self, x: float, y: float, count: int = 12):
        """High-energy sparks at point of laser impact."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(120, 380)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            radius = random.uniform(1.5, 3.5)
            color = random.choice([COLOR_ACCENT_CYAN, COLOR_WHITE, (100, 240, 255)])
            life = random.uniform(0.2, 0.45)
            self.particles.append(Particle(x, y, vx, vy, radius, color, life, drag=0.92, gravity=0.0))

    def spawn_dodge_trail(self, x: float, y: float):
        """Thruster exhaust puff during dodging."""
        for _ in range(6):
            vx = random.uniform(-40, 40)
            vy = random.uniform(30, 90)
            color = random.choice([COLOR_ACCENT_MAGENTA, COLOR_ACCENT_CYAN, COLOR_WHITE])
            p = Particle(x + random.uniform(-10, 10), y + 10, vx, vy, random.uniform(2, 4), color, 0.25, drag=0.90)
            self.particles.append(p)

    def spawn_floating_text(self, text: str, x: float, y: float, color: Tuple[int, int, int], font: pygame.font.Font):
        self.floating_texts.append(FloatingText(text, x, y, color, font))
