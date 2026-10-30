"""
Post-Game Analytics Dashboard and Results Screen for TypeStrike
Renders full performance metrics, arcade rank badge (S+, S, A, B, C, D),
speed and accuracy breakdowns, personalized improvement recommendations, and replay controls.
"""

from typing import Dict, Any, Tuple
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_MAGENTA,
    COLOR_GRAY_LIGHT,
    COLOR_GRAY_MID,
    COLOR_GRAY_DARK,
)
from src.ui.components import Button


class ResultsScreen:
    """Detailed analytics dashboard shown upon game over or session completion."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], on_retry, on_menu, on_leaderboard):
        self.fonts = fonts
        self.on_retry = on_retry
        self.on_menu = on_menu
        self.on_leaderboard = on_leaderboard

        # Buttons at bottom
        btn_y = SCREEN_HEIGHT - 85
        btn_w = 190
        btn_h = 48
        spacing = 30
        total_w = btn_w * 3 + spacing * 2
        start_x = (SCREEN_WIDTH - total_w) // 2

        self.btn_retry = Button(
            (start_x, btn_y, btn_w, btn_h),
            "PLAY AGAIN",
            fonts.get("bold_18", fonts["default"]),
            on_click=self.on_retry,
            accent_color=COLOR_ACCENT_GREEN,
        )
        self.btn_leaderboard = Button(
            (start_x + btn_w + spacing, btn_y, btn_w, btn_h),
            "HIGH SCORES",
            fonts.get("bold_18", fonts["default"]),
            on_click=self.on_leaderboard,
            accent_color=COLOR_ACCENT_GOLD,
        )
        self.btn_menu = Button(
            (start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h),
            "MAIN MENU",
            fonts.get("bold_18", fonts["default"]),
            on_click=self.on_menu,
            accent_color=COLOR_ACCENT_CYAN,
        )

        self.buttons = [self.btn_retry, self.btn_leaderboard, self.btn_menu]

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        for btn in self.buttons:
            btn.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, surface: pygame.Surface, summary: Dict[str, Any], is_new_high_score: bool = False):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        font_grade = self.fonts.get("bold_48", self.fonts["default"])
        font_sub = self.fonts.get("bold_20", self.fonts["default"])
        font_body = self.fonts.get("regular_16", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        # Dim background frosted overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 24, 220))
        surface.blit(overlay, (0, 0))

        # Central Results Card Panel
        card_w = 880
        card_h = 490
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = 45

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (18, 24, 42, 240), (0, 0, card_w, card_h), border_radius=14)
        pygame.draw.rect(card_surf, (45, 60, 95), (0, 0, card_w, card_h), 2, border_radius=14)
        surface.blit(card_surf, (card_x, card_y))

        # Title & High Score banner
        title_txt = font_title.render("COMBAT DEBRIEF & ANALYTICS", True, COLOR_WHITE)
        surface.blit(title_txt, (card_x + 35, card_y + 25))

        if is_new_high_score:
            hs_badge = font_sub.render("★ NEW PERSONAL BEST SCORE! ★", True, COLOR_ACCENT_GOLD)
            surface.blit(hs_badge, (card_x + card_w - hs_badge.get_width() - 35, card_y + 32))

        pygame.draw.line(surface, (40, 52, 80), (card_x + 35, card_y + 68), (card_x + card_w - 35, card_y + 68), 1)

        # 1. Left Column: Arcade Grade & Core Result
        left_x = card_x + 40
        grade_str = summary.get("grade", "D")
        
        # Grade box
        grade_box_rect = pygame.Rect(left_x, card_y + 90, 160, 130)
        pygame.draw.rect(surface, (25, 34, 58), grade_box_rect, border_radius=10)
        
        grade_colors = {
            "S+": COLOR_ACCENT_GOLD,
            "S": COLOR_ACCENT_GOLD,
            "A": COLOR_ACCENT_CYAN,
            "B": COLOR_ACCENT_GREEN,
            "C": COLOR_ACCENT_MAGENTA,
            "D": COLOR_ACCENT_RED,
        }
        grade_color = grade_colors.get(grade_str, COLOR_WHITE)
        pygame.draw.rect(surface, grade_color, grade_box_rect, 2, border_radius=10)

        rank_lbl = font_small.render("COMBAT RANK", True, COLOR_GRAY_LIGHT)
        surface.blit(rank_lbl, (grade_box_rect.centerx - rank_lbl.get_width() // 2, grade_box_rect.y + 12))

        grade_txt = font_grade.render(grade_str, True, grade_color)
        surface.blit(grade_txt, (grade_box_rect.centerx - grade_txt.get_width() // 2, grade_box_rect.y + 42))

        # Score box directly under grade
        score_box_rect = pygame.Rect(left_x, card_y + 235, 160, 90)
        pygame.draw.rect(surface, (25, 34, 58), score_box_rect, border_radius=10)
        pygame.draw.rect(surface, (45, 60, 95), score_box_rect, 1, border_radius=10)
        
        score_lbl = font_small.render("FINAL SCORE", True, COLOR_GRAY_LIGHT)
        surface.blit(score_lbl, (score_box_rect.centerx - score_lbl.get_width() // 2, score_box_rect.y + 14))
        
        score_val = font_sub.render(f"{summary.get('score', 0):,}", True, COLOR_WHITE)
        surface.blit(score_val, (score_box_rect.centerx - score_val.get_width() // 2, score_box_rect.y + 44))

        # 2. Right Column: Detailed Metric Grid
        grid_x = card_x + 230
        grid_y = card_y + 90
        col_w = 195
        row_h = 70

        metrics = [
            ("NET TYPING SPEED", f"{summary.get('net_wpm', 0.0):.1f} WPM", COLOR_ACCENT_CYAN, "Standard 5-char net"),
            ("KEYSTROKE ACCURACY", f"{summary.get('accuracy', 0.0):.1f}%", COLOR_ACCENT_GREEN, "Correct / total strokes"),
            ("PEAK TYPING SPEED", f"{summary.get('peak_wpm', 0.0):.1f} WPM", COLOR_ACCENT_CYAN, "Highest sustained burst"),
            ("WORDS COMPLETED", f"{summary.get('completed_words', 0)} rocks", COLOR_WHITE, "Targets destroyed"),
            ("SURVIVAL DURATION", f"{summary.get('survival_time', 0.0):.1f}s", COLOR_WHITE, "Total combat time"),
            ("LONGEST STREAK", f"{summary.get('longest_streak', 0)} in a row", COLOR_ACCENT_GOLD, "Consecutive clean words"),
        ]

        for i, (label, val_str, val_col, sub_desc) in enumerate(metrics):
            rx = grid_x + (i % 3) * col_w
            ry = grid_y + (i // 3) * row_h
            
            box_rect = pygame.Rect(rx, ry, col_w - 15, row_h - 10)
            pygame.draw.rect(surface, (22, 30, 52), box_rect, border_radius=6)
            pygame.draw.rect(surface, (38, 50, 80), box_rect, 1, border_radius=6)

            lbl_surf = font_small.render(label, True, COLOR_GRAY_LIGHT)
            surface.blit(lbl_surf, (rx + 10, ry + 8))

            val_surf = font_sub.render(val_str, True, val_col)
            surface.blit(val_surf, (rx + 10, ry + 28))

        # Keystrokes & Missed targets summary bar
        stats_line_y = card_y + 250
        corr_k = summary.get("correct_keystrokes", 0)
        inc_k = summary.get("incorrect_keystrokes", 0)
        miss_w = summary.get("missed_words", 0)
        
        detail_str = f"Keystrokes: {corr_k} Correct  |  {inc_k} Errors  |  Targets Missed: {miss_w} rocks"
        detail_surf = font_small.render(detail_str, True, COLOR_GRAY_LIGHT)
        surface.blit(detail_surf, (grid_x, stats_line_y))

        # 3. Bottom Recommendation / Coaching Banner
        coach_rect = pygame.Rect(left_x, card_y + 355, card_w - 80, 95)
        pygame.draw.rect(surface, (24, 32, 54), coach_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT_CYAN, coach_rect, 1, border_radius=8)

        coach_title = font_small.render("TACTICAL DEBRIEF & IMPROVEMENT TIP:", True, COLOR_ACCENT_CYAN)
        surface.blit(coach_title, (coach_rect.x + 18, coach_rect.y + 12))

        feedback_txt = summary.get("feedback", "Keep practicing to improve speed and consistency under pressure.")
        coach_body = font_body.render(feedback_txt, True, COLOR_WHITE)
        surface.blit(coach_body, (coach_rect.x + 18, coach_rect.y + 40))

        # Render action buttons
        for btn in self.buttons:
            btn.render(surface)
