"""
Modern UI Components for TypeStrike
Provides reusable glowing arcade buttons, sliders, progress bars,
toggles, and frosted panels with smooth hover animations.
"""

from typing import Tuple, Optional, Callable
import pygame
from src.config import (
    COLOR_BG_PANEL,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_MAGENTA,
    COLOR_ACCENT_GOLD,
    COLOR_WHITE,
    COLOR_GRAY_LIGHT,
    COLOR_GRAY_MID,
    COLOR_GRAY_DARK,
)


class Button:
    """An interactive cyber button with hover transition and sound trigger."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        font: pygame.font.Font,
        on_click: Optional[Callable] = None,
        base_color: Tuple[int, int, int] = (24, 32, 52),
        hover_color: Tuple[int, int, int] = (38, 50, 82),
        accent_color: Tuple[int, int, int] = COLOR_ACCENT_CYAN,
        text_color: Tuple[int, int, int] = COLOR_WHITE,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.base_color = base_color
        self.hover_color = hover_color
        self.accent_color = accent_color
        self.text_color = text_color
        
        self.is_hovered = False
        self.hover_progress = 0.0  # 0.0 to 1.0 for smooth animation

    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * min(1.0, dt * 14)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                if self.on_click:
                    self.on_click()
                return True
        return False

    def render(self, surface: pygame.Surface):
        # Interpolate background color
        r = int(self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * self.hover_progress)
        g = int(self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * self.hover_progress)
        b = int(self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * self.hover_progress)
        
        # Draw background pill
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (r, g, b, 235), (0, 0, self.rect.width, self.rect.height), border_radius=8)

        # Border outline (glows on hover)
        border_col = self.accent_color if self.hover_progress > 0.1 else COLOR_GRAY_MID
        border_width = 2 if self.hover_progress > 0.3 else 1
        pygame.draw.rect(btn_surf, border_col, (0, 0, self.rect.width, self.rect.height), border_width, border_radius=8)
        
        # Left accent pip when hovered
        if self.hover_progress > 0.05:
            pip_h = int(self.rect.height * 0.5 * self.hover_progress)
            pip_y = (self.rect.height - pip_h) // 2
            pygame.draw.rect(btn_surf, self.accent_color, (2, pip_y, 4, pip_h), border_radius=2)

        surface.blit(btn_surf, self.rect.topleft)

        # Render button text
        text_surf = self.font.render(self.text, True, self.text_color if not self.is_hovered else COLOR_ACCENT_CYAN)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider:
    """An interactive horizontal audio/settings slider."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        label: str,
        value: float,
        font: pygame.font.Font,
        on_change: Optional[Callable[[float], None]] = None,
        min_val: float = 0.0,
        max_val: float = 1.0,
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = value
        self.font = font
        self.on_change = on_change
        self.min_val = min_val
        self.max_val = max_val
        self.is_dragging = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self._update_val_from_mouse(event.pos[0])

    def _update_val_from_mouse(self, mouse_x: int):
        ratio = (mouse_x - self.rect.x) / max(1, self.rect.width)
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        if self.on_change:
            self.on_change(self.value)

    def render(self, surface: pygame.Surface):
        # Render label
        label_surf = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, COLOR_GRAY_LIGHT)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 24))

        # Track background
        pygame.draw.rect(surface, (28, 36, 56), self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_GRAY_MID, self.rect, 1, border_radius=4)

        # Filled portion
        ratio = (self.value - self.min_val) / max(0.001, self.max_val - self.min_val)
        fill_w = int(self.rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(surface, COLOR_ACCENT_CYAN, fill_rect, border_radius=4)

        # Handle knob
        knob_x = self.rect.x + fill_w
        knob_y = self.rect.centery
        pygame.draw.circle(surface, COLOR_WHITE, (knob_x, knob_y), 8)
        pygame.draw.circle(surface, COLOR_ACCENT_CYAN, (knob_x, knob_y), 8, 2)


class ProgressBar:
    """A smooth animated progress bar for Health, Shields, and EMP meters."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        current_val: float,
        max_val: float,
        fill_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int] = (20, 26, 42),
        border_color: Tuple[int, int, int] = COLOR_GRAY_MID,
    ):
        self.rect = pygame.Rect(rect)
        self.current_val = current_val
        self.displayed_val = current_val
        self.max_val = max_val
        self.fill_color = fill_color
        self.bg_color = bg_color
        self.border_color = border_color

    def update(self, dt: float, current_val: float):
        self.current_val = current_val
        # Smooth interpolation to current value
        self.displayed_val += (self.current_val - self.displayed_val) * min(1.0, dt * 10)

    def render(self, surface: pygame.Surface):
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        
        # Draw filled portion
        ratio = max(0.0, min(1.0, self.displayed_val / max(0.01, self.max_val)))
        fill_w = int(self.rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=4)

        # Border
        pygame.draw.rect(surface, self.border_color, self.rect, 1, border_radius=4)
