"""
Core Gameplay Scene and State Controller for TypeStrike
Coordinates player mechanics, rock hazard spawning, typing combat,
collision detection, power-ups, wave progression, and game-over transitions.
"""

import math
import random
import time
from typing import List, Dict, Optional, Tuple, Callable, Any
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_GOLD,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    ROCK_TYPE_NORMAL,
    ROCK_TYPE_FAST,
    ROCK_TYPE_ARMORED,
    ROCK_TYPE_EXPLOSIVE,
    ROCK_TYPE_POWERUP,
    ROCK_TYPE_BOSS,
    MODE_SURVIVAL,
    MODE_PRACTICE,
    MODE_TIME_ATTACK,
    MODE_ENDLESS,
    DIFFICULTY_NORMAL,
    DIFFICULTY_CONFIGS,
    COMBO_THRESHOLDS,
    TIME_ATTACK_DURATION,
)
from src.entities.player import Player
from src.entities.rock import Rock
from src.entities.projectile import ProjectileManager
from src.entities.particle import ParticleManager
from src.entities.powerup import PowerupManager
from src.typing.word_dict import WordBank
from src.typing.typing_engine import TypingEngine
from src.analytics.stats_tracker import StatsTracker
from src.audio.audio_manager import AudioManager
from src.engine.background import Background
from src.ui.hud import HUD
from src.ui.components import Button


class GameScene:
    """Manages active gameplay session, hazard spawning, and combat resolution."""

    def __init__(
        self,
        fonts: Dict[str, pygame.font.Font],
        audio_manager: AudioManager,
        word_bank: WordBank,
        on_game_over: Callable[[Dict[str, Any]], None],
        on_quit_to_menu: Optional[Callable[[], None]] = None,
    ):
        self.fonts = fonts
        self.audio = audio_manager
        self.word_bank = word_bank
        self.on_game_over = on_game_over
        self.on_quit_to_menu = on_quit_to_menu

        self.background = Background()
        self.player = Player()
        self.projectile_mgr = ProjectileManager()
        self.particle_mgr = ParticleManager()
        self.powerup_mgr = PowerupManager()
        self.stats = StatsTracker()
        self.typing_engine = TypingEngine(self.stats, self.audio)
        self.hud = HUD(self.fonts)

        # Wire typing engine callbacks
        self.typing_engine.on_word_completed = self._on_word_completed
        self.typing_engine.on_typo = self._on_typo

        # Pause menu buttons
        font_btn = self.fonts.get("bold_18", self.fonts["default"])
        btn_w, btn_h = 260, 46
        cx = (SCREEN_WIDTH - btn_w) // 2
        self.btn_pause_resume = Button(
            (cx, SCREEN_HEIGHT // 2 + 5, btn_w, btn_h),
            "RESUME MISSION [ESC]",
            font_btn,
            on_click=self._resume_game,
            accent_color=COLOR_ACCENT_CYAN,
        )
        self.btn_pause_menu = Button(
            (cx, SCREEN_HEIGHT // 2 + 62, btn_w, btn_h),
            "RETURN TO MENU",
            font_btn,
            on_click=self._quit_to_menu,
            accent_color=COLOR_ACCENT_MAGENTA,
        )

        # Active gameplay state
        self.game_mode = MODE_SURVIVAL
        self.difficulty = DIFFICULTY_NORMAL
        self.diff_cfg = DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL]

        self.active_rocks: List[Rock] = []
        self.spawn_timer = 0.0
        self.wave_number = 1
        self.wave_timer = 0.0
        self.time_attack_remaining = float(TIME_ATTACK_DURATION)
        
        self.is_paused = False
        self.is_game_over = False

    def _resume_game(self):
        self.is_paused = False

    def _quit_to_menu(self):
        self.is_paused = False
        self.audio.stop_music()
        if self.on_quit_to_menu:
            self.on_quit_to_menu()

    def start_game(self, mode: str, difficulty: str):
        """Initializes a fresh game session for the chosen mode and difficulty."""
        self.game_mode = mode
        self.difficulty = difficulty
        self.diff_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])

        self.player.reset()
        self.projectile_mgr.reset()
        self.particle_mgr.reset()
        self.powerup_mgr.reset()
        self.stats.reset()
        self.typing_engine.reset()
        
        self.active_rocks.clear()
        self.spawn_timer = 0.5  # Quick initial rock spawn
        self.wave_number = 1
        self.wave_timer = 0.0
        self.time_attack_remaining = float(TIME_ATTACK_DURATION)
        
        self.is_paused = False
        self.is_game_over = False

        self.audio.start_music()
        
        # Announcement popup for mission start
        self.particle_mgr.spawn_floating_text(
            f"MISSION ENGAGED: {self.game_mode.upper()}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 80,
            COLOR_ACCENT_CYAN,
            self.fonts.get("bold_32", self.fonts["default"])
        )

    def get_combo_multiplier(self) -> float:
        """Calculates current combo score multiplier based on streak."""
        streak = self.stats.current_streak
        mult = 1.0
        for threshold, m in COMBO_THRESHOLDS:
            if streak >= threshold:
                mult = m
            else:
                break
        return mult

    def _on_word_completed(self, target_rock: Rock):
        """Callback from TypingEngine when a locked target's word is fully typed."""
        if not target_rock.is_active or target_rock.is_destroyed:
            return

        # Player shoots!
        self.player.trigger_fire()
        start_x, start_y = self.player.get_cannon_tip()
        self.audio.play_sfx("laser")

        # Spawn high-velocity laser bolt hitting the rock
        def on_hit_callback(hit_x, hit_y):
            self._resolve_rock_hit(target_rock)

        self.projectile_mgr.spawn_laser_bolt(
            start_x,
            start_y,
            target_rock.pos_x,
            target_rock.pos_y,
            on_hit=on_hit_callback
        )

    def _resolve_rock_hit(self, rock: Rock):
        """Resolves projectile damage on a rock target."""
        if not rock.is_active or rock.is_destroyed:
            return

        rock.current_health -= 1

        if rock.current_health <= 0:
            # Rock completely obliterated!
            rock.is_destroyed = True
            rock.is_active = False

            # Calculate points with combo & double score buff
            base_pts = rock.point_value
            combo = self.get_combo_multiplier()
            overcharge = 2.0 if self.powerup_mgr.is_double_score_active() else 1.0
            total_pts = int(base_pts * combo * overcharge * self.diff_cfg["score_multiplier"])

            self.stats.record_word_completed(rock.target_word, rock.rock_type, total_pts)
            self.player.gain_emp_charge(1)
            self.audio.play_sfx("explosion")
            self.background.trigger_shake(5.0, 0.2)

            # Spawn explosion debris and score popup
            rock_col = rock.get_color()
            self.particle_mgr.spawn_rock_explosion(rock.pos_x, rock.pos_y, rock_col, count=24)
            self.particle_mgr.spawn_laser_sparks(rock.pos_x, rock.pos_y, count=16)

            pts_str = f"+{total_pts}" if combo <= 1.0 else f"+{total_pts} ({combo}x)"
            self.particle_mgr.spawn_floating_text(
                pts_str,
                rock.pos_x,
                rock.pos_y - 20,
                COLOR_ACCENT_GOLD,
                self.fonts.get("bold_20", self.fonts["default"])
            )

            # Special Rock Effects:
            # 1. EXPLOSIVE: detonates all rocks within 220px radius!
            if rock.rock_type == ROCK_TYPE_EXPLOSIVE:
                self.particle_mgr.spawn_floating_text(
                    "MAGMA DETONATION!",
                    rock.pos_x,
                    rock.pos_y - 45,
                    COLOR_ACCENT_RED,
                    self.fonts.get("bold_18", self.fonts["default"])
                )
                self.background.trigger_shake(9.0, 0.35)
                for other in self.active_rocks:
                    if other is not rock and other.is_active and not other.is_destroyed:
                        dist = math.hypot(other.pos_x - rock.pos_x, other.pos_y - rock.pos_y)
                        if dist <= 220.0:
                            self._resolve_rock_hit(other)

            # 2. POWERUP: activates random player perk!
            elif rock.rock_type == ROCK_TYPE_POWERUP:
                self.powerup_mgr.activate_random_powerup(
                    self.player,
                    self.stats,
                    self.particle_mgr,
                    self.audio,
                    self.fonts.get("bold_18", self.fonts["default"])
                )

            # Check milestone streak audio/fanfare
            if self.stats.current_streak in (10, 20, 35, 50):
                self.audio.play_sfx("combo")
                self.particle_mgr.spawn_floating_text(
                    f"★ {self.stats.current_streak} WORD STREAK! ★",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 40,
                    COLOR_ACCENT_GOLD,
                    self.fonts.get("bold_24", self.fonts["default"])
                )
        else:
            # Armored rock partially damaged: reset typed buffer and pick secondary word phase
            self.audio.play_sfx("shield")
            self.particle_mgr.spawn_laser_sparks(rock.pos_x, rock.pos_y, count=12)
            self.particle_mgr.spawn_floating_text(
                "ARMOR BROKEN!",
                rock.pos_x,
                rock.pos_y - 20,
                COLOR_ACCENT_CYAN,
                self.fonts.get("bold_18", self.fonts["default"])
            )

    def _on_typo(self, target_rock: Rock, invalid_char: str):
        """Called when user makes an incorrect keystroke on an active target."""
        self.background.trigger_shake(2.5, 0.1)

    def trigger_emp_bomb(self):
        """Detonates screen-clearing EMP wave if fully charged."""
        if self.player.emp_charge >= self.player.max_emp_charge:
            self.player.emp_charge = 0.0
            self.audio.play_sfx("emp")
            self.background.trigger_shake(12.0, 0.45)
            self.projectile_mgr.spawn_emp_blast(self.player.x, self.player.y - 20)

            # Obliterate all active rocks
            for rock in list(self.active_rocks):
                if rock.is_active and not rock.is_destroyed:
                    rock.current_health = 0
                    self._resolve_rock_hit(rock)

            self.typing_engine.unlock_target()
            self.particle_mgr.spawn_floating_text(
                "EMP OBLITERATION WAVE!",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                COLOR_ACCENT_CYAN,
                self.fonts.get("bold_32", self.fonts["default"])
            )

    def _spawn_rock(self):
        """Spawns a new rock hazard at the top of the screen."""
        if len(self.active_rocks) >= self.diff_cfg["max_active_rocks"]:
            return

        # Choose rock type based on difficulty weights
        weights = self.diff_cfg["rock_weights"]
        r_types = list(weights.keys())
        r_probs = list(weights.values())
        
        # In Endless mode late waves, chance for a giant Boss rock!
        if self.game_mode == MODE_ENDLESS and self.wave_number % 5 == 0 and not any(r.rock_type == ROCK_TYPE_BOSS for r in self.active_rocks):
            chosen_type = ROCK_TYPE_BOSS
        else:
            chosen_type = random.choices(r_types, weights=r_probs, k=1)[0]

        # Determine non-duplicate word
        used_words = {r.target_word for r in self.active_rocks if r.is_active}
        word = self.word_bank.get_word_for_rock(chosen_type, self.difficulty, used_words=used_words)

        # Fall speed calculated with difficulty and wave scaling
        wave_speed_scale = 1.0 + (self.wave_number - 1) * 0.05
        base_speed = random.uniform(self.diff_cfg["fall_speed_min"], self.diff_cfg["fall_speed_max"]) * wave_speed_scale
        if chosen_type == ROCK_TYPE_FAST:
            base_speed *= 1.45
        elif chosen_type == ROCK_TYPE_ARMORED:
            base_speed *= 0.85
        elif chosen_type == ROCK_TYPE_BOSS:
            base_speed *= 0.55

        # Horizontal position (avoid spawning right on top of another rock at y=0)
        margin = 100
        x_pos = random.uniform(margin, SCREEN_WIDTH - margin)
        radius = 28.0 if chosen_type != ROCK_TYPE_BOSS else 52.0

        rock = Rock(x_pos, -radius, word, rock_type=chosen_type, fall_speed=base_speed, radius=radius)
        self.active_rocks.append(rock)

    def handle_event(self, event: pygame.event.Event):
        """
        Handles keyboard and mouse input.
        During active gameplay, typing takes strict priority: only ESC pauses,
        and all character keys (A-Z, 0-9, space) go to typing with no overriding actions.
        """
        if self.is_game_over:
            return

        # 1. When paused: Only allow ESC or clicking pause buttons
        if self.is_paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_paused = False
                return
            self.btn_pause_resume.handle_event(event)
            self.btn_pause_menu.handle_event(event)
            return

        # 2. While playing in match:
        if event.type == pygame.KEYDOWN:
            # ESCAPE is the ONLY control key: toggles pause
            if event.key == pygame.K_ESCAPE:
                self.is_paused = True
                return

            # Dedicated Tactical Dodge strictly on arrow keys (never letters like A or D)
            if event.key == pygame.K_LEFT:
                if self.player.trigger_dodge(-1):
                    self.audio.play_sfx("dodge")
                    self.particle_mgr.spawn_dodge_trail(self.player.x, self.player.y)
                return
            elif event.key == pygame.K_RIGHT:
                if self.player.trigger_dodge(1):
                    self.audio.play_sfx("dodge")
                    self.particle_mgr.spawn_dodge_trail(self.player.x, self.player.y)
                return

            # ALL other keyboard keys (letters, numbers, space, backspace, tab) go to typing!
            self.typing_engine.process_key_event(event, self.active_rocks)
            return

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse triggers for EMP and Dodge so keyboard is 100% free of letter conflicts
            # Right Click or Left-Clicking EMP meter detonates EMP blast
            if (event.button == 3 or (event.button == 1 and self.hud.is_emp_clicked(event.pos))):
                if self.player.emp_charge >= self.player.max_emp_charge:
                    self.trigger_emp_bomb()
                    return

            # Clicking the dodge indicator on the HUD triggers dodge
            if event.button == 1 and self.hud.is_dodge_clicked(event.pos):
                if self.player.trigger_dodge(1):
                    self.audio.play_sfx("dodge")
                    self.particle_mgr.spawn_dodge_trail(self.player.x, self.player.y)
                return

    def update(self, dt: float):
        if self.is_paused:
            mouse_pos = pygame.mouse.get_pos()
            self.btn_pause_resume.update(dt, mouse_pos)
            self.btn_pause_menu.update(dt, mouse_pos)
            return
        if self.is_game_over:
            return

        # 1. Update power-ups & background
        self.powerup_mgr.update(dt)
        speed_mult = 0.40 if self.powerup_mgr.is_chrono_slow_active() else 1.0
        self.background.update(dt, game_speed=speed_mult)

        # 2. Update player aiming angle towards locked target
        target_pos = None
        if self.typing_engine.locked_target and self.typing_engine.locked_target.is_active:
            target_pos = (self.typing_engine.locked_target.pos_x, self.typing_engine.locked_target.pos_y)
        self.player.update(dt, target_pos)

        # 3. Update projectiles & particle effects
        self.projectile_mgr.update(dt)
        self.particle_mgr.update(dt)
        self.typing_engine.update(dt)

        # 4. Spawning hazards logic
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_rock()
            self.spawn_timer = self.diff_cfg["spawn_interval"]

        # 5. Update and check collisions for falling rocks
        player_rect = self.player.get_collision_rect()
        danger_line_y = SCREEN_HEIGHT - 85

        for rock in list(self.active_rocks):
            rock.update(dt, speed_multiplier=speed_mult)

            # Check collision with player or reaching bottom danger ground
            rock_rect = rock.get_collision_rect()
            collided_with_player = rock_rect.colliderect(player_rect)
            reached_ground = rock.pos_y >= danger_line_y

            if collided_with_player or reached_ground:
                self._handle_rock_ground_or_player_hit(rock, collided_with_player)

        # Remove inactive / destroyed rocks
        self.active_rocks = [r for r in self.active_rocks if r.is_active and not r.is_destroyed]

        # 6. Mode progression timers
        if self.game_mode == MODE_TIME_ATTACK:
            self.time_attack_remaining -= dt
            if self.time_attack_remaining <= 0:
                self.trigger_game_over()

        elif self.game_mode in (MODE_SURVIVAL, MODE_ENDLESS):
            self.wave_timer += dt
            if self.wave_timer >= 24.0:  # Wave increases every 24 seconds
                self.wave_timer = 0.0
                self.wave_number += 1
                self.audio.play_sfx("combo")
                self.particle_mgr.spawn_floating_text(
                    f"WAVE {self.wave_number} HAZARD ESCALATION!",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 80,
                    COLOR_ACCENT_MAGENTA,
                    self.fonts.get("bold_24", self.fonts["default"])
                )

        # 7. Update HUD
        self.hud.update(dt, self.player, self.stats.score)

    def _handle_rock_ground_or_player_hit(self, rock: Rock, hit_player_directly: bool):
        """Resolves rock crashing into ground or directly on player."""
        rock.is_active = False
        rock.is_destroyed = True

        # Unlock target if this was the targeted rock
        if self.typing_engine.locked_target is rock:
            self.typing_engine.unlock_target()

        # Missed word recorded in stats
        self.stats.record_word_missed(rock.rock_type)

        # In Practice Mode, no damage is inflicted!
        if self.game_mode == MODE_PRACTICE:
            self.audio.play_sfx("explosion")
            self.particle_mgr.spawn_rock_explosion(rock.pos_x, rock.pos_y, rock.get_color(), count=14)
            return

        # Check if player dodged!
        if self.player.is_invulnerable():
            self.audio.play_sfx("dodge")
            self.particle_mgr.spawn_rock_explosion(rock.pos_x, rock.pos_y, rock.get_color(), count=16)
            self.particle_mgr.spawn_floating_text(
                "EVADED!",
                self.player.x,
                self.player.y - 45,
                COLOR_ACCENT_MAGENTA,
                self.fonts.get("bold_20", self.fonts["default"])
            )
            return

        # Inflict damage
        damage_amount = 25.0 * self.diff_cfg["damage_multiplier"]
        if rock.rock_type == ROCK_TYPE_ARMORED:
            damage_amount *= 1.35
        elif rock.rock_type == ROCK_TYPE_BOSS:
            damage_amount *= 2.0

        took_dmg = self.player.take_damage(damage_amount)
        if took_dmg:
            self.background.trigger_shake(12.0, 0.4)
            self.background.trigger_damage_flash(0.35)
            self.audio.play_sfx("explosion")
            self.particle_mgr.spawn_rock_explosion(rock.pos_x, rock.pos_y, (255, 60, 40), count=24)
            self.particle_mgr.spawn_floating_text(
                f"-{int(damage_amount)} HP",
                self.player.x,
                self.player.y - 45,
                COLOR_ACCENT_RED,
                self.fonts.get("bold_20", self.fonts["default"])
            )

            # Check if player died
            if self.player.health <= 0:
                if self.game_mode == MODE_SURVIVAL and self.player.lives > 1:
                    # Lose 1 life, restore HP with temporary shield
                    self.player.lives -= 1
                    self.player.health = self.player.max_health
                    self.player.shield = 40.0
                    self.particle_mgr.spawn_floating_text(
                        f"LIFE LOST! ({self.player.lives} REMAINING)",
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2,
                        COLOR_ACCENT_RED,
                        self.fonts.get("bold_24", self.fonts["default"])
                    )
                else:
                    self.trigger_game_over()

    def trigger_game_over(self):
        """Ends the current game session and triggers the analytics results dashboard."""
        self.is_game_over = True
        self.audio.stop_music()
        self.audio.play_sfx("game_over")
        summary = self.stats.get_summary_dict()
        if self.on_game_over:
            self.on_game_over(summary)

    def render(self, surface: pygame.Surface):
        # 1. Background with screen shake offset applied
        shake_x, shake_y = self.background.shake_offset
        
        # Draw background onto surface
        self.background.render(surface)

        # 2. Draw falling rocks and words
        word_font = self.fonts.get("bold_18", self.fonts["default"])
        typo_flash = self.typing_engine.typo_flash_timer > 0

        for rock in self.active_rocks:
            rock.render(surface, word_font, typo_flash=typo_flash)

        # 3. Draw projectiles, lasers, and EMP waves
        self.projectile_mgr.render(surface)

        # 4. Draw player turret
        self.player.render(surface)

        # 5. Draw particles and floating popups
        self.particle_mgr.render(surface)

        # 6. Draw HUD
        wave_str = f"WAVE {self.wave_number}"
        if self.game_mode == MODE_TIME_ATTACK:
            mins = int(self.time_attack_remaining // 60)
            secs = int(self.time_attack_remaining % 60)
            wave_str = f"{mins:02d}:{secs:02d} REMAINING"

        self.hud.render(
            surface,
            self.player,
            self.stats,
            self.powerup_mgr,
            self.game_mode,
            wave_str,
            self.get_combo_multiplier(),
        )

        # 7. Pause overlay
        if self.is_paused:
            pause_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_surf.fill((10, 14, 25, 215))
            surface.blit(pause_surf, (0, 0))

            p_font = self.fonts.get("bold_32", self.fonts["default"])
            sub_font = self.fonts.get("regular_16", self.fonts["default"])

            p_txt = p_font.render("GAME PAUSED", True, COLOR_WHITE)
            sub_txt = sub_font.render("Press [ESC] to resume • Combat suspended", True, COLOR_ACCENT_CYAN)

            surface.blit(p_txt, (SCREEN_WIDTH // 2 - p_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 75))
            surface.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

            self.btn_pause_resume.render(surface)
            self.btn_pause_menu.render(surface)
