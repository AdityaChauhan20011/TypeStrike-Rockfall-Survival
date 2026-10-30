"""
Rock Hazards and Falling Targets for TypeStrike
Defines procedural rendering, physics, word labeling, targeting highlights,
and distinct behaviors for Normal, Fast, Armored, Explosive, Powerup, and Boss rocks.
"""

import math
import random
from typing import List, Tuple
import pygame
from src.config import (
    ROCK_TYPE_NORMAL,
    ROCK_TYPE_FAST,
    ROCK_TYPE_ARMORED,
    ROCK_TYPE_EXPLOSIVE,
    ROCK_TYPE_POWERUP,
    ROCK_TYPE_BOSS,
    COLOR_WHITE,
    COLOR_TYPED_MATCH,
    COLOR_UNTYPED_REST,
    COLOR_TYPO_ALERT,
    COLOR_TARGET_PILL,
    COLOR_TARGET_BORDER,
    COLOR_NORMAL_BORDER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_ORANGE,
    ROCK_POINTS,
)


class Rock:
    """A falling hazard bearing a word challenge."""

    def __init__(
        self,
        x: float,
        y: float,
        word: str,
        rock_type: str = ROCK_TYPE_NORMAL,
        fall_speed: float = 70.0,
        radius: float = 28.0,
    ):
        self.pos_x = x
        self.pos_y = y
        self.target_word = word
        self.rock_type = rock_type
        self.base_fall_speed = fall_speed
        self.current_speed = fall_speed
        self.radius = radius
        
        self.is_active = True
        self.is_destroyed = False
        self.is_targeted = False
        self.typed_prefix_len = 0
        
        # Armored rock multiple phases
        self.max_health = 2 if rock_type == ROCK_TYPE_ARMORED else 1
        self.current_health = self.max_health

        # Points awarded on destruction
        self.point_value = ROCK_POINTS.get(rock_type, 100)
        if rock_type == ROCK_TYPE_ARMORED:
            self.point_value += len(word) * 20

        # Visual geometry & rotation
        self.rotation_angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-40, 40)
        self.pulse_timer = random.uniform(0, math.pi * 2)

        # Procedural polygon vertices for organic faceted asteroid appearance
        self.vertices: List[Tuple[float, float]] = []
        self._generate_polygon()

    def _generate_polygon(self):
        """Generates realistic jagged asteroid vertices around center."""
        num_points = 8 if self.rock_type != ROCK_TYPE_BOSS else 14
        angle_step = (2 * math.pi) / num_points
        self.vertices = []
        for i in range(num_points):
            angle = i * angle_step
            # Random radial perturbation
            dist = self.radius * random.uniform(0.75, 1.25)
            vx = math.cos(angle) * dist
            vy = math.sin(angle) * dist
            self.vertices.append((vx, vy))

    def set_targeted(self, targeted: bool):
        self.is_targeted = targeted
        if not targeted:
            self.typed_prefix_len = 0

    def get_color(self) -> Tuple[int, int, int]:
        """Base theme color according to rock type."""
        if self.rock_type == ROCK_TYPE_FAST:
            return (255, 90, 40)       # Blazing orange-red
        elif self.rock_type == ROCK_TYPE_ARMORED:
            return (130, 160, 210)     # Heavy reinforced steel-cyan
        elif self.rock_type == ROCK_TYPE_EXPLOSIVE:
            return (255, 45, 90)       # Volcanic magma crimson
        elif self.rock_type == ROCK_TYPE_POWERUP:
            return (255, 215, 0)       # Radiant cyber gold
        elif self.rock_type == ROCK_TYPE_BOSS:
            return (200, 60, 255)      # Titan void purple
        else:
            return (120, 130, 145)     # Classic rugged gray-blue asteroid

    def update(self, dt: float, speed_multiplier: float = 1.0):
        if not self.is_active:
            return

        self.current_speed = self.base_fall_speed * speed_multiplier
        self.pos_y += self.current_speed * dt
        self.rotation_angle += self.rotation_speed * dt
        self.pulse_timer += dt * 5.0

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos_x - self.radius),
            int(self.pos_y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )

    def render(self, surface: pygame.Surface, font: pygame.font.Font, typo_flash: bool = False):
        if not self.is_active:
            return

        # 1. Render rock body
        base_color = self.get_color()
        rad_rad = math.radians(self.rotation_angle)
        cos_r = math.cos(rad_rad)
        sin_r = math.sin(rad_rad)

        # Rotate polygon vertices
        rotated_pts = []
        for vx, vy in self.vertices:
            rx = vx * cos_r - vy * sin_r + self.pos_x
            ry = vx * sin_r + vy * cos_r + self.pos_y
            rotated_pts.append((rx, ry))

        # Trail effect for fast meteor
        if self.rock_type == ROCK_TYPE_FAST:
            trail_len = 25
            trail_surf = pygame.Surface((int(self.radius * 3), trail_len + 10), pygame.SRCALPHA)
            pygame.draw.polygon(
                trail_surf,
                (255, 120, 20, 100),
                [(self.radius * 1.5 - 12, trail_len), (self.radius * 1.5 + 12, trail_len), (self.radius * 1.5, 0)]
            )
            surface.blit(trail_surf, (self.pos_x - self.radius * 1.5, self.pos_y - self.radius - trail_len + 5))

        # Core fill
        pygame.draw.polygon(surface, base_color, rotated_pts)

        # Highlight outline (glows brightly if actively targeted)
        outline_color = COLOR_TARGET_BORDER if self.is_targeted else COLOR_WHITE
        pulse_width = 3 if self.is_targeted else 1
        pygame.draw.polygon(surface, outline_color, rotated_pts, pulse_width)

        # Shimmering crystal veins for powerup rock
        if self.rock_type == ROCK_TYPE_POWERUP:
            pulse_rad = int(self.radius * (0.4 + 0.15 * math.sin(self.pulse_timer)))
            pygame.draw.circle(surface, COLOR_WHITE, (int(self.pos_x), int(self.pos_y)), max(2, pulse_rad), 2)
        elif self.rock_type == ROCK_TYPE_EXPLOSIVE:
            pulse_rad = int(self.radius * (0.5 + 0.2 * math.sin(self.pulse_timer * 1.8)))
            pygame.draw.circle(surface, (255, 60, 20), (int(self.pos_x), int(self.pos_y)), max(2, pulse_rad))

        # 2. Render Targeted Reticle
        if self.is_targeted:
            reticle_rad = int(self.radius + 8 + 2 * math.sin(self.pulse_timer * 2.0))
            rx = int(self.pos_x)
            ry = int(self.pos_y)
            # Corner brackets
            bracket_len = 7
            pygame.draw.lines(surface, COLOR_TARGET_BORDER, False, [(rx - reticle_rad, ry - reticle_rad + bracket_len), (rx - reticle_rad, ry - reticle_rad), (rx - reticle_rad + bracket_len, ry - reticle_rad)], 2)
            pygame.draw.lines(surface, COLOR_TARGET_BORDER, False, [(rx + reticle_rad - bracket_len, ry - reticle_rad), (rx + reticle_rad, ry - reticle_rad), (rx + reticle_rad, ry - reticle_rad + bracket_len)], 2)
            pygame.draw.lines(surface, COLOR_TARGET_BORDER, False, [(rx - reticle_rad, ry + reticle_rad - bracket_len), (rx - reticle_rad, ry + reticle_rad), (rx - reticle_rad + bracket_len, ry + reticle_rad)], 2)
            pygame.draw.lines(surface, COLOR_TARGET_BORDER, False, [(rx + reticle_rad - bracket_len, ry + reticle_rad), (rx + reticle_rad, ry + reticle_rad), (rx + reticle_rad, ry + reticle_rad - bracket_len)], 2)

        # 3. Render Word Pill Banner
        self._render_word_pill(surface, font, typo_flash)

    def _render_word_pill(self, surface: pygame.Surface, font: pygame.font.Font, typo_flash: bool):
        """Renders frosted pill backdrop with color-coded typed/untyped characters."""
        word = self.target_word
        typed_len = min(self.typed_prefix_len, len(word))
        
        # Word dimensions
        text_w, text_h = font.size(word)
        pill_pad_x = 10
        pill_pad_y = 5
        pill_w = text_w + pill_pad_x * 2
        pill_h = text_h + pill_pad_y * 2
        
        pill_x = int(self.pos_x - pill_w // 2)
        pill_y = int(self.pos_y + self.radius + 4)

        # Frosted dark backing
        pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill_bg_color = (20, 26, 44, 230) if not typo_flash else (70, 20, 30, 240)
        pygame.draw.rect(pill_surf, pill_bg_color, (0, 0, pill_w, pill_h), border_radius=6)
        
        # Pill border
        border_col = COLOR_ACCENT_RED if typo_flash else (COLOR_TARGET_BORDER if self.is_targeted else COLOR_NORMAL_BORDER)
        border_thickness = 2 if (self.is_targeted or typo_flash) else 1
        pygame.draw.rect(pill_surf, border_col, (0, 0, pill_w, pill_h), border_thickness, border_radius=6)
        surface.blit(pill_surf, (pill_x, pill_y))

        # Render characters with split styling
        start_x = pill_x + pill_pad_x
        start_y = pill_y + pill_pad_y

        if typed_len > 0:
            # Correctly typed portion (bright neon cyan/green)
            matched_str = word[:typed_len]
            matched_surf = font.render(matched_str, True, COLOR_TYPED_MATCH)
            surface.blit(matched_surf, (start_x, start_y))
            start_x += matched_surf.get_width()

        if typed_len < len(word):
            # Remaining characters (crisp white, or red if typo flash on targeted)
            remaining_str = word[typed_len:]
            rem_color = COLOR_TYPO_ALERT if (typo_flash and self.is_targeted) else COLOR_UNTYPED_REST
            rem_surf = font.render(remaining_str, True, rem_color)
            surface.blit(rem_surf, (start_x, start_y))
