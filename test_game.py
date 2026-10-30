"""
Automated Test Suite for TypeStrike: Rockfall Survival
Verifies typing calculations, analytics, database persistence,
word banks, entity physics, and collision logic.
"""

import sys
import os
import unittest
import time
import pygame

# Set dummy video driver for headless test execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.analytics.stats_tracker import StatsTracker
from src.typing.word_dict import WordBank
from src.typing.typing_engine import TypingEngine
from src.storage.db_manager import DBManager
from src.entities.player import Player
from src.entities.rock import Rock
from src.entities.projectile import ProjectileManager
from src.entities.powerup import PowerupManager
from src.audio.audio_manager import AudioManager
from src.config import (
    ROCK_TYPE_NORMAL,
    ROCK_TYPE_FAST,
    ROCK_TYPE_ARMORED,
    DIFFICULTY_NORMAL,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_EXPERT,
)


class TestTypeStrike(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_stats_tracker_wpm_and_accuracy(self):
        """Verifies standard 5-char word formula and accuracy calculations."""
        tracker = StatsTracker()
        
        # Simulate typing a 5-letter word accurately: "s-t-o-r-m"
        for _ in range(5):
            tracker.record_keystroke(is_correct=True)
        tracker.record_word_completed("storm", ROCK_TYPE_NORMAL, 100)

        # 5 keystrokes, 0 errors -> 100% accuracy
        self.assertEqual(tracker.get_accuracy(), 100.0)
        self.assertEqual(tracker.completed_words, 1)
        self.assertEqual(tracker.current_streak, 1)

        # Simulate 1 typo
        tracker.record_keystroke(is_correct=False)
        self.assertEqual(tracker.total_keystrokes, 6)
        self.assertEqual(tracker.incorrect_keystrokes, 1)
        # 5 / 6 = 83.3%
        self.assertAlmostEqual(tracker.get_accuracy(), 83.3, places=1)
        self.assertEqual(tracker.current_streak, 0) # streak reset on typo

        # Verify summary dictionary
        summary = tracker.get_summary_dict()
        self.assertIn("net_wpm", summary)
        self.assertIn("accuracy", summary)
        self.assertIn("grade", summary)
        self.assertIn("feedback", summary)

    def test_word_bank_loading_and_selection(self):
        """Verifies word bank successfully loaded vocabularies without duplicates."""
        bank = WordBank()
        self.assertGreater(len(bank.easy_words), 0)
        self.assertGreater(len(bank.normal_words), 0)
        self.assertGreater(len(bank.hard_words), 0)
        self.assertGreater(len(bank.tech_words), 0)
        self.assertGreater(len(bank.boss_phrases), 0)

        # Verify word selection for different rock types
        easy_w = bank.get_word_for_rock(ROCK_TYPE_FAST, DIFFICULTY_NORMAL)
        self.assertIsInstance(easy_w, str)
        self.assertTrue(3 <= len(easy_w) <= 6)

        # Test avoidance of already used words
        used = {"fire", "iron", "rock"}
        chosen = bank.get_word_for_rock(ROCK_TYPE_NORMAL, DIFFICULTY_NORMAL, used_words=used)
        self.assertNotIn(chosen, used)

    def test_db_manager_persistence(self):
        """Verifies SQLite high scores and session history storage."""
        # Use a temporary test db path
        test_db_path = os.path.join(BASE_DIR, "data", "test_typestrike.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        db = DBManager(db_path=test_db_path)
        
        sample_summary = {
            "score": 4500,
            "net_wpm": 68.5,
            "peak_wpm": 74.0,
            "accuracy": 96.2,
            "completed_words": 28,
            "missed_words": 1,
            "longest_streak": 22,
            "survival_time": 95.4,
            "grade": "S",
            "feedback": "Great speed!",
        }

        # Save session
        success = db.save_session(sample_summary, mode="survival", difficulty="normal")
        self.assertTrue(success)

        # Retrieve top scores
        scores = db.get_top_scores(mode="survival", limit=5)
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["score"], 4500)
        self.assertEqual(scores[0]["wpm"], 68.5)
        self.assertEqual(scores[0]["grade"], "S")

        # Verify lifetime stats
        lifetime = db.get_lifetime_stats()
        self.assertEqual(lifetime["total_games"], 1)
        self.assertEqual(lifetime["high_score"], 4500)
        self.assertEqual(lifetime["best_wpm"], 68.5)

        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    def test_typing_engine_targeting(self):
        """Verifies intelligent auto-locking onto rocks and word matching."""
        stats = StatsTracker()
        audio = AudioManager.get_instance()
        engine = TypingEngine(stats, audio)

        rock1 = Rock(x=300, y=200, word="laser")
        rock2 = Rock(x=600, y=350, word="shield")
        active_rocks = [rock1, rock2]

        # Press key 's' -> should auto-lock onto rock2 ('shield')
        mock_event_s = pygame.event.Event(pygame.KEYDOWN, {"unicode": "s", "key": pygame.K_s})
        consumed = engine.process_key_event(mock_event_s, active_rocks)
        self.assertTrue(consumed)
        self.assertIs(engine.locked_target, rock2)
        self.assertEqual(engine.typed_buffer, "s")
        self.assertEqual(rock2.typed_prefix_len, 1)

        # Press key 'h' -> correct continuation
        mock_event_h = pygame.event.Event(pygame.KEYDOWN, {"unicode": "h", "key": pygame.K_h})
        consumed = engine.process_key_event(mock_event_h, active_rocks)
        self.assertTrue(consumed)
        self.assertEqual(engine.typed_buffer, "sh")

        # Press key 'x' -> typo!
        mock_event_x = pygame.event.Event(pygame.KEYDOWN, {"unicode": "x", "key": pygame.K_x})
        consumed = engine.process_key_event(mock_event_x, active_rocks)
        self.assertTrue(consumed)
        self.assertEqual(engine.typed_buffer, "sh")  # buffer unchanged
        self.assertGreater(engine.typo_flash_timer, 0)
        self.assertEqual(stats.incorrect_keystrokes, 1)

        # Test Backspace
        mock_event_back = pygame.event.Event(pygame.KEYDOWN, {"unicode": "", "key": pygame.K_BACKSPACE})
        consumed = engine.process_key_event(mock_event_back, active_rocks)
        self.assertTrue(consumed)
        self.assertEqual(engine.typed_buffer, "s")

    def test_player_mechanics_and_dodge(self):
        """Verifies player damage absorption, shield depletion, and dodge i-frames."""
        player = Player(x=640, y=650)
        self.assertEqual(player.health, 100)
        self.assertEqual(player.shield, 50)

        # Take 30 damage: shield absorbs all 30
        damaged = player.take_damage(30)
        self.assertTrue(damaged)
        self.assertEqual(player.shield, 20)
        self.assertEqual(player.health, 100)

        # Reset invuln to test health penetration
        player.invuln_timer = 0
        # Take 40 damage: shield absorbs remaining 20, 20 penetrates to health
        damaged = player.take_damage(40)
        self.assertTrue(damaged)
        self.assertEqual(player.shield, 0)
        self.assertEqual(player.health, 80)

        # Test Dodge initiation
        dodged = player.trigger_dodge(1)
        self.assertTrue(dodged)
        self.assertTrue(player.is_invulnerable())
        self.assertEqual(player.dodge_direction, 1)

    def test_projectile_and_powerup_systems(self):
        """Verifies laser bolt trajectory and powerup timers."""
        p_mgr = ProjectileManager()
        hit_flag = [False]

        def on_hit(x, y):
            hit_flag[0] = True

        p_mgr.spawn_laser_bolt(start_x=100, start_y=500, target_x=100, target_y=100, speed=2000, on_hit=on_hit)
        self.assertEqual(len(p_mgr.bolts), 1)

        # Update by 0.3s (distance 400px traveled at 2000px/s takes 0.2s)
        p_mgr.update(0.3)
        self.assertTrue(hit_flag[0])
        self.assertEqual(len(p_mgr.bolts), 0)

        # Powerup timers
        pow_mgr = PowerupManager()
        pow_mgr.chrono_slow_timer = 5.0
        self.assertTrue(pow_mgr.is_chrono_slow_active())
        pow_mgr.update(6.0)
        self.assertFalse(pow_mgr.is_chrono_slow_active())


if __name__ == "__main__":
    unittest.main()
