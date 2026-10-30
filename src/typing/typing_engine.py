"""
Intelligent Typing Engine for TypeStrike
Handles real-time keystroke processing, smart target acquisition and lock-on,
character-by-character validation, typo alerts, and word completion callbacks.
"""

from typing import List, Optional, Any, Callable
import pygame
from src.analytics.stats_tracker import StatsTracker
from src.audio.audio_manager import AudioManager


class TypingEngine:
    """Manages active target tracking, keystroke parsing, and visual typing states."""

    def __init__(self, stats_tracker: StatsTracker, audio_manager: AudioManager):
        self.stats = stats_tracker
        self.audio = audio_manager
        
        self.locked_target: Optional[Any] = None  # Reference to the active Rock object
        self.typed_buffer: str = ""               # Currently matched prefix for locked target
        
        # Visual typo flash state
        self.typo_flash_timer: float = 0.0
        self.last_invalid_char: str = ""

        # Callbacks for game events
        self.on_word_completed: Optional[Callable[[Any], None]] = None
        self.on_typo: Optional[Callable[[Any, str], None]] = None

    def reset(self):
        """Resets the typing state and releases target lock."""
        self.locked_target = None
        self.typed_buffer = ""
        self.typo_flash_timer = 0.0
        self.last_invalid_char = ""

    def update(self, dt: float):
        """Updates animation timers like typo flashes."""
        if self.typo_flash_timer > 0:
            self.typo_flash_timer = max(0.0, self.typo_flash_timer - dt)

        # Check if locked target was destroyed or despawned elsewhere
        if self.locked_target is not None:
            if not self.locked_target.is_active or self.locked_target.is_destroyed:
                self.unlock_target()

    def unlock_target(self):
        """Releases the currently targeted rock."""
        if self.locked_target:
            self.locked_target.set_targeted(False)
            self.locked_target.typed_prefix_len = 0
        self.locked_target = None
        self.typed_buffer = ""

    def process_key_event(self, event: pygame.event.Event, active_rocks: List[Any]) -> bool:
        """
        Processes a KEYDOWN event. Returns True if input was consumed as typing.
        """
        # Handle Backspace
        if event.key == pygame.K_BACKSPACE:
            if self.locked_target and self.typed_buffer:
                self.typed_buffer = self.typed_buffer[:-1]
                self.locked_target.typed_prefix_len = len(self.typed_buffer)
                self.stats.record_keystroke(is_correct=False, is_backspace=True)
                self.audio.play_sfx("keystroke")
                if not self.typed_buffer:
                    self.unlock_target()
                return True
            return False

        # Handle Tab to manually drop target lock
        if event.key == pygame.K_TAB:
            if self.locked_target:
                self.unlock_target()
                return True
            return False

        # Only process printable text keys (letters, numbers, space for phrases)
        char = event.unicode
        if not char or not (char.isalnum() or char == " "):
            return False

        char_lower = char.lower()

        # If a rock is already locked:
        if self.locked_target is not None and self.locked_target.is_active:
            target_word = self.locked_target.target_word
            next_idx = len(self.typed_buffer)

            if next_idx < len(target_word) and target_word[next_idx] == char_lower:
                # Correct next character!
                self.typed_buffer += char_lower
                self.locked_target.typed_prefix_len = len(self.typed_buffer)
                self.stats.record_keystroke(is_correct=True)
                self.audio.play_sfx("keystroke")

                # Check if word is completed!
                if len(self.typed_buffer) == len(target_word):
                    target = self.locked_target
                    self.unlock_target()
                    if self.on_word_completed:
                        self.on_word_completed(target)
                return True
            else:
                # Typo on active target!
                self.typo_flash_timer = 0.25
                self.last_invalid_char = char_lower
                self.stats.record_keystroke(is_correct=False)
                self.audio.play_sfx("typo")
                if self.on_typo and self.locked_target:
                    self.on_typo(self.locked_target, char_lower)
                return True

        # If NO rock is locked, search for a falling rock starting with this char:
        candidates = [
            r for r in active_rocks 
            if r.is_active and not r.is_destroyed and r.target_word.startswith(char_lower)
        ]

        if candidates:
            # Prioritize the candidate closest to the bottom (highest Y position = most urgent danger!)
            candidates.sort(key=lambda r: r.pos_y, reverse=True)
            chosen_rock = candidates[0]
            
            self.locked_target = chosen_rock
            chosen_rock.set_targeted(True)
            self.typed_buffer = char_lower
            chosen_rock.typed_prefix_len = 1
            
            self.stats.record_keystroke(is_correct=True)
            self.audio.play_sfx("keystroke")

            # Check if it was a 1-character target
            if len(self.typed_buffer) == len(chosen_rock.target_word):
                target = self.locked_target
                self.unlock_target()
                if self.on_word_completed:
                    self.on_word_completed(target)
            return True
        else:
            # Stray keystroke with no matching rock on screen
            self.stats.record_keystroke(is_correct=False)
            self.audio.play_sfx("typo")
            self.typo_flash_timer = 0.15
            return False
