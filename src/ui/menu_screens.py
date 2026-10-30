"""
Menu Screens and Navigation Interfaces for TypeStrike
Includes Main Menu, Game Mode Selector, Difficulty Selector,
Settings Menu, Instructions/Tutorial, and High Scores Leaderboard.
"""

from typing import Dict, List, Tuple, Callable
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_RED,
    COLOR_GRAY_LIGHT,
    COLOR_GRAY_MID,
    COLOR_GRAY_DARK,
    MODE_SURVIVAL,
    MODE_PRACTICE,
    MODE_TIME_ATTACK,
    MODE_ENDLESS,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_EXPERT,
    DIFFICULTY_CONFIGS,
)
from src.ui.components import Button, Slider


class MainMenuScreen:
    """The central title and menu portal."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], callbacks: Dict[str, Callable]):
        self.fonts = fonts
        self.callbacks = callbacks

        font_btn = fonts.get("bold_18", fonts["default"])
        btn_w = 260
        btn_h = 44
        start_x = (SCREEN_WIDTH - btn_w) // 2
        start_y = 250
        spacing = 52

        self.buttons = [
            Button((start_x, start_y + spacing * 0, btn_w, btn_h), "SURVIVAL MODE", font_btn, on_click=callbacks.get("on_quick_play"), accent_color=COLOR_ACCENT_GREEN),
            Button((start_x, start_y + spacing * 1, btn_w, btn_h), "SELECT GAME MODE", font_btn, on_click=callbacks.get("on_mode_select"), accent_color=COLOR_ACCENT_CYAN),
            Button((start_x, start_y + spacing * 2, btn_w, btn_h), "PRACTICE TRAINING", font_btn, on_click=callbacks.get("on_practice"), accent_color=COLOR_ACCENT_MAGENTA),
            Button((start_x, start_y + spacing * 3, btn_w, btn_h), "ANALYTICS & RECORDS", font_btn, on_click=callbacks.get("on_leaderboard"), accent_color=COLOR_ACCENT_GOLD),
            Button((start_x, start_y + spacing * 4, btn_w, btn_h), "SETTINGS", font_btn, on_click=callbacks.get("on_settings")),
            Button((start_x, start_y + spacing * 5, btn_w, btn_h), "HOW TO PLAY", font_btn, on_click=callbacks.get("on_tutorial")),
            Button((start_x, start_y + spacing * 6, btn_w, btn_h), "QUIT GAME", font_btn, on_click=callbacks.get("on_quit"), accent_color=COLOR_ACCENT_RED),
        ]

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        for btn in self.buttons:
            btn.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_48", self.fonts["default"])
        font_sub = self.fonts.get("bold_18", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        # Main Logo
        t = pygame.time.get_ticks() / 1000.0
        glow_pulse = int(220 + 35 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(t * 120).x))
        logo_surf = font_title.render("TYPESTRIKE", True, (0, glow_pulse, 255))
        logo_rect = logo_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))

        # Shadow
        shadow_surf = font_title.render("TYPESTRIKE", True, (0, 40, 80))
        surface.blit(shadow_surf, (logo_rect.x + 3, logo_rect.y + 3))
        surface.blit(logo_surf, logo_rect)

        sub_surf = font_sub.render("ROCKFALL SURVIVAL  •  ADVANCED TYPING COMBAT", True, COLOR_ACCENT_GOLD)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 185))
        surface.blit(sub_surf, sub_rect)

        # Version & controls footer
        footer_surf = font_small.render("Developed with Pygame-CE • Type words to shoot • Click EMP/Dodge • [ESC] to Pause", True, COLOR_GRAY_MID)
        footer_rect = footer_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 22))
        surface.blit(footer_surf, footer_rect)

        # Render menu buttons
        for btn in self.buttons:
            btn.render(surface)


class ModeSelectScreen:
    """Screen for choosing between Survival, Practice, Time Attack, and Endless."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], on_select_mode: Callable[[str], None], on_back: Callable):
        self.fonts = fonts
        self.on_select_mode = on_select_mode
        self.on_back = on_back

        font_btn = fonts.get("bold_18", fonts["default"])
        card_w = 420
        card_h = 100
        start_x1 = (SCREEN_WIDTH - (card_w * 2 + 30)) // 2
        start_x2 = start_x1 + card_w + 30
        y1 = 200
        y2 = 325

        self.btn_survival = Button((start_x1, y1, card_w, card_h), "SURVIVAL MODE", font_btn, on_click=lambda: on_select_mode(MODE_SURVIVAL), accent_color=COLOR_ACCENT_GREEN)
        self.btn_practice = Button((start_x2, y1, card_w, card_h), "PRACTICE TRAINING", font_btn, on_click=lambda: on_select_mode(MODE_PRACTICE), accent_color=COLOR_ACCENT_MAGENTA)
        self.btn_time = Button((start_x1, y2, card_w, card_h), "TIME ATTACK (2-MIN BLITZ)", font_btn, on_click=lambda: on_select_mode(MODE_TIME_ATTACK), accent_color=COLOR_ACCENT_GOLD)
        self.btn_endless = Button((start_x2, y2, card_w, card_h), "ENDLESS ONCE-MORE", font_btn, on_click=lambda: on_select_mode(MODE_ENDLESS), accent_color=COLOR_ACCENT_CYAN)

        self.btn_back = Button(((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 90, 200, 44), "BACK TO MENU", font_btn, on_click=on_back)
        self.buttons = [self.btn_survival, self.btn_practice, self.btn_time, self.btn_endless, self.btn_back]

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        for btn in self.buttons:
            btn.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        title = font_title.render("SELECT MISSION PROTOCOL", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 90))

        # Render buttons
        for btn in self.buttons:
            btn.render(surface)

        # Mode descriptions below buttons
        desc_map = [
            (self.btn_survival, "Survive escalating waves, manage shield & 3 lives."),
            (self.btn_practice, "Infinite health, relaxed typing to hone rhythm and speed."),
            (self.btn_time, "Fast frantic race against the clock! 120s blitz."),
            (self.btn_endless, "Infinite scaling hazards with giant Titan Boss rocks."),
        ]
        for btn, desc in desc_map:
            desc_surf = font_small.render(desc, True, COLOR_GRAY_LIGHT)
            surface.blit(desc_surf, (btn.rect.x + 20, btn.rect.bottom - 26))


class DifficultySelectScreen:
    """Screen for choosing difficulty tier (Easy, Normal, Hard, Expert)."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], on_select_diff: Callable[[str], None], on_back: Callable):
        self.fonts = fonts
        self.on_select_diff = on_select_diff
        self.on_back = on_back

        font_btn = fonts.get("bold_18", fonts["default"])
        btn_w = 480
        btn_h = 75
        start_x = (SCREEN_WIDTH - btn_w) // 2
        start_y = 170
        spacing = 90

        diffs = [
            (DIFFICULTY_EASY, COLOR_ACCENT_GREEN),
            (DIFFICULTY_NORMAL, COLOR_ACCENT_CYAN),
            (DIFFICULTY_HARD, COLOR_ACCENT_GOLD),
            (DIFFICULTY_EXPERT, COLOR_ACCENT_RED),
        ]

        self.buttons = []
        for i, (d_key, accent) in enumerate(diffs):
            cfg = DIFFICULTY_CONFIGS[d_key]
            btn = Button(
                (start_x, start_y + spacing * i, btn_w, btn_h),
                cfg["name"],
                font_btn,
                on_click=lambda k=d_key: self.on_select_diff(k),
                accent_color=accent,
            )
            self.buttons.append((btn, cfg["desc"]))

        self.btn_back = Button(((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 85, 200, 44), "BACK", font_btn, on_click=on_back)

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        for btn, _ in self.buttons:
            btn.update(dt, mouse_pos)
        self.btn_back.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        for btn, _ in self.buttons:
            btn.handle_event(event)
        self.btn_back.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        title = font_title.render("SELECT DIFFICULTY COMBAT TIER", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 85))

        for btn, desc in self.buttons:
            btn.render(surface)
            desc_surf = font_small.render(desc, True, COLOR_GRAY_LIGHT)
            surface.blit(desc_surf, (btn.rect.x + 22, btn.rect.bottom - 24))

        self.btn_back.render(surface)


class SettingsScreen:
    """Audio and visual preferences."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], audio_manager, db_manager, on_back: Callable):
        self.fonts = fonts
        self.audio = audio_manager
        self.db = db_manager
        self.on_back = on_back

        font_label = fonts.get("bold_18", fonts["default"])
        font_btn = fonts.get("bold_18", fonts["default"])

        cx = (SCREEN_WIDTH - 380) // 2
        y = 200
        
        self.slider_master = Slider((cx, y, 380, 16), "Master Volume", self.audio.master_volume, font_label, on_change=self._set_master)
        self.slider_sfx = Slider((cx, y + 80, 380, 16), "Sound Effects (SFX)", self.audio.sfx_volume, font_label, on_change=self._set_sfx)
        self.slider_music = Slider((cx, y + 160, 380, 16), "Background Music", self.audio.music_volume, font_label, on_change=self._set_music)

        self.btn_back = Button(((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 100, 200, 46), "SAVE & BACK", font_btn, on_click=on_back)

    def _set_master(self, v: float):
        self.audio.set_master_volume(v)
        self.db.set_setting("master_volume", str(v))

    def _set_sfx(self, v: float):
        self.audio.set_sfx_volume(v)
        self.db.set_setting("sfx_volume", str(v))

    def _set_music(self, v: float):
        self.audio.set_music_volume(v)
        self.db.set_setting("music_volume", str(v))

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.btn_back.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        self.slider_master.handle_event(event)
        self.slider_sfx.handle_event(event)
        self.slider_music.handle_event(event)
        self.btn_back.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        title = font_title.render("AUDIO & CONTROLS SETTINGS", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 95))

        self.slider_master.render(surface)
        self.slider_sfx.render(surface)
        self.slider_music.render(surface)
        self.btn_back.render(surface)


class TutorialScreen:
    """Step-by-step game mechanics and instructions guide."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], on_back: Callable):
        self.fonts = fonts
        self.on_back = on_back
        font_btn = fonts.get("bold_18", fonts["default"])
        self.btn_back = Button(((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 75, 200, 44), "UNDERSTOOD", font_btn, on_click=on_back)

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.btn_back.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        self.btn_back.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        font_sub = self.fonts.get("bold_20", self.fonts["default"])
        font_body = self.fonts.get("regular_16", self.fonts["default"])

        title = font_title.render("HOW TO PLAY TYPESTRIKE", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 45))

        sections = [
            ("1. PURE TYPING & SMART LOCK-ON", "Type the first letter of any falling rock to lock onto it. Type the full word to shatter it! All letter keys are 100% reserved for typing. Press Backspace to correct typos or Tab to release lock."),
            ("2. TACTICAL DODGE & SHOCKWAVE", "When a hazard drops too close, press Left / Right Arrow or click the Dodge button. Destroying rocks charges your EMP capacitor; click the golden EMP bar or Right-Click anywhere to detonate!"),
            ("3. PAUSE & COMBAT SUSPENSION", "Press [ESC] at any time during a match to pause the game, suspend combat, and safely access the mission menu without losing your streak."),
            ("4. SPECIAL HAZARD TYPES & POWER-UPS", "Orange Meteors fall fast! Blue Armored rocks take more hits. Red Volcanic rocks explode nearby targets! Shimmering Gold rocks grant Shields, Chrono-Slow, and Nanite repairs."),
            ("5. COMBOS & ANALYTICS GRADING", "Unbroken clean typing builds streak multipliers up to 4.0x score. At the end of every match, review your Net WPM, accuracy %, and tailored coaching tips."),
        ]

        card_x = (SCREEN_WIDTH - 920) // 2
        card_y = 110
        card_w = 920
        card_h = 515

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (18, 24, 42, 230), (0, 0, card_w, card_h), border_radius=12)
        pygame.draw.rect(card_surf, (45, 60, 95), (0, 0, card_w, card_h), 1, border_radius=12)
        surface.blit(card_surf, (card_x, card_y))

        curr_y = card_y + 25
        for header, body in sections:
            h_surf = font_sub.render(header, True, COLOR_ACCENT_CYAN)
            surface.blit(h_surf, (card_x + 35, curr_y))
            curr_y += 28
            b_surf = font_body.render(body, True, COLOR_WHITE)
            surface.blit(b_surf, (card_x + 35, curr_y))
            curr_y += 48

        self.btn_back.render(surface)


class LeaderboardScreen:
    """Historical records, high scores, and lifetime analytics."""

    def __init__(self, fonts: Dict[str, pygame.font.Font], db_manager, on_back: Callable):
        self.fonts = fonts
        self.db = db_manager
        self.on_back = on_back
        font_btn = fonts.get("bold_18", fonts["default"])
        self.btn_back = Button(((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 75, 200, 44), "BACK TO MENU", font_btn, on_click=on_back)

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.btn_back.update(dt, mouse_pos)

    def handle_event(self, event: pygame.event.Event):
        self.btn_back.handle_event(event)

    def render(self, surface: pygame.Surface):
        font_title = self.fonts.get("bold_32", self.fonts["default"])
        font_sub = self.fonts.get("bold_18", self.fonts["default"])
        font_body = self.fonts.get("regular_16", self.fonts["default"])
        font_small = self.fonts.get("regular_14", self.fonts["default"])

        title = font_title.render("COMBAT ARCHIVES & HIGH SCORES", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Lifetime Stats Banner
        life = self.db.get_lifetime_stats()
        card_w = 900
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = 100

        top_stats = [
            ("TOTAL GAMES", f"{life['total_games']}"),
            ("HIGH SCORE", f"{life['high_score']:,}"),
            ("BEST WPM", f"{life['best_wpm']:.1f}"),
            ("AVG ACCURACY", f"{life['avg_accuracy']:.1f}%"),
            ("TOTAL WORDS", f"{life['total_words_typed']:,}"),
            ("BEST STREAK", f"{life['best_streak']}"),
        ]

        stat_w = card_w // len(top_stats)
        for i, (label, val) in enumerate(top_stats):
            bx = card_x + i * stat_w
            pygame.draw.rect(surface, (22, 28, 48), (bx, card_y, stat_w - 8, 64), border_radius=6)
            pygame.draw.rect(surface, (40, 52, 85), (bx, card_y, stat_w - 8, 64), 1, border_radius=6)
            
            l_surf = font_small.render(label, True, COLOR_GRAY_LIGHT)
            v_surf = font_sub.render(val, True, COLOR_ACCENT_CYAN)
            surface.blit(l_surf, (bx + 12, card_y + 10))
            surface.blit(v_surf, (bx + 12, card_y + 32))

        # Leaderboard Table
        table_y = 185
        table_h = 420
        pygame.draw.rect(surface, (18, 24, 42), (card_x, table_y, card_w, table_h), border_radius=8)
        pygame.draw.rect(surface, (45, 60, 95), (card_x, table_y, card_w, table_h), 1, border_radius=8)

        # Header Row
        headers = ["RANK", "DATE", "MODE", "TIER", "SCORE", "WPM", "ACCURACY", "RANK"]
        cols_x = [card_x + 20, card_x + 90, card_x + 250, card_x + 400, card_x + 520, card_x + 650, card_x + 750, card_x + 850]
        
        for h, cx in zip(headers, cols_x):
            h_surf = font_small.render(h, True, COLOR_ACCENT_GOLD)
            surface.blit(h_surf, (cx, table_y + 14))

        pygame.draw.line(surface, (40, 52, 80), (card_x + 15, table_y + 40), (card_x + card_w - 15, table_y + 40), 1)

        # Rows
        scores = self.db.get_top_scores(limit=9)
        if not scores:
            empty_txt = font_body.render("No combat sessions logged yet. Complete a mission to record your records!", True, COLOR_GRAY_MID)
            surface.blit(empty_txt, (card_x + 80, table_y + 120))
        else:
            row_y = table_y + 55
            for idx, entry in enumerate(scores):
                r_rank = font_body.render(f"#{idx + 1}", True, COLOR_WHITE)
                r_date = font_body.render(str(entry.get("created_at", ""))[:10], True, COLOR_GRAY_LIGHT)
                r_mode = font_body.render(str(entry.get("mode", "")).upper(), True, COLOR_WHITE)
                r_diff = font_body.render(str(entry.get("difficulty", "")).upper(), True, COLOR_ACCENT_CYAN)
                r_score = font_body.render(f"{entry.get('score', 0):,}", True, COLOR_ACCENT_GOLD)
                r_wpm = font_body.render(f"{entry.get('wpm', 0.0):.1f}", True, COLOR_WHITE)
                r_acc = font_body.render(f"{entry.get('accuracy', 0.0):.1f}%", True, COLOR_ACCENT_GREEN)
                r_grade = font_sub.render(str(entry.get("grade", "D")), True, COLOR_ACCENT_MAGENTA)

                surface.blit(r_rank, (cols_x[0], row_y))
                surface.blit(r_date, (cols_x[1], row_y))
                surface.blit(r_mode, (cols_x[2], row_y))
                surface.blit(r_diff, (cols_x[3], row_y))
                surface.blit(r_score, (cols_x[4], row_y))
                surface.blit(r_wpm, (cols_x[5], row_y))
                surface.blit(r_acc, (cols_x[6], row_y))
                surface.blit(r_grade, (cols_x[7], row_y - 2))

                row_y += 38

        self.btn_back.render(surface)
