"""
Audio Manager for TypeStrike
Handles sound effects playback, volume levels, synthesizer caching,
and ambient sci-fi music loops with zero-crash fallbacks.
"""

import pygame
import numpy as np
from src.config import DEFAULT_MASTER_VOLUME, DEFAULT_SFX_VOLUME, DEFAULT_MUSIC_VOLUME
from src.audio.sound_gen import (
    generate_keystroke_sound,
    generate_typo_sound,
    generate_laser_sound,
    generate_explosion_sound,
    generate_powerup_sound,
    generate_shield_sound,
    generate_emp_sound,
    generate_dodge_sound,
    generate_game_over_sound,
    generate_combo_fanfare,
)


class DummySound:
    """Fallback sound object when audio is unavailable or muted."""
    def play(self, *args, **kwargs):
        pass
    def set_volume(self, *args, **kwargs):
        pass
    def stop(self):
        pass


class AudioManager:
    """Central audio controller for TypeStrike."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def __init__(self):
        self.enabled = True
        self.master_volume = DEFAULT_MASTER_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sounds = {}
        self.bg_channel = None
        self.bg_sound = None
        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
            pygame.mixer.set_num_channels(24)
            self.enabled = True
            self._load_sounds()
            self._build_ambient_music()
        except Exception as e:
            print(f"[AudioManager] Audio mixer initialization failed or disabled: {e}")
            self.enabled = False

    def _load_sounds(self):
        """Synthesize and cache all in-game sound effects."""
        if not self.enabled:
            return
        try:
            self.sounds = {
                "keystroke": generate_keystroke_sound(),
                "typo": generate_typo_sound(),
                "laser": generate_laser_sound(),
                "explosion": generate_explosion_sound(),
                "powerup": generate_powerup_sound(),
                "shield": generate_shield_sound(),
                "emp": generate_emp_sound(),
                "dodge": generate_dodge_sound(),
                "game_over": generate_game_over_sound(),
                "combo": generate_combo_fanfare(),
            }
            self._update_all_sound_volumes()
        except Exception as e:
            print(f"[AudioManager] Warning: procedural sound synthesis error: {e}")
            self.sounds = {}

    def _build_ambient_music(self):
        """Generates an atmospheric cyber-electronic ambient loop."""
        if not self.enabled:
            return
        try:
            sample_rate = 44100
            duration = 8.0  # 8-second seamless looping atmospheric theme
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            
            # Deep rhythmic sub-bass pulse (A1, 55Hz & D2, 73.4Hz)
            pulse_mod = (np.sin(2 * np.pi * 2.0 * t) > 0).astype(float) * 0.4 + 0.6
            sub_bass = np.sin(2 * np.pi * 55.0 * t) * 0.45 * pulse_mod
            
            # Warm analog synth pad (minor triad: A3, C4, E4)
            pad1 = np.sin(2 * np.pi * 220.0 * t) * 0.15
            pad2 = np.sin(2 * np.pi * 261.63 * t) * 0.12
            pad3 = np.sin(2 * np.pi * 329.63 * t) * 0.10
            pad = (pad1 + pad2 + pad3) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t))
            
            # Gentle space cyber arpeggio
            arp_freqs = [440, 523.25, 659.25, 783.99]
            arp = np.zeros_like(t)
            steps = len(arp_freqs) * 4
            step_len = len(t) // steps
            for i in range(steps):
                f = arp_freqs[i % len(arp_freqs)]
                idx_start = i * step_len
                idx_end = idx_start + step_len if i < steps - 1 else len(t)
                sub_t = t[idx_start:idx_end] - t[idx_start]
                arp[idx_start:idx_end] = np.sin(2 * np.pi * f * sub_t) * np.exp(-sub_t * 6) * 0.12

            total = sub_bass + pad + arp
            # Apply fade in and fade out at endpoints for click-free loop
            fade_len = int(sample_rate * 0.1)
            total[:fade_len] *= np.linspace(0, 1, fade_len)
            total[-fade_len:] *= np.linspace(1, 0, fade_len)

            total = np.clip(total * 0.5, -1.0, 1.0)
            audio_stereo = np.column_stack((total, total))
            audio_int16 = (audio_stereo * 32767).astype(np.int16)
            
            self.bg_sound = pygame.sndarray.make_sound(audio_int16)
            self.bg_sound.set_volume(self.master_volume * self.music_volume)
        except Exception as e:
            print(f"[AudioManager] Ambient music loop creation skipped: {e}")
            self.bg_sound = None

    def start_music(self):
        """Start playing ambient cyber background loop."""
        if not self.enabled or self.bg_sound is None:
            return
        try:
            if self.bg_channel is None or not self.bg_channel.get_busy():
                self.bg_channel = self.bg_sound.play(loops=-1, fade_ms=1000)
        except Exception:
            pass

    def stop_music(self):
        """Stop background music."""
        if self.bg_channel:
            try:
                self.bg_channel.stop()
            except Exception:
                pass

    def play_sfx(self, sound_name: str):
        """Play a registered sound effect."""
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def _update_all_sound_volumes(self):
        """Update volumes for all loaded sound effects."""
        effective_sfx = self.master_volume * self.sfx_volume
        for sound in self.sounds.values():
            try:
                sound.set_volume(effective_sfx)
            except Exception:
                pass
        if self.bg_sound:
            try:
                self.bg_sound.set_volume(self.master_volume * self.music_volume)
            except Exception:
                pass

    def set_master_volume(self, vol: float):
        self.master_volume = max(0.0, min(1.0, vol))
        self._update_all_sound_volumes()

    def set_sfx_volume(self, vol: float):
        self.sfx_volume = max(0.0, min(1.0, vol))
        self._update_all_sound_volumes()

    def set_music_volume(self, vol: float):
        self.music_volume = max(0.0, min(1.0, vol))
        self._update_all_sound_volumes()
