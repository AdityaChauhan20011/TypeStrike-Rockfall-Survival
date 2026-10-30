"""
TypeStrike: Rockfall Survival - Main Application Entry Point
High-performance arcade typing combat game combining reflexes, survival action,
intelligent typing targeting, and advanced performance analytics.
"""

import sys
import os
import pygame

# Ensure project root is in system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TITLE,
    VERSION,
    MODE_SURVIVAL,
    MODE_PRACTICE,
    DIFFICULTY_NORMAL,
)
from src.audio.audio_manager import AudioManager
from src.storage.db_manager import DBManager
from src.typing.word_dict import WordBank
from src.engine.game_scene import GameScene
from src.ui.menu_screens import (
    MainMenuScreen,
    ModeSelectScreen,
    DifficultySelectScreen,
    SettingsScreen,
    TutorialScreen,
    LeaderboardScreen,
)
from src.ui.results_screen import ResultsScreen
from src.engine.background import Background


# High-Level State Enum
STATE_MAIN_MENU = "main_menu"
STATE_MODE_SELECT = "mode_select"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_GAMEPLAY = "gameplay"
STATE_RESULTS = "results"
STATE_SETTINGS = "settings"
STATE_TUTORIAL = "tutorial"
STATE_LEADERBOARD = "leaderboard"


class TypeStrikeApp:
    """Primary game application manager orchestrating scenes, fonts, events, and rendering."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(f"{TITLE} v{VERSION}")

        # Set up display surface
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Initialize core services
        self.audio = AudioManager.get_instance()
        self.db = DBManager.get_instance()
        self.word_bank = WordBank()

        # Load typography fonts
        self.fonts = self._load_fonts()

        # Initialize visual background for menus
        self.menu_background = Background()

        # Application state
        self.current_state = STATE_MAIN_MENU
        self.selected_mode = MODE_SURVIVAL
        self.selected_difficulty = DIFFICULTY_NORMAL
        self.last_summary = {}
        self.is_new_high_score = False

        # Initialize Game Scene
        self.game_scene = GameScene(
            self.fonts,
            self.audio,
            self.word_bank,
            on_game_over=self._handle_game_over,
            on_quit_to_menu=lambda: self._change_state(STATE_MAIN_MENU),
        )

        # Initialize UI Screens
        self._init_screens()

    def _load_fonts(self):
        """Loads modern clean fonts with graceful system fallbacks."""
        font_names = ["Segoe UI", "Arial", "Consolas", "Courier New", "sans-serif"]
        
        def get_sys_font(size, bold=False):
            for name in font_names:
                try:
                    f = pygame.font.SysFont(name, size, bold=bold)
                    if f:
                        return f
                except Exception:
                    continue
            return pygame.font.Font(None, size)

        return {
            "default": pygame.font.Font(None, 20),
            "regular_14": get_sys_font(14, bold=False),
            "regular_16": get_sys_font(16, bold=False),
            "bold_18": get_sys_font(18, bold=True),
            "bold_20": get_sys_font(20, bold=True),
            "bold_24": get_sys_font(24, bold=True),
            "bold_32": get_sys_font(32, bold=True),
            "bold_48": get_sys_font(48, bold=True),
        }

    def _init_screens(self):
        """Builds all menu and dashboard screens with wire callbacks."""
        menu_callbacks = {
            "on_quick_play": self._start_quick_play,
            "on_mode_select": lambda: self._change_state(STATE_MODE_SELECT),
            "on_practice": self._start_practice,
            "on_leaderboard": lambda: self._change_state(STATE_LEADERBOARD),
            "on_settings": lambda: self._change_state(STATE_SETTINGS),
            "on_tutorial": lambda: self._change_state(STATE_TUTORIAL),
            "on_quit": self._quit,
        }
        self.screen_main_menu = MainMenuScreen(self.fonts, menu_callbacks)

        self.screen_mode_select = ModeSelectScreen(
            self.fonts,
            on_select_mode=self._on_mode_chosen,
            on_back=lambda: self._change_state(STATE_MAIN_MENU),
        )

        self.screen_diff_select = DifficultySelectScreen(
            self.fonts,
            on_select_diff=self._on_diff_chosen,
            on_back=lambda: self._change_state(STATE_MODE_SELECT),
        )

        self.screen_settings = SettingsScreen(
            self.fonts,
            self.audio,
            self.db,
            on_back=lambda: self._change_state(STATE_MAIN_MENU),
        )

        self.screen_tutorial = TutorialScreen(
            self.fonts,
            on_back=lambda: self._change_state(STATE_MAIN_MENU),
        )

        self.screen_leaderboard = LeaderboardScreen(
            self.fonts,
            self.db,
            on_back=lambda: self._change_state(STATE_MAIN_MENU),
        )

        self.screen_results = ResultsScreen(
            self.fonts,
            on_retry=self._retry_current_game,
            on_menu=lambda: self._change_state(STATE_MAIN_MENU),
            on_leaderboard=lambda: self._change_state(STATE_LEADERBOARD),
        )

    def _change_state(self, new_state: str):
        self.current_state = new_state

    def _start_quick_play(self):
        """Starts quick play with Survival mode on Normal difficulty."""
        self.selected_mode = MODE_SURVIVAL
        self.selected_difficulty = DIFFICULTY_NORMAL
        self.game_scene.start_game(self.selected_mode, self.selected_difficulty)
        self._change_state(STATE_GAMEPLAY)

    def _start_practice(self):
        """Starts Practice mode immediately."""
        self.selected_mode = MODE_PRACTICE
        self.selected_difficulty = DIFFICULTY_NORMAL
        self.game_scene.start_game(self.selected_mode, self.selected_difficulty)
        self._change_state(STATE_GAMEPLAY)

    def _on_mode_chosen(self, mode: str):
        self.selected_mode = mode
        self._change_state(STATE_DIFFICULTY_SELECT)

    def _on_diff_chosen(self, difficulty: str):
        self.selected_difficulty = difficulty
        self.game_scene.start_game(self.selected_mode, self.selected_difficulty)
        self._change_state(STATE_GAMEPLAY)

    def _retry_current_game(self):
        self.game_scene.start_game(self.selected_mode, self.selected_difficulty)
        self._change_state(STATE_GAMEPLAY)

    def _handle_game_over(self, summary: dict):
        """Persists stats to SQLite and shifts to results dashboard."""
        self.last_summary = summary
        
        # Check if score is a new high score
        top_scores = self.db.get_top_scores(mode=self.selected_mode, limit=1)
        prev_best = top_scores[0]["score"] if top_scores else 0
        self.is_new_high_score = summary.get("score", 0) > prev_best and summary.get("score", 0) > 0

        # Save to SQLite
        self.db.save_session(summary, self.selected_mode, self.selected_difficulty)
        self._change_state(STATE_RESULTS)

    def _quit(self):
        self.is_running = False

    def run(self):
        """Main game loop with stable delta time."""
        while self.is_running:
            # Calculate delta time in seconds, clamped to avoid physics hitching
            dt = min(0.08, self.clock.tick(FPS) / 1000.0)
            mouse_pos = pygame.mouse.get_pos()

            # Process global events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    break

                # Dispatch events according to active state
                if self.current_state == STATE_GAMEPLAY:
                    self.game_scene.handle_event(event)
                elif self.current_state == STATE_MAIN_MENU:
                    self.screen_main_menu.handle_event(event)
                elif self.current_state == STATE_MODE_SELECT:
                    self.screen_mode_select.handle_event(event)
                elif self.current_state == STATE_DIFFICULTY_SELECT:
                    self.screen_diff_select.handle_event(event)
                elif self.current_state == STATE_SETTINGS:
                    self.screen_settings.handle_event(event)
                elif self.current_state == STATE_TUTORIAL:
                    self.screen_tutorial.handle_event(event)
                elif self.current_state == STATE_LEADERBOARD:
                    self.screen_leaderboard.handle_event(event)
                elif self.current_state == STATE_RESULTS:
                    self.screen_results.handle_event(event)

            # Update active state
            if self.current_state == STATE_GAMEPLAY:
                self.game_scene.update(dt)
            else:
                self.menu_background.update(dt, game_speed=0.5)
                if self.current_state == STATE_MAIN_MENU:
                    self.screen_main_menu.update(dt, mouse_pos)
                elif self.current_state == STATE_MODE_SELECT:
                    self.screen_mode_select.update(dt, mouse_pos)
                elif self.current_state == STATE_DIFFICULTY_SELECT:
                    self.screen_diff_select.update(dt, mouse_pos)
                elif self.current_state == STATE_SETTINGS:
                    self.screen_settings.update(dt, mouse_pos)
                elif self.current_state == STATE_TUTORIAL:
                    self.screen_tutorial.update(dt, mouse_pos)
                elif self.current_state == STATE_LEADERBOARD:
                    self.screen_leaderboard.update(dt, mouse_pos)
                elif self.current_state == STATE_RESULTS:
                    self.screen_results.update(dt, mouse_pos)

            # Render active state
            if self.current_state == STATE_GAMEPLAY:
                self.game_scene.render(self.screen)
            else:
                self.menu_background.render(self.screen)
                if self.current_state == STATE_MAIN_MENU:
                    self.screen_main_menu.render(self.screen)
                elif self.current_state == STATE_MODE_SELECT:
                    self.screen_mode_select.render(self.screen)
                elif self.current_state == STATE_DIFFICULTY_SELECT:
                    self.screen_diff_select.render(self.screen)
                elif self.current_state == STATE_SETTINGS:
                    self.screen_settings.render(self.screen)
                elif self.current_state == STATE_TUTORIAL:
                    self.screen_tutorial.render(self.screen)
                elif self.current_state == STATE_LEADERBOARD:
                    self.screen_leaderboard.render(self.screen)
                elif self.current_state == STATE_RESULTS:
                    self.screen_results.render(self.screen, self.last_summary, is_new_high_score=self.is_new_high_score)

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = TypeStrikeApp()
    app.run()
