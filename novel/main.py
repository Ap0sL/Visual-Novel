
import pygame
import sys
import json
import math
import random
import array
import os
from pathlib import Path

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

# ============================================================
# КОНСТАНТЫ
# ============================================================
WIDTH = 1000
HEIGHT = 650
FPS = 60

BASE_DIR = Path(__file__).resolve().parent
BACKGROUNDS_DIR = BASE_DIR / "assets" / "backgrounds"
CHARACTER_PATH = BASE_DIR / "assets" / "characters" / "visitor.png"
STORY_PATH = BASE_DIR / "story_data.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
SAVES_DIR = BASE_DIR / "saves"

# Создаём папку сохранений
SAVES_DIR.mkdir(exist_ok=True)


# ============================================================
# ЦВЕТОВАЯ ПАЛИТРА
# ============================================================
class Colors:
    WHITE = (230, 225, 215)
    BLACK = (10, 10, 10)
    DARK = (8, 12, 24)
    SOFT_DARK = (20, 24, 38)
    GRAY = (90, 90, 100)
    LIGHT_GRAY = (160, 160, 170)

    ACCENT_RED = (180, 40, 50)
    ACCENT_RED_GLOW = (220, 60, 70)
    ACCENT_BLUE = (80, 140, 200)
    ACCENT_BLUE_GLOW = (120, 180, 240)
    ACCENT_TEAL = (60, 180, 170)
    ACCENT_AMBER = (220, 180, 60)
    ACCENT_GREEN = (80, 200, 120)

    PANEL_BG = (8, 12, 24)
    PANEL_BORDER = (60, 80, 120)
    PANEL_BORDER_GLOW = (80, 120, 180)
    TEXT = (220, 215, 205)
    TEXT_DIM = (140, 135, 130)
    TEXT_BRIGHT = (255, 250, 240)
    SPEAKER = (255, 200, 180)
    HINT = (120, 130, 150)
    SAVE_MSG = (220, 180, 60)

    BTN_NORMAL = (30, 45, 75)
    BTN_HOVER = (45, 65, 110)
    BTN_DISABLED = (30, 30, 40)
    BTN_BORDER = (70, 100, 160)
    BTN_BORDER_HOVER = (100, 150, 220)
    BTN_TEXT = (210, 210, 220)
    BTN_TEXT_DISABLED = (70, 70, 80)

    STAT = {
        "trust": (100, 180, 255),
        "knowledge": (120, 220, 180),
        "fear": (220, 80, 80),
        "noise": (220, 180, 60),
        "time": (180, 140, 255)
    }


# ============================================================
# КОНСТАНТЫ ПРЕДМЕТОВ
# ============================================================
ITEM_NAMES = {
    "map": "План школы",
    "key": "Медный ключ",
    "note": "Записка",
    "flashlight": "Фонарик"
}
ITEM_ICONS = {"map": "M", "key": "K", "note": "N", "flashlight": "F"}
ITEM_DESCRIPTIONS = {
    "map": "показывает короткий путь к лестнице",
    "key": "открывает старую дверь у подсобки",
    "note": "подсказывает, когда коридор безопасен",
    "flashlight": "помогает не потеряться в темном крыле"
}
STAT_LABELS = {
    "trust": "Смелость",
    "knowledge": "Внимательность",
    "fear": "Страх",
    "noise": "Шум",
    "time": "Время"
}


# ============================================================
# ШРИФТЫ
# ============================================================
class Fonts:
    def __init__(self):
        family = "segoeui"
        try:
            self.title = pygame.font.SysFont(family, 52, bold=True)
            self.name = pygame.font.SysFont(family, 28, bold=True)
            self.text = pygame.font.SysFont(family, 24)
            self.small = pygame.font.SysFont(family, 20)
            self.tiny = pygame.font.SysFont(family, 16)
            self.icon = pygame.font.SysFont(family, 14, bold=True)
        except Exception:
            family = "arial"
            self.title = pygame.font.SysFont(family, 52, bold=True)
            self.name = pygame.font.SysFont(family, 28, bold=True)
            self.text = pygame.font.SysFont(family, 24)
            self.small = pygame.font.SysFont(family, 20)
            self.tiny = pygame.font.SysFont(family, 16)
            self.icon = pygame.font.SysFont(family, 14, bold=True)


fonts = Fonts()


# ============================================================
# ЗВУКОВАЯ СИСТЕМА
# ============================================================
class SoundManager:
    """Процедурная генерация звуков + управление громкостью."""

    def __init__(self):
        self.master_volume = 0.5
        self.sfx_volume = 0.6
        self.sounds = {}
        self._generate_sounds()
        self.ambient_playing = False

    def _make_tone(self, freq, duration_ms, volume=0.3, fade_out=True):
        """Генерирует синусоидальный тон."""
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = array.array('h', [0] * n_samples)
        max_amp = int(32767 * volume)
        for i in range(n_samples):
            t = i / sample_rate
            val = int(max_amp * math.sin(2.0 * math.pi * freq * t))
            if fade_out:
                fade = 1.0 - (i / n_samples)
                val = int(val * fade)
            buf[i] = max(-32768, min(32767, val))
        snd = pygame.mixer.Sound(buffer=buf)
        return snd

    def _make_noise_burst(self, duration_ms, volume=0.15):
        """Генерирует короткий шумовой импульс."""
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = array.array('h', [0] * n_samples)
        max_amp = int(32767 * volume)
        for i in range(n_samples):
            fade = 1.0 - (i / n_samples)
            val = int(random.randint(-max_amp, max_amp) * fade)
            buf[i] = max(-32768, min(32767, val))
        return pygame.mixer.Sound(buffer=buf)

    def _make_ambient_drone(self):
        """Генерирует длинный эмбиентный дрон."""
        sample_rate = 22050
        duration = 8  # секунд
        n_samples = sample_rate * duration
        buf = array.array('h', [0] * n_samples)
        volume = 0.08
        max_amp = int(32767 * volume)
        for i in range(n_samples):
            t = i / sample_rate
            # Низкочастотный дрон с модуляцией
            val = math.sin(2 * math.pi * 55 * t) * 0.5  # основной тон
            val += math.sin(2 * math.pi * 82.5 * t) * 0.3  # квинта
            val += math.sin(2 * math.pi * 38 * t + math.sin(t * 0.5) * 2) * 0.2  # модуляция
            val = int(val * max_amp)
            buf[i] = max(-32768, min(32767, val))
        return pygame.mixer.Sound(buffer=buf)

    def _generate_sounds(self):
        """Генерирует все звуки."""
        try:
            self.sounds["typewriter"] = self._make_tone(800, 20, volume=0.1, fade_out=True)
            self.sounds["hover"] = self._make_tone(600, 40, volume=0.08)
            self.sounds["click"] = self._make_tone(400, 60, volume=0.15)
            self.sounds["item"] = self._make_tone(880, 200, volume=0.2)
            self.sounds["save"] = self._make_tone(660, 150, volume=0.15)
            self.sounds["fear"] = self._make_noise_burst(300, volume=0.2)
            self.sounds["step"] = self._make_noise_burst(80, volume=0.06)
            self.sounds["ambient"] = self._make_ambient_drone()
        except Exception:
            pass

    def play(self, name):
        """Воспроизводит звук по имени."""
        if name in self.sounds:
            vol = self.master_volume * self.sfx_volume
            self.sounds[name].set_volume(vol)
            self.sounds[name].play()

    def start_ambient(self):
        """Запускает фоновую музыку."""
        if not self.ambient_playing and "ambient" in self.sounds:
            self.sounds["ambient"].set_volume(self.master_volume * 0.4)
            self.sounds["ambient"].play(loops=-1)
            self.ambient_playing = True

    def stop_ambient(self):
        if self.ambient_playing and "ambient" in self.sounds:
            self.sounds["ambient"].stop()
            self.ambient_playing = False

    def update_volumes(self):
        if self.ambient_playing and "ambient" in self.sounds:
            self.sounds["ambient"].set_volume(self.master_volume * 0.4)

    def set_master_volume(self, vol):
        self.master_volume = max(0.0, min(1.0, vol))
        self.update_volumes()


# ============================================================
# СИСТЕМА НАСТРОЕК
# ============================================================
class Settings:
    def __init__(self):
        self.master_volume = 0.5
        self.sfx_volume = 0.6
        self.text_speed = 0.03  # секунд на символ (меньше = быстрее)
        self.load()

    def save(self):
        data = {
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "text_speed": self.text_speed
        }
        try:
            with SETTINGS_PATH.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load(self):
        if not SETTINGS_PATH.exists():
            return
        try:
            with SETTINGS_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.master_volume = float(data.get("master_volume", 0.5))
            self.sfx_volume = float(data.get("sfx_volume", 0.6))
            self.text_speed = float(data.get("text_speed", 0.03))
        except Exception:
            pass


# ============================================================
# СИСТЕМА СОХРАНЕНИЙ
# ============================================================
class SaveSystem:
    MAX_SLOTS = 3

    @staticmethod
    def _slot_path(slot):
        return SAVES_DIR / f"slot_{slot}.json"

    @staticmethod
    def save(slot, game_data):
        path = SaveSystem._slot_path(slot)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def load(slot):
        path = SaveSystem._slot_path(slot)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def get_slot_info(slot):
        """Возвращает краткую инфо о слоте для UI."""
        data = SaveSystem.load(slot)
        if data is None:
            return None
        return {
            "node": data.get("current_node", "?"),
            "trust": data.get("trust", 0),
            "knowledge": data.get("knowledge", 0),
            "time_left": data.get("time_left", 0),
            "items": len(data.get("inventory", []))
        }

    @staticmethod
    def auto_save(game_data):
        """Автосохранение в слот 0 (скрытый)."""
        path = SAVES_DIR / "autosave.json"
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def load_auto():
        path = SAVES_DIR / "autosave.json"
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None


# ============================================================
# ЛОГ ДИАЛОГОВ
# ============================================================
class DialogLog:
    MAX_ENTRIES = 50

    def __init__(self):
        self.entries = []  # [(speaker, text), ...]
        self.visible = False
        self.scroll_offset = 0

    def add(self, speaker, text):
        self.entries.append((speaker, text))
        if len(self.entries) > self.MAX_ENTRIES:
            self.entries.pop(0)

    def toggle(self):
        self.visible = not self.visible
        self.scroll_offset = max(0, len(self.entries) - 8)

    def scroll(self, direction):
        self.scroll_offset = max(0, min(len(self.entries) - 1, self.scroll_offset + direction))

    def draw(self, surface):
        if not self.visible:
            return

        # Полноэкранный оверлей
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Панель
        panel_rect = pygame.Rect(60, 30, 880, 570)
        draw_panel(surface, panel_rect, alpha=240, glow=True, glow_color=Colors.PANEL_BORDER_GLOW)

        # Заголовок
        title = fonts.name.render("История диалогов", True, Colors.ACCENT_BLUE)
        surface.blit(title, (80, 45))

        # Подсказка
        hint = fonts.tiny.render("H — закрыть    ↑↓ / колесо — прокрутка", True, Colors.HINT)
        surface.blit(hint, (panel_rect.right - hint.get_width() - 20, 50))

        # Линия
        line_s = pygame.Surface((840, 1), pygame.SRCALPHA)
        line_s.fill((*Colors.PANEL_BORDER, 100))
        surface.blit(line_s, (80, 78))

        # Записи
        y = 90
        max_y = panel_rect.bottom - 30
        visible_entries = self.entries[self.scroll_offset:]

        for speaker, text in visible_entries:
            if y > max_y - 30:
                break

            # Спикер
            sp_surf = fonts.small.render(speaker, True, Colors.ACCENT_RED)
            surface.blit(sp_surf, (90, y))
            y += 24

            # Текст
            lines = wrap_text(text, fonts.small, 800)
            for line in lines:
                if y > max_y - 10:
                    break
                line_surf = fonts.small.render(line, True, Colors.TEXT_DIM)
                surface.blit(line_surf, (90, y))
                y += 22
            y += 12

        # Полоса прокрутки
        if len(self.entries) > 8:
            bar_h = max(30, int(570 * 8 / len(self.entries)))
            bar_y = 85 + int((570 - bar_h - 30) * self.scroll_offset / max(1, len(self.entries) - 8))
            bar_surf = pygame.Surface((4, bar_h), pygame.SRCALPHA)
            bar_surf.fill((*Colors.ACCENT_BLUE, 100))
            surface.blit(bar_surf, (panel_rect.right - 15, bar_y))

    def clear(self):
        self.entries = []
        self.scroll_offset = 0


# ============================================================
# ВСПЛЫВАЮЩИЕ ПОПАПЫ СТАТОВ
# ============================================================
class StatPopup:
    def __init__(self, text, color, x, y):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.life = 1.5  # секунд
        self.max_life = 1.5
        self.vy = -40  # пикселей в секунду (вверх)

    def update(self, dt):
        self.life -= dt
        self.y += self.vy * dt

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = self.life / self.max_life
        alpha = int(255 * min(1.0, progress * 2))

        text_surf = fonts.small.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))

    @property
    def alive(self):
        return self.life > 0


# ============================================================
# ЧАСТИЦЫ
# ============================================================
class DustParticle:
    def __init__(self):
        self.reset()
        self.y = random.uniform(0, HEIGHT)

    def reset(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(-20, -5)
        self.size = random.uniform(1.0, 2.5)
        self.speed_y = random.uniform(8, 25)
        self.speed_x = random.uniform(-8, 8)
        self.alpha = random.randint(20, 55)
        self.wobble_offset = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.5, 2.0)
        self.wobble_amp = random.uniform(5, 15)

    def update(self, dt, anim_time):
        self.y += self.speed_y * dt
        self.x += self.speed_x * dt + math.sin(anim_time * self.wobble_speed + self.wobble_offset) * self.wobble_amp * dt
        if self.y > HEIGHT + 10 or self.x < -20 or self.x > WIDTH + 20:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((int(self.size * 2 + 2), int(self.size * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 190, 170, self.alpha), (int(self.size + 1), int(self.size + 1)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


# ============================================================
# УТИЛИТЫ РИСОВАНИЯ
# ============================================================
def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return (int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t))


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + word + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current.strip())
            current = word + " "
    if current:
        lines.append(current.strip())
    return lines


def draw_gradient_rect(surface, rect, color_top, color_bottom, alpha=255, border_radius=0):
    grad = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(grad, (r, g, b, alpha), (0, y), (rect.width, y))
    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(grad, rect.topleft)


def draw_glow_border(surface, rect, color, width=2, glow_width=6, alpha=80):
    for i in range(glow_width, 0, -1):
        a = int(alpha * (1 - i / glow_width))
        expanded = rect.inflate(i * 2, i * 2)
        gs = pygame.Surface((expanded.width, expanded.height), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*color, a), (0, 0, expanded.width, expanded.height), width=1, border_radius=14)
        surface.blit(gs, expanded.topleft)
    pygame.draw.rect(surface, color, rect, width=width, border_radius=12)


def draw_panel(surface, rect, alpha=200, border_color=None, glow=False, glow_color=None):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    draw_gradient_rect(panel, pygame.Rect(0, 0, rect.width, rect.height),
                       (12, 16, 30, alpha), (6, 8, 18, alpha), border_radius=12)
    surface.blit(panel, rect.topleft)
    if glow and glow_color:
        draw_glow_border(surface, rect, glow_color, width=1, glow_width=5, alpha=50)
    elif border_color:
        pygame.draw.rect(surface, border_color, rect, 1, border_radius=12)


def draw_progress_bar(surface, x, y, width, height, value, max_value, color):
    bg = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (20, 25, 40), bg, border_radius=4)
    fill_w = int((min(value, max_value) / max(max_value, 1)) * (width - 2))
    if fill_w > 0:
        fill_rect = pygame.Rect(x + 1, y + 1, fill_w, height - 2)
        bar_s = pygame.Surface((fill_w, height - 2), pygame.SRCALPHA)
        bright = tuple(min(255, c + 40) for c in color)
        for bx in range(fill_w):
            t = bx / max(1, fill_w - 1)
            r = int(color[0] + (bright[0] - color[0]) * t)
            g = int(color[1] + (bright[1] - color[1]) * t)
            b = int(color[2] + (bright[2] - color[2]) * t)
            pygame.draw.line(bar_s, (r, g, b, 200), (bx, 0), (bx, height - 2))
        surface.blit(bar_s, fill_rect.topleft)
    pygame.draw.rect(surface, (*color, 100), bg, 1, border_radius=4)


# ============================================================
# КНОПКА
# ============================================================
class Button:
    def __init__(self, x, y, w, h, text, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.enabled = enabled
        self.hover_anim = 0.0
        self._was_hovered = False

    def update(self, mouse_pos, dt):
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        target = 1.0 if hovered else 0.0
        speed = 6.0
        self.hover_anim = max(0, min(1, self.hover_anim + (speed if self.hover_anim < target else -speed) * dt))

        # Звук при наведении
        if hovered and not self._was_hovered and self.enabled:
            game.sound.play("hover")
        self._was_hovered = hovered

    def draw(self, surface, mouse_pos, appear_progress=1.0, pulse_time=0.0):
        if appear_progress <= 0:
            return

        offset_x = int((1 - ease_out_cubic(appear_progress)) * 60)
        alpha = int(255 * min(1.0, appear_progress * 1.5))

        draw_rect = self.rect.copy()
        draw_rect.x += offset_x
        expand = int(self.hover_anim * 6)
        draw_rect.inflate_ip(expand, expand // 2)
        t = self.hover_anim

        if not self.enabled:
            bg = Colors.BTN_DISABLED
            border = (40, 40, 50)
            tc = Colors.BTN_TEXT_DISABLED
        else:
            bg = lerp_color(Colors.BTN_NORMAL, Colors.BTN_HOVER, t)
            border = lerp_color(Colors.BTN_BORDER, Colors.BTN_BORDER_HOVER, t)
            tc = lerp_color(Colors.BTN_TEXT, Colors.TEXT_BRIGHT, t)

        # Тень
        ss = pygame.Surface((draw_rect.width + 8, draw_rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(ss, (0, 0, 0, int(60 * appear_progress)), (4, 6, draw_rect.width, draw_rect.height), border_radius=12)
        surface.blit(ss, (draw_rect.x - 4, draw_rect.y - 2))

        # Фон
        btn_s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        ct = tuple(min(255, c + 15) for c in bg)
        cb = tuple(max(0, c - 10) for c in bg)
        draw_gradient_rect(btn_s, pygame.Rect(0, 0, draw_rect.width, draw_rect.height),
                           (*ct, alpha), (*cb, alpha), border_radius=10)
        surface.blit(btn_s, draw_rect.topleft)

        # Glow при ховере
        if self.enabled and t > 0.05:
            ga = int(40 * t * appear_progress)
            for i in range(4, 0, -1):
                a = int(ga * (1 - i / 4))
                exp = draw_rect.inflate(i * 2, i * 2)
                gs = pygame.Surface((exp.width, exp.height), pygame.SRCALPHA)
                pygame.draw.rect(gs, (*Colors.BTN_BORDER_HOVER, a), (0, 0, exp.width, exp.height), width=1, border_radius=14)
                surface.blit(gs, exp.topleft)

        # Рамка
        bs = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bs, (*border, int(min(255, alpha))), (0, 0, draw_rect.width, draw_rect.height), width=1, border_radius=10)
        surface.blit(bs, draw_rect.topleft)

        # Пульсация
        if self.enabled:
            pa = max(0, min(255, int((0.5 + 0.5 * math.sin(pulse_time * 2.5)) * 80 * appear_progress)))
            ls = pygame.Surface((draw_rect.width - 20, 2), pygame.SRCALPHA)
            ls.fill((*Colors.ACCENT_BLUE_GLOW, pa))
            surface.blit(ls, (draw_rect.x + 10, draw_rect.y + 1))

        # Текст
        lf = fonts.text if fonts.text.size(self.text)[0] <= draw_rect.width - 30 else fonts.small
        label = lf.render(self.text, True, tc)
        label.set_alpha(alpha)
        surface.blit(label, label.get_rect(center=draw_rect.center))

        # Замок
        if not self.enabled:
            lock = fonts.icon.render("[X]", True, (80, 80, 90))
            lock.set_alpha(alpha)
            surface.blit(lock, (draw_rect.right - 35, draw_rect.centery - 8))

    def is_clicked(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.inflate(12, 8).collidepoint(event.pos)
        return False


# ============================================================
# ГЛАВНЫЙ КЛАСС ИГРЫ
# ============================================================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Школьный Коридор")
        self.clock = pygame.time.Clock()

        # Подсистемы
        self.settings = Settings()
        self.sound = SoundManager()
        self.sound.set_master_volume(self.settings.master_volume)
        self.sound.sfx_volume = self.settings.sfx_volume
        self.dialog_log = DialogLog()

        # Загрузка ассетов
        self._load_assets()
        self._create_vignette()

        # Загрузка сценария
        self.story = self._load_story()

        # Состояние игры
        self.state = "menu"  # menu, story, result, settings, saves
        self.current_node = "intro_1"
        self.previous_node = self.current_node

        # Статы
        self.trust = 0
        self.knowledge = 0
        self.fear = 0
        self.noise = 0
        self.time_left = 8
        self.last_choice = ""
        self.inventory = []

        # UI
        self.save_message = ""
        self.save_message_timer = 0
        self.stat_popups = []

        # Анимации
        self.anim_time = 0.0
        self.scene_fade_alpha = 0
        self.pulse_time = 0.0

        # Typewriter
        self.tw_text = ""
        self.tw_target = ""
        self.tw_timer = 0.0
        self.tw_node = ""
        self.tw_last_char_index = 0

        # Мерцание
        self.flicker_alpha = 0
        self.flicker_timer = 0.0
        self.flicker_next = random.uniform(3.0, 8.0)
        self.flicker_dur = 0.0

        # Screen shake
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0.0

        # Частицы
        self.particles = [DustParticle() for _ in range(40)]

        # Кнопки выбора
        self.choice_appear_timer = 0.0
        self.choice_appear_node = ""

        # Глитч заголовка
        self.glitch_timer = 0.0
        self.glitch_active = False
        self.glitch_offset = 0
        self.glitch_next = random.uniform(2.0, 5.0)

        # Фон текущий
        self.current_bg_key = "corridor"
        self.bg_transition_alpha = 0

        # Кнопки меню
        self.start_btn = Button(360, 300, 280, 55, "НАЧАТЬ ИГРУ")
        self.load_btn = Button(360, 370, 280, 55, "ЗАГРУЗИТЬ")
        self.settings_btn = Button(360, 440, 280, 55, "НАСТРОЙКИ")
        self.exit_btn = Button(360, 510, 280, 55, "ВЫХОД")

        # Кнопки настроек
        self.settings_back_btn = Button(360, 500, 280, 50, "НАЗАД")

        # Кнопки сохранений
        self.save_slot_btns = []
        self.save_back_btn = Button(360, 480, 280, 50, "НАЗАД")
        self.save_mode = "load"  # "load" или "save"

        # Запуск
        self.running = True

    def _load_assets(self):
        self.character_img = pygame.image.load(str(CHARACTER_PATH)).convert_alpha()
        self.character_img = pygame.transform.smoothscale(self.character_img, (150, 290))

        self.backgrounds = {}
        bg_files = {
            "corridor": "school.png",
            "library": "library.png",
            "stairs": "stairs.png"
        }
        for key, filename in bg_files.items():
            path = BACKGROUNDS_DIR / filename
            if path.exists():
                img = pygame.image.load(str(path)).convert()
                self.backgrounds[key] = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

        # Fallback
        if "corridor" not in self.backgrounds:
            fallback = pygame.Surface((WIDTH, HEIGHT))
            fallback.fill((20, 20, 30))
            self.backgrounds["corridor"] = fallback

    def _create_vignette(self):
        self.vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(80):
            a = int(i * 2.8)
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (0, i, WIDTH, 1))
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (0, HEIGHT - 1 - i, WIDTH, 1))
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (i, 0, 1, HEIGHT))
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (WIDTH - 1 - i, 0, 1, HEIGHT))

    def _load_story(self):
        try:
            with STORY_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    # ------- Данные для сохранения -------
    def _get_save_data(self):
        return {
            "current_node": self.current_node,
            "trust": self.trust,
            "knowledge": self.knowledge,
            "fear": self.fear,
            "noise": self.noise,
            "time_left": self.time_left,
            "last_choice": self.last_choice,
            "inventory": self.inventory
        }

    def _apply_save_data(self, data):
        if data is None:
            return False

        node = data.get("current_node", "intro_1")
        if node not in self.story:
            node = "intro_1"

        self.current_node = node
        self.previous_node = node
        self.trust = max(0, int(data.get("trust", 0)))
        self.knowledge = max(0, int(data.get("knowledge", 0)))
        self.fear = max(0, int(data.get("fear", 0)))
        self.noise = max(0, int(data.get("noise", 0)))
        self.time_left = max(0, int(data.get("time_left", 8)))
        self.last_choice = str(data.get("last_choice", ""))

        inv = data.get("inventory", [])
        self.inventory = [i for i in inv if i in ITEM_NAMES] if isinstance(inv, list) else []

        self.state = "story"
        self.tw_node = ""  # Сбросить typewriter
        return True

    # ------- Игровая логика -------
    def choice_is_available(self, choice):
        if "requires" in choice:
            return choice["requires"] in self.inventory
        if "requires_all" in choice:
            return all(i in self.inventory for i in choice["requires_all"])
        if "requires_any" in choice:
            return any(i in self.inventory for i in choice["requires_any"])
        return True

    def get_choice_lock_text(self, choice):
        if "requires" in choice:
            return "Нужно: " + ITEM_NAMES.get(choice["requires"], choice["requires"])
        if "requires_all" in choice:
            missing = [ITEM_NAMES.get(i, i) for i in choice["requires_all"] if i not in self.inventory]
            return "Не хватает: " + ", ".join(missing)
        if "requires_any" in choice:
            names = [ITEM_NAMES.get(i, i) for i in choice["requires_any"]]
            return "Нужен: " + " / ".join(names)
        return ""

    def apply_choice(self, choice):
        if not self.choice_is_available(choice):
            self.save_message = self.get_choice_lock_text(choice)
            self.save_message_timer = 2.0
            return

        # Запомним старые значения для попапов
        old_stats = {"trust": self.trust, "knowledge": self.knowledge,
                     "fear": self.fear, "noise": self.noise, "time": self.time_left}

        self.trust = max(0, self.trust + choice.get("trust", 0))
        self.knowledge = max(0, self.knowledge + choice.get("knowledge", 0))
        self.fear = max(0, self.fear + choice.get("fear", 0))
        self.noise = max(0, self.noise + choice.get("noise", 0))
        self.time_left = max(0, self.time_left + choice.get("time", 0))

        # Попапы изменений
        new_stats = {"trust": self.trust, "knowledge": self.knowledge,
                     "fear": self.fear, "noise": self.noise, "time": self.time_left}
        popup_y = 180
        for key in ["trust", "knowledge", "fear", "noise", "time"]:
            diff = new_stats[key] - old_stats[key]
            if diff != 0:
                sign = "+" if diff > 0 else ""
                color = Colors.STAT.get(key, Colors.WHITE)
                label = STAT_LABELS.get(key, key)
                self.stat_popups.append(StatPopup(f"{sign}{diff} {label}", color, 720, popup_y))
                popup_y += 28

        self.last_choice = choice["text"]

        # Screen shake
        fear_d = choice.get("fear", 0)
        if fear_d >= 2:
            self.shake_intensity = 8.0
            self.sound.play("fear")
        elif fear_d >= 1:
            self.shake_intensity = 4.0

        if "item" in choice:
            item = choice["item"]
            if item not in self.inventory:
                self.inventory.append(item)
                self.save_message = "Найден предмет: " + ITEM_NAMES.get(item, item)
                self.save_message_timer = 3.0
                self.sound.play("item")
        else:
            self.save_message = ""
            self.save_message_timer = 0

        self.sound.play("click")

        if self.time_left == 0:
            self.current_node = "time_out"
        else:
            self.current_node = choice["next"]

        # Автосохранение
        SaveSystem.auto_save(self._get_save_data())

    def advance_story(self):
        # Пропуск typewriter
        if self.tw_text != self.tw_target and self.tw_target:
            self.tw_text = self.tw_target
            self.sound.play("click")
            return

        node = self.story.get(self.current_node, {})
        if self.current_node == "final_check":
            self.state = "result"
            self.sound.stop_ambient()
        else:
            self.current_node = node.get("next", "final_check")
            self.sound.play("step")

    def reset_game(self):
        self.state = "menu"
        self.current_node = "intro_1"
        self.previous_node = "intro_1"
        self.trust = self.knowledge = self.fear = self.noise = 0
        self.time_left = 8
        self.last_choice = ""
        self.inventory = []
        self.save_message = ""
        self.save_message_timer = 0
        self.stat_popups = []
        self.dialog_log.clear()
        self.tw_node = ""
        self.sound.stop_ambient()

    # ------- Обновление анимаций -------
    def update(self, dt):
        self.anim_time += dt
        self.pulse_time += dt

        # Сообщение
        if self.save_message_timer > 0:
            self.save_message_timer -= dt

        # Scene fade
        if self.previous_node != self.current_node:
            self.previous_node = self.current_node
            self.scene_fade_alpha = 120

            # Лог
            node = self.story.get(self.current_node, {})
            self.dialog_log.add(node.get("speaker", ""), node.get("text", ""))

            # Typewriter
            self.tw_target = node.get("text", "")
            self.tw_text = ""
            self.tw_timer = 0.0
            self.tw_node = self.current_node

            # Фон
            new_bg = node.get("background", self.current_bg_key)
            if new_bg != self.current_bg_key and new_bg in self.backgrounds:
                self.current_bg_key = new_bg
        elif self.scene_fade_alpha > 0:
            self.scene_fade_alpha = max(0, self.scene_fade_alpha - 180 * dt)

        # Typewriter
        if self.tw_node != self.current_node:
            node = self.story.get(self.current_node, {})
            self.tw_target = node.get("text", "")
            self.tw_text = ""
            self.tw_timer = 0.0
            self.tw_node = self.current_node
            self.dialog_log.add(node.get("speaker", ""), node.get("text", ""))

        if self.tw_text != self.tw_target:
            self.tw_timer += dt
            chars = int(self.tw_timer / self.settings.text_speed)
            old_len = len(self.tw_text)
            if chars >= len(self.tw_target):
                self.tw_text = self.tw_target
            else:
                self.tw_text = self.tw_target[:chars]

            # Звук typewriter
            if len(self.tw_text) > old_len and len(self.tw_text) % 3 == 0:
                self.sound.play("typewriter")

        # Мерцание
        self.flicker_timer += dt
        if self.flicker_dur > 0:
            self.flicker_dur -= dt
            if self.flicker_dur <= 0:
                self.flicker_alpha = 0
                self.flicker_next = random.uniform(3.0, 8.0)
                self.flicker_timer = 0
        elif self.flicker_timer >= self.flicker_next:
            self.flicker_alpha = random.randint(30, 80)
            self.flicker_dur = random.uniform(0.05, 0.15)
            self.flicker_timer = 0

        # Shake
        if self.shake_intensity > 0:
            self.shake_x = int(random.uniform(-self.shake_intensity, self.shake_intensity))
            self.shake_y = int(random.uniform(-self.shake_intensity, self.shake_intensity))
            self.shake_intensity *= 0.88
            if self.shake_intensity < 0.5:
                self.shake_intensity = self.shake_x = self.shake_y = 0
        else:
            self.shake_x = self.shake_y = 0

        # Частицы
        for p in self.particles:
            p.update(dt, self.anim_time)

        # Попапы
        for popup in self.stat_popups:
            popup.update(dt)
        self.stat_popups = [p for p in self.stat_popups if p.alive]

        # Глитч
        self.glitch_timer += dt
        if self.glitch_active:
            self.glitch_offset = random.randint(-6, 6)
            if self.glitch_timer >= 0.15:
                self.glitch_active = False
                self.glitch_timer = 0
                self.glitch_next = random.uniform(2.0, 6.0)
        else:
            if self.glitch_timer >= self.glitch_next:
                self.glitch_active = True
                self.glitch_timer = 0

    # ------- ОТРИСОВКА -------
    def draw_bg(self):
        bg = self.backgrounds.get(self.current_bg_key, self.backgrounds["corridor"])
        self.screen.blit(bg, (self.shake_x, self.shake_y))

    def draw_character(self):
        base_w, base_h = 150, 290
        bob_y = int(math.sin(self.anim_time * 1.8) * 3)
        bob_x = int(math.sin(self.anim_time * 1.1) * 2)
        bs = 1.0 + math.sin(self.anim_time * 2.5) * 0.005
        w = int(base_w * bs)
        h = int(base_h * bs)
        img = pygame.transform.smoothscale(self.character_img, (w, h)) if (w != base_w or h != base_h) else self.character_img
        self.screen.blit(img, (100 + bob_x - (w - base_w) // 2, 150 + bob_y - (h - base_h)))

    def draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    def draw_vignette(self):
        self.screen.blit(self.vignette, (0, 0))

    def draw_flicker(self):
        if self.flicker_alpha > 0:
            o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            o.fill((0, 0, 0, self.flicker_alpha))
            self.screen.blit(o, (0, 0))

    def draw_scene_fade(self):
        if self.scene_fade_alpha > 0:
            o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            o.fill((0, 0, 0, int(self.scene_fade_alpha)))
            self.screen.blit(o, (0, 0))

    def draw_text_box(self):
        node = self.story.get(self.current_node, {})
        speaker = node.get("speaker", "")
        box = pygame.Rect(50, 455, 900, 165)
        draw_panel(self.screen, box, alpha=220, glow=True, glow_color=Colors.PANEL_BORDER_GLOW)

        # Таб спикера
        sw = fonts.small.size(speaker)[0] + 30
        tab = pygame.Rect(65, 438, sw, 28)
        ts = pygame.Surface((tab.width, tab.height), pygame.SRCALPHA)
        pygame.draw.rect(ts, (*Colors.ACCENT_RED, 200), (0, 0, tab.width, tab.height), border_radius=6)
        self.screen.blit(ts, tab.topleft)
        self.screen.blit(fonts.small.render(speaker, True, Colors.TEXT_BRIGHT), (tab.x + 15, tab.y + 4))

        # Линия
        ls = pygame.Surface((box.width - 30, 1), pygame.SRCALPHA)
        ls.fill((*Colors.PANEL_BORDER_GLOW, 60))
        self.screen.blit(ls, (box.x + 15, 472))

        # Текст
        display = self.tw_text if self.tw_text else node.get("text", "")
        font = fonts.text
        lines = wrap_text(display, font, 840)
        if len(lines) > 3:
            font = fonts.small
            lines = wrap_text(display, font, 840)

        y = 482
        for line in lines:
            self.screen.blit(font.render(line, True, Colors.TEXT), (80, y))
            y += font.get_linesize() + 2

        # Курсор
        if self.tw_text != self.tw_target and self.tw_target:
            if int(self.anim_time * 3) % 2 == 0 and lines:
                cx = 80 + font.size(lines[-1])[0] + 2
                cy = y - font.get_linesize() - 2
                cs = pygame.Surface((2, font.get_linesize()), pygame.SRCALPHA)
                cs.fill((*Colors.ACCENT_BLUE, 180))
                self.screen.blit(cs, (cx, cy))

        # Стрелка "продолжить"
        if (self.tw_text == self.tw_target or not self.tw_target) and "choices" not in node:
            aa = int(120 + 80 * math.sin(self.anim_time * 4))
            self.screen.blit(fonts.small.render("▼", True, Colors.ACCENT_BLUE), (box.right - 35, box.bottom - 28))

    def draw_inventory(self):
        r = pygame.Rect(18, 12, 360, 115)
        draw_panel(self.screen, r, alpha=180, glow=True, glow_color=(60, 90, 130))
        self.screen.blit(fonts.small.render("Инвентарь", True, Colors.ACCENT_BLUE), (35, 22))
        ls = pygame.Surface((330, 1), pygame.SRCALPHA)
        ls.fill((*Colors.PANEL_BORDER, 80))
        self.screen.blit(ls, (35, 45))

        if not self.inventory:
            self.screen.blit(fonts.tiny.render("пусто", True, Colors.HINT), (35, 55))
            return
        for i, item in enumerate(self.inventory[:4]):
            col, row = i % 2, i // 2
            x, y = 35 + col * 170, 55 + row * 30
            # Иконка-бейдж
            icon_letter = ITEM_ICONS.get(item, "?")
            badge = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.rect(badge, (*Colors.ACCENT_AMBER, 180), (0, 0, 18, 18), border_radius=4)
            il = fonts.icon.render(icon_letter, True, Colors.BLACK)
            badge.blit(il, (9 - il.get_width() // 2, 9 - il.get_height() // 2))
            self.screen.blit(badge, (x, y))
            self.screen.blit(fonts.tiny.render(ITEM_NAMES.get(item, item), True, Colors.TEXT), (x + 24, y + 1))

    def draw_stats(self):
        r = pygame.Rect(690, 12, 292, 155)
        draw_panel(self.screen, r, alpha=180, glow=True, glow_color=(60, 90, 130))

        stats = [
            ("Смелость", self.trust, 10, Colors.STAT["trust"]),
            ("Внимательность", self.knowledge, 10, Colors.STAT["knowledge"]),
            ("Страх", self.fear, 10, Colors.STAT["fear"]),
            ("Шум", self.noise, 10, Colors.STAT["noise"]),
            ("Время", self.time_left, 8, Colors.STAT["time"]),
        ]
        y = 24
        for label, val, mx, color in stats:
            self.screen.blit(fonts.tiny.render(label, True, Colors.TEXT_DIM), (708, y))
            self.screen.blit(fonts.tiny.render(str(val), True, color), (955, y))
            draw_progress_bar(self.screen, 810, y + 3, 138, 12, val, mx, color)
            y += 27

    def draw_save_message(self):
        if not self.save_message or self.save_message_timer <= 0:
            return
        alpha = int(min(255, self.save_message_timer * 510)) if self.save_message_timer < 0.5 else 255
        msg = fonts.small.render(self.save_message, True, Colors.SAVE_MSG)
        mw, mh = msg.get_width() + 40, 36
        mx, my = WIDTH // 2 - mw // 2, 410
        bg = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.rect(bg, (15, 20, 35, int(alpha * 0.85)), (0, 0, mw, mh), border_radius=8)
        pygame.draw.rect(bg, (*Colors.SAVE_MSG, int(alpha * 0.5)), (0, 0, mw, mh), width=1, border_radius=8)
        self.screen.blit(bg, (mx, my))
        msg.set_alpha(alpha)
        self.screen.blit(msg, (mx + 20, my + 8))

    def draw_popups(self):
        for p in self.stat_popups:
            p.draw(self.screen)

    def draw_choice_buttons(self, dt):
        node = self.story.get(self.current_node, {})
        choices = node.get("choices", [])
        if not choices:
            return []

        if self.choice_appear_node != self.current_node:
            self.choice_appear_node = self.current_node
            self.choice_appear_timer = 0.0
        self.choice_appear_timer += dt

        buttons = []
        bh, gap = 48, 12
        total = len(choices) * bh + (len(choices) - 1) * gap
        y = 230 + max(0, 220 - total) // 2

        mouse = pygame.mouse.get_pos()
        for i, choice in enumerate(choices):
            btn = Button(490, y, 450, bh, choice["text"], self.choice_is_available(choice))
            delay = i * 0.12
            progress = max(0, min(1, (self.choice_appear_timer - delay) / 0.4))
            btn.update(mouse, dt)
            btn.draw(self.screen, mouse, appear_progress=progress, pulse_time=self.pulse_time)

            if not self.choice_is_available(choice) and progress > 0.5:
                la = int(min(255, (progress - 0.5) * 2 * 255))
                lt = fonts.tiny.render(self.get_choice_lock_text(choice), True, Colors.SAVE_MSG)
                lt.set_alpha(la)
                self.screen.blit(lt, (btn.rect.x + 14, btn.rect.y + btn.rect.height + 3))

            buttons.append(btn)
            y += bh + gap
        return buttons

    # ------- ЭКРАНЫ -------
    def draw_menu(self, dt):
        self.draw_bg()
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 160))
        self.screen.blit(o, (0, 0))
        self.draw_particles()
        self.draw_vignette()

        # Заголовок
        t = "Школьный Коридор"
        if self.glitch_active:
            for color, dx, dy in [((255, 60, 60), self.glitch_offset - 3, random.randint(-2, 2)),
                                   ((60, 255, 60), self.glitch_offset + 3, random.randint(-2, 2)),
                                   ((60, 60, 255), -self.glitch_offset, 0)]:
                s = fonts.title.render(t, True, color)
                s.set_alpha(120)
                self.screen.blit(s, (WIDTH // 2 - fonts.title.size(t)[0] // 2 + dx, 80 + dy))
        else:
            ts = fonts.title.render(t, True, (0, 0, 0))
            ts.set_alpha(100)
            cx = WIDTH // 2 - fonts.title.size(t)[0] // 2
            self.screen.blit(ts, (cx + 3, 83))
            self.screen.blit(fonts.title.render(t, True, Colors.TEXT_BRIGHT), (cx, 80))

        # Подзаголовок
        sub = fonts.text.render("Мини-хоррор новелла", True, Colors.ACCENT_RED)
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 145))

        # Линия
        lw = 200
        ls = pygame.Surface((lw, 2), pygame.SRCALPHA)
        for lx in range(lw):
            a = int(80 * (1 - abs(lx - lw / 2) / (lw / 2)))
            pygame.draw.line(ls, (*Colors.ACCENT_RED, a), (lx, 0), (lx, 1))
        self.screen.blit(ls, (WIDTH // 2 - lw // 2, 180))

        # Описание
        info = fonts.small.render("Сделай выбор и попробуй выбраться из темной школы.", True, Colors.TEXT_DIM)
        self.screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 200))

        # Версия
        ver = fonts.tiny.render("v2.0 — Exam Edition", True, Colors.HINT)
        self.screen.blit(ver, (WIDTH - ver.get_width() - 15, HEIGHT - 22))

        mouse = pygame.mouse.get_pos()
        for btn in [self.start_btn, self.load_btn, self.settings_btn, self.exit_btn]:
            btn.update(mouse, dt)
            btn.draw(self.screen, mouse, pulse_time=self.pulse_time)

        self.draw_save_message()

    def draw_settings_screen(self, dt):
        self.draw_bg()
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 180))
        self.screen.blit(o, (0, 0))
        self.draw_vignette()

        panel = pygame.Rect(200, 80, 600, 480)
        draw_panel(self.screen, panel, alpha=230, glow=True, glow_color=Colors.ACCENT_BLUE)

        self.screen.blit(fonts.name.render("Настройки", True, Colors.ACCENT_BLUE), (220, 100))

        # Громкость
        y = 160
        for label, attr, display_fn in [
            ("Громкость", "master_volume", lambda v: f"{int(v * 100)}%"),
            ("Звуковые эффекты", "sfx_volume", lambda v: f"{int(v * 100)}%"),
            ("Скорость текста", "text_speed", lambda v: f"{['Быстро', 'Средне', 'Медленно'][min(2, int(v / 0.025))]}"),
        ]:
            self.screen.blit(fonts.small.render(label, True, Colors.TEXT), (240, y))
            val = getattr(self.settings, attr)
            self.screen.blit(fonts.small.render(display_fn(val), True, Colors.ACCENT_AMBER), (620, y))

            # Слайдер
            bar_x, bar_y, bar_w = 240, y + 30, 500
            pygame.draw.rect(self.screen, (30, 35, 50), (bar_x, bar_y, bar_w, 8), border_radius=4)

            if attr == "text_speed":
                fill = 1.0 - (val - 0.01) / 0.05
            else:
                fill = val
            fill = max(0, min(1, fill))
            fw = int(fill * bar_w)
            if fw > 0:
                color = Colors.ACCENT_BLUE
                pygame.draw.rect(self.screen, color, (bar_x, bar_y, fw, 8), border_radius=4)

            # Ручка
            hx = bar_x + fw
            pygame.draw.circle(self.screen, Colors.TEXT_BRIGHT, (hx, bar_y + 4), 8)
            pygame.draw.circle(self.screen, Colors.ACCENT_BLUE, (hx, bar_y + 4), 6)

            y += 80

        mouse = pygame.mouse.get_pos()
        self.settings_back_btn.update(mouse, dt)
        self.settings_back_btn.draw(self.screen, mouse, pulse_time=self.pulse_time)

    def draw_saves_screen(self, dt):
        self.draw_bg()
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 180))
        self.screen.blit(o, (0, 0))
        self.draw_vignette()

        panel = pygame.Rect(200, 60, 600, 520)
        draw_panel(self.screen, panel, alpha=230, glow=True, glow_color=Colors.ACCENT_BLUE)

        title = "Загрузить игру" if self.save_mode == "load" else "Сохранить игру"
        self.screen.blit(fonts.name.render(title, True, Colors.ACCENT_BLUE), (220, 80))

        # Автосохранение (только для загрузки)
        y = 130
        if self.save_mode == "load":
            auto = SaveSystem.load_auto()
            auto_text = "Автосохранение: "
            if auto:
                auto_text += f"узел {auto.get('current_node', '?')}, время {auto.get('time_left', '?')}"
            else:
                auto_text += "пусто"
            self.screen.blit(fonts.tiny.render(auto_text, True, Colors.TEXT_DIM), (240, y))
            y += 30

        # Слоты
        self.save_slot_btns = []
        for slot in range(1, SaveSystem.MAX_SLOTS + 1):
            info = SaveSystem.get_slot_info(slot)
            if info:
                text = f"Слот {slot}: время {info['time_left']}, предметов {info['items']}"
            else:
                text = f"Слот {slot}: пусто"
            enabled = True if self.save_mode == "save" else (info is not None)
            btn = Button(250, y, 500, 50, text, enabled=enabled)
            self.save_slot_btns.append((btn, slot))
            y += 65

        mouse = pygame.mouse.get_pos()
        for btn, _ in self.save_slot_btns:
            btn.update(mouse, dt)
            btn.draw(self.screen, mouse, pulse_time=self.pulse_time)

        self.save_back_btn.update(mouse, dt)
        self.save_back_btn.draw(self.screen, mouse, pulse_time=self.pulse_time)

        self.draw_save_message()

    def draw_story(self, dt):
        self.draw_bg()
        self.draw_character()
        self.draw_particles()
        self.draw_flicker()
        self.draw_vignette()
        self.draw_inventory()
        self.draw_stats()
        self.draw_text_box()

        node = self.story.get(self.current_node, {})
        if "choices" in node:
            self.choice_buttons = self.draw_choice_buttons(dt)
            h = fonts.tiny.render("S — сохранить   L — загрузить   H — история", True, Colors.HINT)
        else:
            self.choice_buttons = []
            h = fonts.tiny.render("SPACE/клик — дальше   S — сохранить   L — загрузить   H — история", True, Colors.HINT)
        self.screen.blit(h, (WIDTH - h.get_width() - 15, HEIGHT - 20))

        self.draw_save_message()
        self.draw_popups()
        self.draw_scene_fade()

    def draw_result(self):
        self.draw_bg()
        o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        o.fill((0, 0, 0, 180))
        self.screen.blit(o, (0, 0))
        self.draw_vignette()

        panel = pygame.Rect(90, 50, 820, 550)
        draw_panel(self.screen, panel, alpha=230, glow=True, glow_color=Colors.ACCENT_RED)

        self.screen.blit(fonts.title.render("Финал", True, Colors.ACCENT_RED),
                         (panel.centerx - fonts.title.size("Финал")[0] // 2, 70))

        lw = 300
        ls = pygame.Surface((lw, 2), pygame.SRCALPHA)
        for lx in range(lw):
            a = int(80 * (1 - abs(lx - lw / 2) / (lw / 2)))
            pygame.draw.line(ls, (*Colors.ACCENT_RED, a), (lx, 0), (lx, 1))
        self.screen.blit(ls, (panel.centerx - lw // 2, 125))

        et, ed = self._get_ending()
        es = fonts.name.render(et, True, Colors.ACCENT_RED_GLOW)
        self.screen.blit(es, (panel.centerx - es.get_width() // 2, 145))

        lines = wrap_text(ed, fonts.text, 680)
        y = 200
        for line in lines:
            self.screen.blit(fonts.text.render(line, True, Colors.TEXT), (160, y))
            y += 34

        sy = max(y + 20, 340)
        stats = [
            ("Смелость", self.trust, 10, Colors.STAT["trust"]),
            ("Внимательность", self.knowledge, 10, Colors.STAT["knowledge"]),
            ("Страх", self.fear, 10, Colors.STAT["fear"]),
            ("Шум", self.noise, 10, Colors.STAT["noise"]),
            ("Время", self.time_left, 8, Colors.STAT["time"]),
        ]
        for i, (label, val, mx, color) in enumerate(stats):
            sx = 160 + (i % 3) * 230
            ssy = sy + (i // 3) * 40
            self.screen.blit(fonts.small.render(f"{label}: {val}", True, color), (sx, ssy))
            draw_progress_bar(self.screen, sx, ssy + 24, 180, 8, val, mx, color)

        iy = sy + 90
        inv = "Инвентарь: " + (", ".join(ITEM_NAMES.get(i, i) for i in self.inventory) if self.inventory else "пусто")
        self.screen.blit(fonts.small.render(inv, True, Colors.TEXT_DIM), (160, iy))

        if self.last_choice:
            self.screen.blit(fonts.tiny.render(f"Последний выбор: {self.last_choice}", True, Colors.HINT), (160, iy + 30))

        self.screen.blit(fonts.tiny.render("R — перезапуск    ESC — выход", True, Colors.HINT),
                         (panel.centerx - 120, panel.bottom - 35))

    def _get_ending(self):
        if self.time_left == 0:
            return ("Слишком поздно", "Школа забрала твое время. Выход был рядом, но коридор успел перестроиться.")
        elif self.fear >= 5:
            return ("Паника", "Ты добрался до выхода, но страх спутал все воспоминания.")
        elif self.noise >= 7:
            return ("Разбуженный коридор", "Ты выбрался, но слишком много дверей хлопнуло по пути.")
        elif len(self.inventory) >= 4 and self.trust >= 2 and self.knowledge >= 3:
            return ("Полный побег", "Ты собрал подсказки и не потерял решимость. Коридор остался позади.")
        elif self.trust >= 3 and self.knowledge >= 3:
            return ("Побег", "Хладнокровие и бдительность помогли тебе выбраться из школы.")
        elif abs(self.trust - self.knowledge) <= 1:
            return ("Сквозь страх", "Ты выбрался, но этот коридор ещё долго будет сниться.")
        elif self.knowledge > self.trust:
            return ("Холодный расчет", "Внимательность спасла тебе жизнь. Ты замечал то, что другие пропустили бы.")
        elif self.trust > self.knowledge:
            return ("Рывок в темноту", "Решимость спасла тебя в последний момент.")
        return ("Неровный побег", "Путь получился опасным. Школа отпустила тебя, оставив вопросы.")

    # ------- ОСНОВНОЙ ЦИКЛ -------
    def run(self):
        self.choice_buttons = []

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self.update(dt)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.dialog_log.visible:
                        self.dialog_log.toggle()
                    elif self.state in ("settings", "saves"):
                        self.state = "menu"
                    else:
                        self.running = False

                # Прокрутка лога
                if event.type == pygame.MOUSEWHEEL and self.dialog_log.visible:
                    self.dialog_log.scroll(-event.y * 2)

                if self.state == "menu":
                    if self.start_btn.is_clicked(event):
                        self.state = "story"
                        self.sound.start_ambient()
                        self.sound.play("click")
                    if self.load_btn.is_clicked(event):
                        self.save_mode = "load"
                        self.state = "saves"
                        self.sound.play("click")
                    if self.settings_btn.is_clicked(event):
                        self.state = "settings"
                        self.sound.play("click")
                    if self.exit_btn.is_clicked(event):
                        self.running = False

                elif self.state == "settings":
                    if self.settings_back_btn.is_clicked(event):
                        self.settings.save()
                        self.state = "menu"
                        self.sound.play("click")

                    # Слайдеры
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        bar_x, bar_w = 240, 500
                        for i, attr in enumerate(["master_volume", "sfx_volume", "text_speed"]):
                            bar_y = 160 + i * 80 + 30
                            if bar_x <= mx <= bar_x + bar_w and bar_y - 10 <= my <= bar_y + 18:
                                t = (mx - bar_x) / bar_w
                                if attr == "text_speed":
                                    setattr(self.settings, attr, max(0.01, 0.06 - t * 0.05))
                                else:
                                    setattr(self.settings, attr, max(0.0, min(1.0, t)))
                                self.sound.set_master_volume(self.settings.master_volume)
                                self.sound.sfx_volume = self.settings.sfx_volume

                    if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                        mx, my = event.pos
                        bar_x, bar_w = 240, 500
                        for i, attr in enumerate(["master_volume", "sfx_volume", "text_speed"]):
                            bar_y = 160 + i * 80 + 30
                            if bar_x <= mx <= bar_x + bar_w and bar_y - 10 <= my <= bar_y + 18:
                                t = (mx - bar_x) / bar_w
                                if attr == "text_speed":
                                    setattr(self.settings, attr, max(0.01, 0.06 - t * 0.05))
                                else:
                                    setattr(self.settings, attr, max(0.0, min(1.0, t)))
                                self.sound.set_master_volume(self.settings.master_volume)
                                self.sound.sfx_volume = self.settings.sfx_volume

                elif self.state == "saves":
                    if self.save_back_btn.is_clicked(event):
                        self.state = "menu" if self.state != "story" else "story"
                        self.sound.play("click")
                        # При выходе из save во время игры — вернуть в сторию
                        if hasattr(self, '_return_to_story') and self._return_to_story:
                            self.state = "story"
                            self._return_to_story = False
                        else:
                            self.state = "menu"

                    # Автозагрузка
                    if self.save_mode == "load" and event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                        data = SaveSystem.load_auto()
                        if data and self._apply_save_data(data):
                            self.save_message = "Автосохранение загружено"
                            self.save_message_timer = 2.0
                            self.sound.start_ambient()
                            self.sound.play("save")

                    for btn, slot in self.save_slot_btns:
                        if btn.is_clicked(event):
                            if self.save_mode == "save":
                                if SaveSystem.save(slot, self._get_save_data()):
                                    self.save_message = f"Сохранено в слот {slot}"
                                    self.save_message_timer = 2.0
                                    self.sound.play("save")
                            else:
                                data = SaveSystem.load(slot)
                                if data and self._apply_save_data(data):
                                    self.save_message = f"Загружено из слота {slot}"
                                    self.save_message_timer = 2.0
                                    self.sound.start_ambient()
                                    self.sound.play("save")

                elif self.state == "story":
                    if self.dialog_log.visible:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_h:
                                self.dialog_log.toggle()
                            elif event.key == pygame.K_UP:
                                self.dialog_log.scroll(-1)
                            elif event.key == pygame.K_DOWN:
                                self.dialog_log.scroll(1)
                        continue

                    node = self.story.get(self.current_node, {})

                    if "choices" in node:
                        for btn in self.choice_buttons:
                            if btn.is_clicked(event):
                                idx = self.choice_buttons.index(btn)
                                self.apply_choice(node["choices"][idx])
                    else:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            self.advance_story()
                        inv_rect = pygame.Rect(18, 12, 360, 115)
                        stats_rect = pygame.Rect(690, 12, 292, 155)
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if not inv_rect.collidepoint(event.pos) and not stats_rect.collidepoint(event.pos):
                                self.advance_story()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            self.save_mode = "save"
                            self._return_to_story = True
                            self.state = "saves"
                            self.sound.play("click")
                        if event.key == pygame.K_l:
                            self.save_mode = "load"
                            self._return_to_story = True
                            self.state = "saves"
                            self.sound.play("click")
                        if event.key == pygame.K_h:
                            self.dialog_log.toggle()

                elif self.state == "result":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset_game()

            # === ОТРИСОВКА ===
            if self.state == "menu":
                self.draw_menu(dt)
            elif self.state == "settings":
                self.draw_settings_screen(dt)
            elif self.state == "saves":
                self.draw_saves_screen(dt)
            elif self.state == "story":
                self.draw_story(dt)
            elif self.state == "result":
                self.draw_result()
                self.draw_particles()

            self.dialog_log.draw(self.screen)
            self.draw_scene_fade()
            pygame.display.flip()

        self.settings.save()
        pygame.quit()
        sys.exit()


# ============================================================
# ЗАПУСК
# ============================================================
game = Game()
game.run()
