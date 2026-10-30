"""
Projectile and Blast Wave System for TypeStrike
Handles player plasma laser bolts fired at typed targets,
and expanding EMP blast waves.
"""

import math
from typing import List, Tuple, Callable
import pygame
from src.config import COLOR_ACCENT_CYAN, COLOR_WHITE, COLOR_ACCENT_GOLD, COLOR_ACCENT_MAGENTA


class LaserBolt:
    """A high-speed plasma beam traveling towards a target coordinate."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        speed: float = 1600.0,
        on_hit: Callable = None
    ):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.on_hit = on_hit
        self.is_alive = True

        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
        else:
            self.vx = 0
            self.vy = -speed

        self.angle = math.atan2(dy, dx)
        self.length = 40.0

    def update(self, dt: float):
        if not self.is_alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Check if reached or passed target point
        if self.vy < 0 and self.y <= self.target_y:
            self.is_alive = False
            if self.on_hit:
                self.on_hit(self.target_x, self.target_y)
        elif self.vy >= 0 and self.y >= self.target_y:
            self.is_alive = False
            if self.on_hit:
                self.on_hit(self.target_x, self.target_y)

    def render(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        tail_x = self.x - math.cos(self.angle) * self.length
        tail_y = self.y - math.sin(self.angle) * self.length

        # Outer glow beam
        pygame.draw.line(surface, COLOR_ACCENT_CYAN, (tail_x, tail_y), (self.x, self.y), 6)
        # Inner white laser core
        pygame.draw.line(surface, COLOR_WHITE, (tail_x, tail_y), (self.x, self.y), 2)
        # Tip bright point
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), 4)


class EMPBlastWave:
    """Expanding full-screen circular electromagnetic shockwave."""

    def __init__(self, origin_x: float, origin_y: float, max_radius: float = 900.0, expansion_speed: float = 1400.0):
        self.x = origin_x
        self.y = origin_y
        self.radius = 10.0
        self.max_radius = max_radius
        self.speed = expansion_speed
        self.is_alive = True
        self.affected_rocks = set()

    def update(self, dt: float):
        if not self.is_alive:
            return
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.is_alive = False

    def render(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        alpha = int(255 * (1.0 - (self.radius / self.max_radius)))
        if alpha <= 0:
            return

        temp_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*COLOR_ACCENT_CYAN[:3], alpha)
        inner_color = (*COLOR_WHITE[:3], int(alpha * 0.8))

        pygame.draw.circle(temp_surf, color, (int(self.x), int(self.y)), int(self.radius), 8)
        if self.radius > 15:
            pygame.draw.circle(temp_surf, inner_color, (int(self.x), int(self.y)), int(self.radius - 8), 3)

        surface.blit(temp_surf, (0, 0))


class ProjectileManager:
    """Oversees active laser bolts and EMP blasts."""

    def __init__(self):
        self.bolts: List[LaserBolt] = []
        self.emp_waves: List[EMPBlastWave] = []

    def reset(self):
        self.bolts.clear()
        self.emp_waves.clear()

    def spawn_laser_bolt(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        speed: float = 1600.0,
        on_hit: Callable = None
    ):
        bolt = LaserBolt(start_x, start_y, target_x, target_y, speed=speed, on_hit=on_hit)
        self.bolts.append(bolt)

    def spawn_emp_blast(self, origin_x: float, origin_y: float):
        self.emp_waves.append(EMPBlastWave(origin_x, origin_y))

    def update(self, dt: float):
        for b in self.bolts:
            b.update(dt)
        self.bolts = [b for b in self.bolts if b.is_alive]

        for emp in self.emp_waves:
            emp.update(dt)
        self.emp_waves = [emp for emp in self.emp_waves if emp.is_alive]

    def render(self, surface: pygame.Surface):
        for b in self.bolts:
            b.render(surface)
        for emp in self.emp_waves:
            emp.render(surface)
