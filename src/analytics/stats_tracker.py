"""
Advanced Typing Analytics and Performance Tracking
Calculates standard WPM (5-char word convention), keystroke accuracy, word accuracy,
streaks, speed trends, and automated performance grading.
"""

import time
from typing import List, Dict, Any, Tuple


class StatsTracker:
    """Tracks typing speed, accuracy, streaks, and combat performance metrics."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Resets all metrics for a new game session."""
        self.start_time = time.time()
        self.active_typing_time = 0.0
        self._last_keystroke_time = None
        
        self.total_keystrokes = 0
        self.correct_keystrokes = 0
        self.incorrect_keystrokes = 0
        
        self.completed_words = 0
        self.missed_words = 0            # Rocks that hit the player or bottom
        self.uncorrected_errors = 0
        
        self.current_streak = 0
        self.longest_streak = 0
        self.current_combo = 1.0
        
        self.score = 0
        self.rocks_destroyed_by_type = {}
        
        # Periodic samples for speed consistency graphs [(timestamp, current_wpm, accuracy)]
        self.wpm_history: List[Tuple[float, float, float]] = []
        self._last_sample_time = self.start_time
        self.peak_wpm = 0.0

    def record_keystroke(self, is_correct: bool, is_backspace: bool = False):
        """Records a single keystroke event."""
        now = time.time()
        if self._last_keystroke_time is not None:
            delta = now - self._last_keystroke_time
            # Count towards active typing time if pause is less than 3 seconds
            if delta < 3.0:
                self.active_typing_time += delta
            else:
                self.active_typing_time += 0.5  # Count initial pause tap as minimal time
        self._last_keystroke_time = now

        if not is_backspace:
            self.total_keystrokes += 1
            if is_correct:
                self.correct_keystrokes += 1
            else:
                self.incorrect_keystrokes += 1
                self.uncorrected_errors += 1
                self.current_streak = 0  # Reset streak on mistake

        # Update periodic history sample
        if now - self._last_sample_time >= 1.5:
            wpm = self.get_net_wpm()
            acc = self.get_accuracy()
            self.wpm_history.append((now - self.start_time, wpm, acc))
            if wpm > self.peak_wpm:
                self.peak_wpm = wpm
            self._last_sample_time = now

    def record_word_completed(self, word: str, rock_type: str, points: int):
        """Called when a falling rock's word is successfully typed and destroyed."""
        self.completed_words += 1
        self.current_streak += 1
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
            
        self.rocks_destroyed_by_type[rock_type] = self.rocks_destroyed_by_type.get(rock_type, 0) + 1
        self.score += points

    def record_word_missed(self, rock_type: str):
        """Called when a rock impacts the player or reaches the danger line."""
        self.missed_words += 1
        self.current_streak = 0

    def get_elapsed_seconds(self) -> float:
        """Returns total elapsed session time in seconds."""
        return max(0.1, time.time() - self.start_time)

    def get_effective_typing_minutes(self) -> float:
        """
        Returns active typing duration in minutes.
        Ensures a fair WPM formula that doesn't penalize waiting for rocks to spawn,
        while maintaining standard typing metrics.
        """
        # Active typing time with a floor based on elapsed time to prevent infinite WPM
        effective_sec = max(1.5, self.active_typing_time, self.get_elapsed_seconds() * 0.4)
        return effective_sec / 60.0

    def get_gross_wpm(self) -> float:
        """
        Gross Words Per Minute:
        (Total Characters Typed / 5) / (Time in Minutes)
        """
        mins = self.get_effective_typing_minutes()
        if mins <= 0 or self.correct_keystrokes == 0:
            return 0.0
        words = self.correct_keystrokes / 5.0
        return round(words / mins, 1)

    def get_net_wpm(self) -> float:
        """
        Net Words Per Minute:
        ((Correct Characters Typed - Errors) / 5) / (Time in Minutes)
        """
        mins = self.get_effective_typing_minutes()
        if mins <= 0 or self.correct_keystrokes == 0:
            return 0.0
        net_chars = max(0, self.correct_keystrokes - (self.incorrect_keystrokes * 0.5))
        words = net_chars / 5.0
        return round(max(0.0, words / mins), 1)

    def get_accuracy(self) -> float:
        """Keystroke accuracy percentage."""
        if self.total_keystrokes == 0:
            return 100.0
        acc = (self.correct_keystrokes / self.total_keystrokes) * 100.0
        return round(max(0.0, min(100.0, acc)), 1)

    def get_word_accuracy(self) -> float:
        """Percentage of successfully typed rocks vs total target encounters."""
        total = self.completed_words + self.missed_words
        if total == 0:
            return 100.0
        return round((self.completed_words / total) * 100.0, 1)

    def calculate_grade(self) -> Tuple[str, str]:
        """
        Calculates an arcade performance grade (S+, S, A, B, C, D)
        and returns (Grade, Recommendation).
        """
        wpm = self.get_net_wpm()
        acc = self.get_accuracy()

        if wpm >= 75 and acc >= 96:
            grade = "S+"
            feedback = "Legendary Cyber-Gunner! Godlike typing speed and pinpoint precision under fire."
        elif wpm >= 60 and acc >= 93:
            grade = "S"
            feedback = "Elite Outpost Defender! Exceptional speed and composure across all hazard waves."
        elif wpm >= 45 and acc >= 88:
            grade = "A"
            feedback = "Veteran Survivor! Swift reflexes and solid accuracy. Keep up the high combos."
        elif wpm >= 30 and acc >= 82:
            grade = "B"
            feedback = "Skilled Defender. Good rhythm! Focus on prioritizing fast meteors before they hit."
        elif wpm >= 18 and acc >= 75:
            grade = "C"
            feedback = "Promising Recruit. Work on steady finger placement to reduce typos on longer words."
        else:
            grade = "D"
            feedback = "Combat Training Recommended. Try Practice Mode with slower fall speed to build muscle memory."

        return grade, feedback

    def get_summary_dict(self) -> Dict[str, Any]:
        """Returns a complete dictionary of session metrics for storage or display."""
        grade, feedback = self.calculate_grade()
        elapsed = self.get_elapsed_seconds()
        return {
            "score": self.score,
            "net_wpm": self.get_net_wpm(),
            "gross_wpm": self.get_gross_wpm(),
            "peak_wpm": round(self.peak_wpm, 1),
            "accuracy": self.get_accuracy(),
            "word_accuracy": self.get_word_accuracy(),
            "completed_words": self.completed_words,
            "missed_words": self.missed_words,
            "correct_keystrokes": self.correct_keystrokes,
            "incorrect_keystrokes": self.incorrect_keystrokes,
            "longest_streak": self.longest_streak,
            "survival_time": round(elapsed, 1),
            "grade": grade,
            "feedback": feedback,
            "rocks_destroyed": sum(self.rocks_destroyed_by_type.values()),
        }
