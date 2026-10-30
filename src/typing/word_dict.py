"""
Word Bank and Dictionary Manager for TypeStrike
Loads wordlists, categorizes vocabulary by difficulty and length,
and provides collision-free word selection for falling rocks.
"""

import os
import random
from typing import List, Set, Optional
from src.config import (
    WORDS_DIR,
    ROCK_TYPE_NORMAL,
    ROCK_TYPE_FAST,
    ROCK_TYPE_ARMORED,
    ROCK_TYPE_EXPLOSIVE,
    ROCK_TYPE_POWERUP,
    ROCK_TYPE_BOSS,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_EXPERT,
)


class WordBank:
    """Manages active dictionaries and selects words for rock hazards."""

    def __init__(self):
        self.easy_words: List[str] = []
        self.normal_words: List[str] = []
        self.hard_words: List[str] = []
        self.tech_words: List[str] = []
        self.boss_phrases: List[str] = []
        self._load_all_words()

    def _load_file(self, filename: str) -> List[str]:
        path = os.path.join(WORDS_DIR, filename)
        if not os.path.exists(path):
            print(f"[WordBank] Word file not found at {path}, using built-in fallback.")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
            return words
        except Exception as e:
            print(f"[WordBank] Error reading {filename}: {e}")
            return []

    def _load_all_words(self):
        self.easy_words = self._load_file("easy.txt")
        self.normal_words = self._load_file("normal.txt")
        self.hard_words = self._load_file("hard.txt")
        self.tech_words = self._load_file("tech.txt")
        self.boss_phrases = self._load_file("boss_phrases.txt")

        # Fallback words if files were somehow missing or empty
        if not self.easy_words:
            self.easy_words = ["fire", "iron", "rock", "bold", "fast", "nova", "warp", "grit", "star", "glow"]
        if not self.normal_words:
            self.normal_words = ["strike", "plasma", "shield", "cannon", "hazard", "meteor", "vortex", "crater"]
        if not self.hard_words:
            self.hard_words = ["cataclysm", "annihilate", "interstellar", "juggernaut", "indomitable", "trajectory"]
        if not self.tech_words:
            self.tech_words = ["algorithm", "compiler", "recursion", "database", "interface", "parameter", "binary"]
        if not self.boss_phrases:
            self.boss_phrases = ["strike the core", "shatter the barrier", "defend the outpost", "fire all turrets"]

    def get_word_for_rock(
        self,
        rock_type: str,
        difficulty: str = DIFFICULTY_NORMAL,
        used_words: Optional[Set[str]] = None,
        use_tech_words: bool = False
    ) -> str:
        """
        Selects an appropriate, non-duplicate word for a given rock type and difficulty.
        """
        if used_words is None:
            used_words = set()

        if rock_type == ROCK_TYPE_BOSS:
            candidates = [p for p in self.boss_phrases if p not in used_words]
            return random.choice(candidates if candidates else self.boss_phrases)

        # Build candidate pool based on rock type and difficulty
        if rock_type == ROCK_TYPE_FAST:
            # Fast rocks always get shorter words so they are quick reaction tests
            pool = self.easy_words if self.easy_words else self.normal_words
            candidates = [w for w in pool if 3 <= len(w) <= 5 and w not in used_words]
        elif rock_type == ROCK_TYPE_ARMORED:
            # Armored rocks get longer words
            if difficulty in (DIFFICULTY_HARD, DIFFICULTY_EXPERT):
                pool = self.hard_words + (self.tech_words if use_tech_words else [])
            else:
                pool = self.normal_words + self.hard_words
            candidates = [w for w in pool if len(w) >= 6 and w not in used_words]
        elif rock_type in (ROCK_TYPE_POWERUP, ROCK_TYPE_EXPLOSIVE):
            # Tactical rocks get clean distinct 4-6 letter words
            pool = self.easy_words + self.normal_words
            candidates = [w for w in pool if 4 <= len(w) <= 6 and w not in used_words]
        else:
            # Normal rocks: match difficulty preset
            if difficulty == DIFFICULTY_EASY:
                pool = self.easy_words
            elif difficulty == DIFFICULTY_NORMAL:
                pool = self.easy_words + self.normal_words
            elif difficulty == DIFFICULTY_HARD:
                pool = self.normal_words + self.hard_words
            else:  # EXPERT
                pool = self.hard_words + (self.tech_words if use_tech_words else [])
            
            candidates = [w for w in pool if w not in used_words]

        # Avoid prefix collision if possible with already falling rocks:
        used_prefixes = {w[0] for w in used_words if w}
        distinct_first_letter = [w for w in candidates if w and w[0] not in used_prefixes]
        if distinct_first_letter:
            return random.choice(distinct_first_letter)

        if candidates:
            return random.choice(candidates)

        # Fallback to general random choice from normal words
        fallback_pool = self.normal_words if self.normal_words else ["strike", "shield", "laser"]
        return random.choice(fallback_pool)
