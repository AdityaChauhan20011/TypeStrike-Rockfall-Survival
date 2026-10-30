"""
Player Entity and Cyber-Gunner Turret for TypeStrike
Handles positioning, dynamic cannon aiming towards active targets,
dodge-dash evasion with i-frames, health/shield mitigation, and EMP blast triggering.
"""

import math
from typing import Tuple, Optional
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_MAX_HEALTH,
    PLAYER_MAX_SHIELD,
    PLAYER_STARTING_LIVES,
    PLAYER_MOVE_SPEED,
    PLAYER_DODGE_SPEED,
    PLAYER_DODGE_DURATION,
    PLAYER_DODGE_COOLDOWN,
    PLAYER_INVULN_TIME,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_GOLD,
    COLOR_WHITE,
    COLOR_SHIELD,
    COLOR_HEALTH_FULL,
    COLOR_HEALTH_LOW,
    EMP_MAX_CHARGE,
    EMP_CHARGE_PER_WORD,
)


class Player:
    """The cyber defense turret controlled at the bottom of the screen."""

    def __init__(self, x: float = SCREEN_WIDTH // 2, y: float = SCREEN_HEIGHT - 65):
        self.x = x
        self.y = y
        self.width = 68
        self.height = 42
        
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_shield = PLAYER_MAX_SHIELD
        self.shield = 50.0
        self.lives = PLAYER_STARTING_LIVES

        # EMP Special Ability
        self.emp_charge = 0.0
        self.max_emp_charge = float(EMP_MAX_CHARGE)

        # Movement & Dodge mechanics
        self.vx = 0.0
        self.dodge_direction = 0  # -1 for Left, 1 for Right, 0 for none
        self.dodge_timer = 0.0
        self.dodge_cooldown = 0.0
        
        # Invulnerability states (after damage or during dodge)
        self.invuln_timer = 0.0
        self.flash_timer = 0.0

        # Cannon aiming angle
        self.aim_angle = -math.pi / 2  # Straight up by default
        self.muzzle_flash_timer = 0.0

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.health = self.max_health
        self.shield = 50.0
        self.lives = PLAYER_STARTING_LIVES
        self.emp_charge = 0.0
        self.dodge_direction = 0
        self.dodge_timer = 0.0
        self.dodge_cooldown = 0.0
        self.invuln_timer = 0.0
        self.aim_angle = -math.pi / 2
        self.muzzle_flash_timer = 0.0

    def is_invulnerable(self) -> bool:
        return self.invuln_timer > 0 or self.dodge_timer > 0

    def trigger_dodge(self, direction: int) -> bool:
        """
        Initiates a quick tactical dodge roll left (-1) or right (1).
        Returns True if dodge was successfully triggered.
        """
        if self.dodge_cooldown <= 0 and self.dodge_timer <= 0:
            self.dodge_direction = direction
            self.dodge_timer = PLAYER_DODGE_DURATION
            self.dodge_cooldown = PLAYER_DODGE_COOLDOWN
            return True
        return False

    def take_damage(self, amount: float) -> bool:
        """
        Applies damage to shield first, then health.
        Returns True if damage was taken, False if invulnerable.
        """
        if self.is_invulnerable():
            return False

        # Shield absorbs damage first
        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0

        # Remaining damage penetrates to health
        if amount > 0:
            self.health = max(0.0, self.health - amount)

        # Trigger invulnerability frames
        self.invuln_timer = PLAYER_INVULN_TIME
        return True

    def gain_emp_charge(self, words: int = 1):
        """Adds charge towards the EMP shockwave ability."""
        self.emp_charge = min(self.max_emp_charge, self.emp_charge + (EMP_CHARGE_PER_WORD * words))

    def update(self, dt: float, target_pos: Optional[Tuple[float, float]] = None):
        # Update cooldowns and timers
        if self.dodge_cooldown > 0:
            self.dodge_cooldown = max(0.0, self.dodge_cooldown - dt)
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer = max(0.0, self.muzzle_flash_timer - dt)
        self.flash_timer += dt * 25.0

        # Handle active dodge roll physics
        if self.dodge_timer > 0:
            self.dodge_timer -= dt
            self.x += self.dodge_direction * PLAYER_DODGE_SPEED * dt
            if self.dodge_timer <= 0:
                self.dodge_direction = 0
        else:
            # Handle standard sliding movement if velocity set
            self.x += self.vx * dt

        # Clamp inside screen boundaries with margin
        margin = self.width // 2 + 10
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))

        # Dynamic cannon aiming angle
        if target_pos is not None:
            tx, ty = target_pos
            dx = tx - self.x
            dy = ty - (self.y - 12)
            self.aim_angle = math.atan2(dy, dx)
        else:
            # Smoothly return to center upright angle
            target_angle = -math.pi / 2
            self.aim_angle += (target_angle - self.aim_angle) * min(1.0, dt * 10)

    def trigger_fire(self):
        """Triggers muzzle flash when cannon shoots."""
        self.muzzle_flash_timer = 0.12

    def get_cannon_tip(self) -> Tuple[float, float]:
        """Returns coordinate of cannon nozzle where laser originates."""
        cannon_len = 28.0
        tip_x = self.x + math.cos(self.aim_angle) * cannon_len
        tip_y = (self.y - 10) + math.sin(self.aim_angle) * cannon_len
        return tip_x, tip_y

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width // 2),
            int(self.y - self.height // 2),
            int(self.width),
            int(self.height),
        )

    def render(self, surface: pygame.Surface):
        # Flicker when invulnerable from damage (flashes at ~25Hz)
        if self.invuln_timer > 0 and (int(self.flash_timer) % 2 == 0):
            return

        cx = int(self.x)
        cy = int(self.y)

        # 1. Base platform / tread chassis
        chassis_w = self.width
        chassis_h = 16
        chassis_rect = pygame.Rect(cx - chassis_w // 2, cy + 4, chassis_w, chassis_h)
        pygame.draw.rect(surface, (28, 36, 56), chassis_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, chassis_rect, 1, border_radius=4)

        # Thruster / power core neon lights
        pygame.draw.circle(surface, COLOR_ACCENT_MAGENTA, (cx - 18, cy + 12), 3)
        pygame.draw.circle(surface, COLOR_ACCENT_CYAN, (cx, cy + 12), 4)
        pygame.draw.circle(surface, COLOR_ACCENT_MAGENTA, (cx + 18, cy + 12), 3)

        # 2. Turret dome
        dome_rect = pygame.Rect(cx - 20, cy - 14, 40, 24)
        pygame.draw.ellipse(surface, (45, 55, 85), dome_rect)
        pygame.draw.ellipse(surface, COLOR_WHITE, dome_rect, 1)

        # 3. Rotating dual plasma cannons
        cannon_len = 28
        barrel_offset = 6
        perp_angle = self.aim_angle + math.pi / 2

        for offset in (-barrel_offset, barrel_offset):
            bx = cx + math.cos(perp_angle) * offset
            by = (cy - 6) + math.sin(perp_angle) * offset
            tip_x = bx + math.cos(self.aim_angle) * cannon_len
            tip_y = by + math.sin(self.aim_angle) * cannon_len
            pygame.draw.line(surface, (15, 20, 32), (bx, by), (tip_x, tip_y), 5)
            pygame.draw.line(surface, COLOR_ACCENT_CYAN, (bx, by), (tip_x, tip_y), 2)

        # 4. Muzzle flash effect
        if self.muzzle_flash_timer > 0:
            tip_x, tip_y = self.get_cannon_tip()
            pygame.draw.circle(surface, COLOR_WHITE, (int(tip_x), int(tip_y)), 9)
            pygame.draw.circle(surface, COLOR_ACCENT_CYAN, (int(tip_x), int(tip_y)), 15, 2)

        # 5. Energy Shield Dome (if shield active)
        if self.shield > 0:
            shield_surf = pygame.Surface((self.width + 36, self.height + 40), pygame.SRCALPHA)
            shield_alpha = int(90 + 35 * math.sin(self.flash_timer * 0.4))
            shield_col = (*COLOR_SHIELD[:3], shield_alpha)
            pygame.draw.ellipse(shield_surf, shield_col, (0, 0, self.width + 36, self.height + 40), 2)
            surface.blit(shield_surf, (cx - (self.width + 36) // 2, cy - (self.height + 40) // 2 - 6))

        # 6. Dodge cooldown indicator above turret
        if self.dodge_cooldown > 0:
            ratio = 1.0 - (self.dodge_cooldown / PLAYER_DODGE_COOLDOWN)
            bar_w = 44
            bar_h = 3
            bx = cx - bar_w // 2
            by = cy - 24
            pygame.draw.rect(surface, (30, 30, 40), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, COLOR_ACCENT_MAGENTA, (bx, by, int(bar_w * ratio), bar_h))
