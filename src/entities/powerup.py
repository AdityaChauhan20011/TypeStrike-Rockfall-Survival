"""
Power-Up System for TypeStrike
Handles power-up activation, status durations (Chrono-Slow, Shield, Overcharge),
and buffs awarded by special golden/crystal power-up rocks.
"""

from typing import Dict, Optional, Callable
import random
from src.config import (
    POWERUP_SHIELD,
    POWERUP_SLOW,
    POWERUP_EMP,
    POWERUP_HEAL,
    POWERUP_DOUBLE_SCORE,
    COLOR_SHIELD,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_MAGENTA,
)


class PowerupManager:
    """Manages active temporary player buffs and timers."""

    def __init__(self):
        # Remaining durations for time-based buffs
        self.chrono_slow_timer: float = 0.0
        self.double_score_timer: float = 0.0
        self.shield_boost_timer: float = 0.0

    def reset(self):
        self.chrono_slow_timer = 0.0
        self.double_score_timer = 0.0
        self.shield_boost_timer = 0.0

    def update(self, dt: float):
        if self.chrono_slow_timer > 0:
            self.chrono_slow_timer = max(0.0, self.chrono_slow_timer - dt)
        if self.double_score_timer > 0:
            self.double_score_timer = max(0.0, self.double_score_timer - dt)
        if self.shield_boost_timer > 0:
            self.shield_boost_timer = max(0.0, self.shield_boost_timer - dt)

    def is_chrono_slow_active(self) -> bool:
        return self.chrono_slow_timer > 0

    def is_double_score_active(self) -> bool:
        return self.double_score_timer > 0

    def activate_random_powerup(self, player, stats_tracker, particle_manager, audio_manager, font):
        """Activates a random beneficial powerup when a powerup rock is destroyed."""
        powerup_types = [
            POWERUP_SHIELD,
            POWERUP_SLOW,
            POWERUP_EMP,
            POWERUP_HEAL,
            POWERUP_DOUBLE_SCORE,
        ]
        chosen = random.choice(powerup_types)
        audio_manager.play_sfx("powerup")

        if chosen == POWERUP_SHIELD:
            player.shield = min(player.max_shield, player.shield + 50)
            self.shield_boost_timer = 6.0
            particle_manager.spawn_floating_text("ENERGY SHIELD +50!", player.x, player.y - 60, COLOR_SHIELD, font)

        elif chosen == POWERUP_SLOW:
            self.chrono_slow_timer = 6.5
            particle_manager.spawn_floating_text("CHRONO SLOW (6s)!", player.x, player.y - 60, COLOR_ACCENT_CYAN, font)

        elif chosen == POWERUP_EMP:
            player.emp_charge = player.max_emp_charge
            particle_manager.spawn_floating_text("EMP BOMB FULLY CHARGED [SPACE]!", player.x, player.y - 60, COLOR_ACCENT_GOLD, font)

        elif chosen == POWERUP_HEAL:
            player.health = min(player.max_health, player.health + 30)
            particle_manager.spawn_floating_text("NANITE REPAIR +30 HP!", player.x, player.y - 60, COLOR_ACCENT_GREEN, font)

        elif chosen == POWERUP_DOUBLE_SCORE:
            self.double_score_timer = 10.0
            particle_manager.spawn_floating_text("DOUBLE SCORE (10s)!", player.x, player.y - 60, COLOR_ACCENT_MAGENTA, font)
