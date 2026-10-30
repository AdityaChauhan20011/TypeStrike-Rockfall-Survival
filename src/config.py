"""
TypeStrike: Rockfall Survival - Configuration and Constants
Defines global configurations, display constants, color palettes, difficulty presets,
and gameplay tuning parameters.
"""

import os

# --- Display & Window ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "TypeStrike: Rockfall Survival"
VERSION = "1.0.0"

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
WORDS_DIR = os.path.join(ASSETS_DIR, "words")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "typestrike.db")

# --- Theme & Color Palette (Futuristic Cyber-Survival) ---
COLOR_BG_DARK = (10, 12, 22)
COLOR_BG_PANEL = (18, 22, 38)
COLOR_BG_PANEL_TRANSPARENT = (18, 22, 38, 210)
COLOR_ACCENT_CYAN = (0, 240, 255)
COLOR_ACCENT_MAGENTA = (255, 0, 128)
COLOR_ACCENT_GOLD = (255, 204, 0)
COLOR_ACCENT_GREEN = (0, 255, 136)
COLOR_ACCENT_RED = (255, 50, 70)
COLOR_ACCENT_ORANGE = (255, 120, 0)
COLOR_ACCENT_PURPLE = (170, 60, 255)
COLOR_WHITE = (245, 250, 255)
COLOR_GRAY_LIGHT = (180, 195, 215)
COLOR_GRAY_MID = (90, 105, 130)
COLOR_GRAY_DARK = (35, 42, 60)

# Health & Shield Colors
COLOR_HEALTH_FULL = (0, 240, 150)
COLOR_HEALTH_MID = (255, 190, 0)
COLOR_HEALTH_LOW = (255, 50, 60)
COLOR_SHIELD = (0, 180, 255)
COLOR_DODGE = (220, 100, 255)

# Text Highlight Colors for Typing Engine
COLOR_TYPED_MATCH = (0, 255, 170)        # Green/Cyan for correct typed prefix
COLOR_UNTYPED_REST = (235, 245, 255)     # Crisp white for remaining letters
COLOR_TYPO_ALERT = (255, 45, 85)         # Neon crimson for typo flash
COLOR_TARGET_PILL = (25, 32, 55, 230)    # Dark frosted background behind word
COLOR_TARGET_BORDER = (0, 240, 255)      # Cyan border for locked target
COLOR_NORMAL_BORDER = (70, 85, 120)      # Gray border for inactive targets

# --- Rock Types ---
ROCK_TYPE_NORMAL = "normal"
ROCK_TYPE_FAST = "fast"
ROCK_TYPE_ARMORED = "armored"
ROCK_TYPE_EXPLOSIVE = "explosive"
ROCK_TYPE_POWERUP = "powerup"
ROCK_TYPE_BOSS = "boss"

# --- Powerup Types ---
POWERUP_SHIELD = "shield"
POWERUP_SLOW = "slow"
POWERUP_EMP = "emp"
POWERUP_HEAL = "heal"
POWERUP_DOUBLE_SCORE = "double_score"

# --- Game Modes ---
MODE_SURVIVAL = "survival"
MODE_PRACTICE = "practice"
MODE_TIME_ATTACK = "time_attack"
MODE_ENDLESS = "endless"

# --- Difficulty Settings ---
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"
DIFFICULTY_EXPERT = "expert"

DIFFICULTY_CONFIGS = {
    DIFFICULTY_EASY: {
        "name": "Recruit (Easy)",
        "desc": "Slower rocks, shorter words (3-5 letters), generous reaction times.",
        "fall_speed_min": 45,
        "fall_speed_max": 75,
        "spawn_interval": 2.8,       # seconds between spawns
        "min_word_len": 3,
        "max_word_len": 5,
        "max_active_rocks": 4,
        "damage_multiplier": 0.75,
        "score_multiplier": 1.0,
        "rock_weights": {
            ROCK_TYPE_NORMAL: 0.65,
            ROCK_TYPE_FAST: 0.10,
            ROCK_TYPE_ARMORED: 0.05,
            ROCK_TYPE_EXPLOSIVE: 0.10,
            ROCK_TYPE_POWERUP: 0.10,
        }
    },
    DIFFICULTY_NORMAL: {
        "name": "Veteran (Normal)",
        "desc": "Balanced speed, 4-7 letter words, varied tactical hazards.",
        "fall_speed_min": 65,
        "fall_speed_max": 105,
        "spawn_interval": 2.1,
        "min_word_len": 4,
        "max_word_len": 7,
        "max_active_rocks": 6,
        "damage_multiplier": 1.0,
        "score_multiplier": 1.5,
        "rock_weights": {
            ROCK_TYPE_NORMAL: 0.45,
            ROCK_TYPE_FAST: 0.20,
            ROCK_TYPE_ARMORED: 0.15,
            ROCK_TYPE_EXPLOSIVE: 0.10,
            ROCK_TYPE_POWERUP: 0.10,
        }
    },
    DIFFICULTY_HARD: {
        "name": "Elite (Hard)",
        "desc": "Rapid rockfall, longer vocabulary (5-10 letters), aggressive meteors.",
        "fall_speed_min": 90,
        "fall_speed_max": 145,
        "spawn_interval": 1.6,
        "min_word_len": 5,
        "max_word_len": 9,
        "max_active_rocks": 8,
        "damage_multiplier": 1.25,
        "score_multiplier": 2.0,
        "rock_weights": {
            ROCK_TYPE_NORMAL: 0.35,
            ROCK_TYPE_FAST: 0.25,
            ROCK_TYPE_ARMORED: 0.20,
            ROCK_TYPE_EXPLOSIVE: 0.12,
            ROCK_TYPE_POWERUP: 0.08,
        }
    },
    DIFFICULTY_EXPERT: {
        "name": "Cyber-Titan (Expert)",
        "desc": "Extremely fast blitz, complex terminology, demanding precision typing.",
        "fall_speed_min": 115,
        "fall_speed_max": 180,
        "spawn_interval": 1.25,
        "min_word_len": 6,
        "max_word_len": 12,
        "max_active_rocks": 10,
        "damage_multiplier": 1.5,
        "score_multiplier": 3.0,
        "rock_weights": {
            ROCK_TYPE_NORMAL: 0.25,
            ROCK_TYPE_FAST: 0.30,
            ROCK_TYPE_ARMORED: 0.25,
            ROCK_TYPE_EXPLOSIVE: 0.12,
            ROCK_TYPE_POWERUP: 0.08,
        }
    }
}

# --- Player Attributes ---
PLAYER_MAX_HEALTH = 100
PLAYER_STARTING_LIVES = 3
PLAYER_STARTING_SHIELD = 50
PLAYER_MAX_SHIELD = 100
PLAYER_MOVE_SPEED = 400.0            # pixels per second when sliding
PLAYER_DODGE_SPEED = 700.0           # pixels per second burst
PLAYER_DODGE_DURATION = 0.25         # seconds
PLAYER_DODGE_COOLDOWN = 1.2          # seconds
PLAYER_INVULN_TIME = 1.5             # invulnerability seconds after taking hit

# --- Scoring System ---
BASE_SCORE_PER_CHAR = 10
BASE_WORD_BONUS = 50
ACCURACY_PERFECT_BONUS = 100
ROCK_POINTS = {
    ROCK_TYPE_NORMAL: 100,
    ROCK_TYPE_FAST: 180,
    ROCK_TYPE_ARMORED: 250,
    ROCK_TYPE_EXPLOSIVE: 200,
    ROCK_TYPE_POWERUP: 150,
    ROCK_TYPE_BOSS: 1000,
}

# Combo Multiplier thresholds (consecutive words without typo)
COMBO_THRESHOLDS = [
    (0, 1.0),
    (5, 1.25),
    (10, 1.5),
    (15, 2.0),
    (25, 2.5),
    (40, 3.0),
    (60, 4.0),
]

# EMP Charge: points per word typed towards charging EMP bomb (max 100)
EMP_CHARGE_PER_WORD = 10
EMP_MAX_CHARGE = 100

# Time Attack Mode Duration in seconds
TIME_ATTACK_DURATION = 120  # 2 minutes

# Audio settings
DEFAULT_MASTER_VOLUME = 0.8
DEFAULT_SFX_VOLUME = 0.8
DEFAULT_MUSIC_VOLUME = 0.5
