"""
Procedural Sound Generator for TypeStrike
Generates synthetic retro/arcade sound effects directly using NumPy,
converting them to pygame.mixer.Sound objects without requiring external audio files.
"""

import math
import numpy as np
import pygame


def _to_sound(audio: np.ndarray) -> pygame.mixer.Sound:
    """Clips audio, converts to int16, matches mixer channels (stereo/mono), and returns Sound."""
    audio = np.clip(audio, -1.0, 1.0)
    audio = (audio * 32767).astype(np.int16)
    init_res = pygame.mixer.get_init()
    if init_res and init_res[2] == 2 and audio.ndim == 1:
        audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(audio)


def generate_keystroke_sound(sample_rate=44100):
    """Short crisp mechanical typewriter/laser chirp."""
    duration = 0.035
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq = np.linspace(1400, 700, len(t))
    wave = np.sin(2 * np.pi * freq * t)
    # Quick exponential decay envelope
    envelope = np.exp(-t * 120)
    audio = wave * envelope
    # Add subtle click noise at the attack
    noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 250) * 0.35
    audio = audio + noise
    return _to_sound(audio)


def generate_typo_sound(sample_rate=44100):
    """Low discordant buzzer indicating a typing mistake."""
    duration = 0.09
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq1 = 150
    freq2 = 195  # Dissonant minor second
    wave = 0.5 * np.sin(2 * np.pi * freq1 * t) + 0.5 * np.sin(2 * np.pi * freq2 * t)
    # Square clipping for rough buzzer texture
    wave = np.clip(wave * 2.0, -0.8, 0.8)
    envelope = np.exp(-t * 25)
    audio = wave * envelope
    return _to_sound(audio)


def generate_laser_sound(sample_rate=44100):
    """Plasma cannon blast with fast downward pitch envelope."""
    duration = 0.14
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq = 1100 * np.exp(-t * 22)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    wave = np.sin(phase) + 0.25 * np.sin(3 * phase)
    envelope = np.exp(-t * 18)
    audio = wave * envelope
    return _to_sound(audio)


def generate_explosion_sound(sample_rate=44100):
    """Deep thunderous rock shatter with sub-bass impact and noise."""
    duration = 0.35
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    # Sub-bass rumble
    sub = np.sin(2 * np.pi * np.linspace(130, 35, len(t)) * t) * 0.8
    wave = noise * 0.6 + sub * 0.4
    envelope = np.exp(-t * 8)
    audio = wave * envelope
    return _to_sound(audio)


def generate_powerup_sound(sample_rate=44100):
    """Bright ascending crystal chime."""
    duration = 0.32
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # 4 quick ascending notes: C5, E5, G5, C6
    notes = [523.25, 659.25, 783.99, 1046.50]
    sub_len = len(t) // len(notes)
    audio = np.zeros_like(t)
    for i, freq in enumerate(notes):
        start = i * sub_len
        end = start + sub_len if i < len(notes) - 1 else len(t)
        sub_t = t[start:end] - t[start]
        note_wave = np.sin(2 * np.pi * freq * sub_t) + 0.3 * np.sin(4 * np.pi * freq * sub_t)
        note_env = np.exp(-sub_t * 14)
        audio[start:end] = note_wave * note_env
    return _to_sound(audio)


def generate_shield_sound(sample_rate=44100):
    """High-energy shield deflection hum and ring."""
    duration = 0.22
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq = np.linspace(800, 350, len(t))
    wave = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 1.5 * t)
    envelope = np.exp(-t * 12)
    audio = wave * envelope
    return _to_sound(audio)


def generate_emp_sound(sample_rate=44100):
    """Massive screen-clearing EMP blast wave."""
    duration = 0.65
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sweep = np.sin(2 * np.pi * (np.linspace(250, 40, len(t))) * t)
    noise = np.random.uniform(-0.8, 0.8, len(t))
    wave = sweep * 0.7 + noise * 0.5
    envelope = (1.0 - t / duration) ** 1.8
    audio = wave * envelope
    return _to_sound(audio)


def generate_dodge_sound(sample_rate=44100):
    """Fast air whoosh / thruster burst."""
    duration = 0.18
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    # Filter-like envelope by modulating with a sine rise & fall
    mod = np.sin(np.pi * t / duration) ** 2
    audio = noise * mod * 0.7
    return _to_sound(audio)


def generate_game_over_sound(sample_rate=44100):
    """Dramatic descending arcade game-over tones."""
    duration = 0.85
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    notes = [440, 392, 349.23, 293.66, 220]
    sub_len = len(t) // len(notes)
    audio = np.zeros_like(t)
    for i, freq in enumerate(notes):
        start = i * sub_len
        end = start + sub_len if i < len(notes) - 1 else len(t)
        sub_t = t[start:end] - t[start]
        note_wave = 0.7 * np.sin(2 * np.pi * freq * sub_t) + 0.3 * np.sin(4 * np.pi * freq * sub_t)
        note_env = np.exp(-sub_t * 6)
        audio[start:end] = note_wave * note_env
    return _to_sound(audio)


def generate_combo_fanfare(sample_rate=44100):
    """Pleasing high-tech milestone chime."""
    duration = 0.30
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.6 * np.sin(2 * np.pi * 880 * t) + 0.4 * np.sin(2 * np.pi * 1320 * t)
    envelope = np.exp(-t * 9)
    audio = wave * envelope
    return _to_sound(audio)
