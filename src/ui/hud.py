"""
In-Game HUD Display for TypeStrike
Renders top combat stats (Score, Combo, WPM, Accuracy, Streak, Wave/Time),
and bottom player status (Health, Shield, EMP Meter, Dodge CD, and Buff Timers).
"""

import math
from typing import Tuple, Dict, Any
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    COLOR_SHIELD,
    COLOR_HEALTH_FULL,
    COLOR_HEALTH_MID,
    COLOR_HEALTH_LOW,
    COLOR_GRAY_LIGHT,
    COLOR_GRAY_MID,
    COLOR_GRAY_DARK,
    MODE_SURVIVAL,
    MODE_PRACTICE,
    MODE_TIME_ATTACK,
    MODE_ENDLESS,
)
from src.ui.components import ProgressBar


class HUD:
    """Manages the in-game heads-up display rendering."""

    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        self.fonts = fonts
        
        # Health & Shield progress bars at bottom left
        self.health_bar = ProgressBar((30, SCREEN_HEIGHT - 38, 180, 14), 100, 100, COLOR_HEALTH_FULL)
        self.shield_bar = ProgressBar((30, SCREEN_HEIGHT - 18, 180, 10), 50, 100, COLOR_SHIELD)
        
        # EMP Charge progress bar at bottom right
        self.emp_bar = ProgressBar((SCREEN_WIDTH - 210, SCREEN_HEIGHT - 30, 180, 16), 0, 100, COLOR_ACCENT_GOLD)

        # Smooth score roll-up
        self.displayed_score = 0

    def update(self, dt: float, player, score: int):
        # Smooth score increment
        self.displayed_score += int((score - self.displayed_score) * min(1.0, dt * 10))
        if abs(score - self.displayed_score) < 4:
            self.displayed_score = score

        # Update health bar color dynamically
        hp_ratio = player.health / player.max_health
        if hp_ratio > 0.5:
            hp_color = COLOR_HEALTH_FULL
        elif hp_ratio > 0.25:
            hp_color = COLOR_HEALTH_MID
        else:
            hp_color = COLOR_HEALTH_LOW

        self.health_bar.fill_color = hp_color
        self.health_bar.update(dt, player.health)
        self.shield_bar.update(dt, player.shield)
        self.emp_bar.update(dt, player.emp_charge)

    def render(
        self,
        surface: pygame.Surface,
        player,
        stats,
        powerup_mgr,
        game_mode: str,
        wave_or_time_str: str,
        combo_mult: float,
    ):
        # 1. TOP HEADER BANNER
        header_surf = pygame.Surface((SCREEN_WIDTH, 52), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (16, 22, 38, 225), (0, 0, SCREEN_WIDTH, 52))
        pygame.draw.line(header_surf, (40, 52, 80), (0, 51), (SCREEN_WIDTH, 51), 1)
        surface.blit(header_surf, (0, 0))

        font_large = self.fonts.get("bold_24", self.fonts["default"])
        font_mid = self.fonts.get("bold_18", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        # Score (Left)
        score_text = font_large.render(f"{self.displayed_score:,}", True, COLOR_WHITE)
        score_lbl = font_small.render("SCORE", True, COLOR_GRAY_LIGHT)
        surface.blit(score_lbl, (25, 8))
        surface.blit(score_text, (25, 22))

        # Mode & Wave/Timer (Center-Left)
        mode_surf = font_mid.render(f"{game_mode.upper()}  •  {wave_or_time_str}", True, COLOR_ACCENT_CYAN)
        surface.blit(mode_surf, (190, 16))

        # Typing Analytics Gauges (Right side of top bar)
        wpm_val = stats.get_net_wpm()
        acc_val = stats.get_accuracy()
        streak_val = stats.current_streak

        # WPM
        wpm_title = font_small.render("SPEED", True, COLOR_GRAY_LIGHT)
        wpm_txt = font_mid.render(f"{wpm_val:.0f} WPM", True, COLOR_ACCENT_CYAN)
        surface.blit(wpm_title, (SCREEN_WIDTH - 420, 8))
        surface.blit(wpm_txt, (SCREEN_WIDTH - 420, 24))

        # ACCURACY
        acc_title = font_small.render("ACCURACY", True, COLOR_GRAY_LIGHT)
        acc_txt = font_mid.render(f"{acc_val:.1f}%", True, COLOR_ACCENT_GREEN if acc_val >= 90 else COLOR_ACCENT_GOLD)
        surface.blit(acc_title, (SCREEN_WIDTH - 290, 8))
        surface.blit(acc_txt, (SCREEN_WIDTH - 290, 24))

        # STREAK & COMBO
        combo_col = COLOR_ACCENT_GOLD if combo_mult >= 1.5 else COLOR_WHITE
        streak_title = font_small.render("STREAK", True, COLOR_GRAY_LIGHT)
        streak_txt = font_mid.render(f"{streak_val} ({combo_mult:.1f}x)", True, combo_col)
        surface.blit(streak_title, (SCREEN_WIDTH - 150, 8))
        surface.blit(streak_txt, (SCREEN_WIDTH - 150, 24))

        # 2. BOTTOM PLAYER STATUS PANEL
        bottom_surf = pygame.Surface((SCREEN_WIDTH, 58), pygame.SRCALPHA)
        pygame.draw.rect(bottom_surf, (14, 18, 32, 210), (0, 0, SCREEN_WIDTH, 58))
        pygame.draw.line(bottom_surf, (35, 45, 70), (0, 0), (SCREEN_WIDTH, 0), 1)
        surface.blit(bottom_surf, (0, SCREEN_HEIGHT - 58))

        # Render Health & Shield Bars
        self.health_bar.render(surface)
        self.shield_bar.render(surface)

        hp_num = font_small.render(f"HP {int(player.health)}/{player.max_health}", True, COLOR_WHITE)
        surface.blit(hp_num, (220, SCREEN_HEIGHT - 40))

        sh_num = font_small.render(f"SHIELD {int(player.shield)}/{player.max_shield}", True, COLOR_SHIELD)
        surface.blit(sh_num, (220, SCREEN_HEIGHT - 22))

        # Lives indicator (Survival mode)
        if game_mode == MODE_SURVIVAL:
            lives_x = 340
            lives_lbl = font_small.render("LIVES:", True, COLOR_GRAY_LIGHT)
            surface.blit(lives_lbl, (lives_x, SCREEN_HEIGHT - 32))
            for i in range(player.lives):
                pygame.draw.polygon(
                    surface,
                    COLOR_ACCENT_MAGENTA,
                    [
                        (lives_x + 55 + i * 20, SCREEN_HEIGHT - 32),
                        (lives_x + 63 + i * 20, SCREEN_HEIGHT - 24),
                        (lives_x + 55 + i * 20, SCREEN_HEIGHT - 16),
                        (lives_x + 47 + i * 20, SCREEN_HEIGHT - 24),
                    ]
                )

        # Dodge status indicator (Center bottom)
        dodge_ready = player.dodge_cooldown <= 0
        dodge_col = COLOR_ACCENT_MAGENTA if dodge_ready else COLOR_GRAY_MID
        dodge_str = "[←/→] DODGE (Click)" if dodge_ready else f"DODGE ({player.dodge_cooldown:.1f}s)"
        dodge_txt = font_small.render(dodge_str, True, dodge_col)
        surface.blit(dodge_txt, (SCREEN_WIDTH // 2 - dodge_txt.get_width() // 2, SCREEN_HEIGHT - 32))

        # EMP Special Bar & Trigger prompt (Bottom right)
        self.emp_bar.render(surface)
        emp_ready = player.emp_charge >= player.max_emp_charge
        if emp_ready:
            pulse = int(pygame.time.get_ticks() / 250) % 2
            emp_str = "★ [CLICK] EMP BOMB READY! ★" if pulse else "  [CLICK] EMP BOMB READY!  "
            emp_txt = font_mid.render(emp_str, True, COLOR_ACCENT_GOLD)
        else:
            emp_txt = font_small.render(f"EMP CHARGE {int(player.emp_charge)}%", True, COLOR_GRAY_LIGHT)
        surface.blit(emp_txt, (SCREEN_WIDTH - 210, SCREEN_HEIGHT - 52))

    def is_emp_clicked(self, pos: Tuple[int, int]) -> bool:
        """Returns True if the user clicked the EMP gauge area."""
        return pygame.Rect(SCREEN_WIDTH - 230, SCREEN_HEIGHT - 65, 220, 55).collidepoint(pos)

    def is_dodge_clicked(self, pos: Tuple[int, int]) -> bool:
        """Returns True if the user clicked the bottom dodge indicator area."""
        return pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 45, 240, 35).collidepoint(pos)

        # 3. ACTIVE POWER-UP STATUS BADGES
        badge_y = 62
        if powerup_mgr.is_chrono_slow_active():
            slow_txt = font_small.render(f"⚡ CHRONO SLOW: {powerup_mgr.chrono_slow_timer:.1f}s", True, COLOR_ACCENT_CYAN)
            surface.blit(slow_txt, (25, badge_y))
            badge_y += 20
        if powerup_mgr.is_double_score_active():
            dbl_txt = font_small.render(f"★ 2X SCORE OVERCHARGE: {powerup_mgr.double_score_timer:.1f}s", True, COLOR_ACCENT_MAGENTA)
            surface.blit(dbl_txt, (25, badge_y))
            badge_y += 20
