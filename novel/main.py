
import pygame
import sys
import json
from pathlib import Path

pygame.init()

# -----------------------------
# НАСТРОЙКИ ОКНА
# -----------------------------
WIDTH = 1000
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Novel Prototype")
clock = pygame.time.Clock()

# -----------------------------
# ПУТИ К ФАЙЛАМ
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
CHARACTER_PATH = BASE_DIR / "assets" / "characters" / "visitor.png"
BACKGROUND_PATH = BASE_DIR / "assets" / "backgrounds" / "school.png"
SAVE_PATH = BASE_DIR / "save_data.json"

# -----------------------------
# ЦВЕТА
# -----------------------------
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DARK = (18, 18, 18)
SOFT_DARK = (35, 35, 35)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
BLUE = (120, 170, 255)
LIGHT_BLUE = (210, 230, 255)
RED = (220, 100, 100)
GREEN = (120, 220, 150)
YELLOW = (245, 210, 120)
MENU_TITLE_COLOR = (255, 255, 255)
MENU_TEXT_COLOR = (235, 235, 235)
MENU_HINT_COLOR = (210, 210, 210)
SHADOW_COLOR = (0, 0, 0)
STAT_COLOR = (255, 255, 255)
BOX_TEXT_COLOR = (240, 240, 240)
BOX_NAME_COLOR = (255, 255, 255)
BOX_HINT_COLOR = (200, 200, 200)

# -----------------------------
# ШРИФТЫ
# -----------------------------
title_font = pygame.font.SysFont("arial", 48, bold=True)
name_font = pygame.font.SysFont("arial", 32, bold=True)
text_font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 22)

# -----------------------------
# ЗАГРУЗКА ИЗОБРАЖЕНИЙ
# -----------------------------
character_img = pygame.image.load(str(CHARACTER_PATH)).convert_alpha()
character_img = pygame.transform.smoothscale(character_img, (220, 420))

background_img = pygame.image.load(str(BACKGROUND_PATH)).convert()
background_img = pygame.transform.smoothscale(background_img, (WIDTH, HEIGHT))

# -----------------------------
# ДАННЫЕ ИГРЫ
# -----------------------------
game_state = "menu"
current_node = "intro_1"

trust = 0
knowledge = 0
fear = 0
noise = 0
time_left = 8
last_choice = ""
inventory = []
save_message = ""

ITEM_NAMES = {
    "map": "План школы",
    "key": "Медный ключ",
    "note": "Записка",
    "flashlight": "Фонарик"
}

ITEM_DESCRIPTIONS = {
    "map": "показывает короткий путь к лестнице",
    "key": "открывает старую дверь у подсобки",
    "note": "подсказывает, когда коридор становится безопасным",
    "flashlight": "помогает не потеряться в темном крыле"
}

# -----------------------------
# СТРУКТУРА СЦЕНАРИЯ
# -----------------------------
story = {
    "intro_1": {
        "speaker": "Рассказчик",
        "text": "Ты приходишь в себя в пустом школьном коридоре.",
        "next": "intro_2"
    },
    "intro_2": {
        "speaker": "Рассказчик",
        "text": "Свет мигает, а вдалеке раздаются чьи-то медленные шаги.",
        "next": "intro_3"
    },
    "intro_3": {
        "speaker": "Неизвестный голос",
        "text": "Если хочешь выбраться отсюда, не стой на месте.",
        "next": "choice_1"
    },
    "choice_1": {
        "speaker": "Рассказчик",
        "text": "Что ты сделаешь первым?",
        "choices": [
            {
                "text": "Пойти на странный звук",
                "next": "plot_path",
                "trust": 1,
                "knowledge": 0,
                "fear": 1,
                "noise": 1,
                "time": -1
            },
            {
                "text": "Осмотреть коридор вокруг",
                "next": "system_path",
                "trust": 0,
                "knowledge": 1,
                "fear": 0,
                "noise": 0,
                "time": -1,
                "item": "map"
            }
        ]
    },
    "plot_path": {
        "speaker": "Рассказчик",
        "text": "Ты идешь вперед, стараясь не показывать страх.",
        "next": "middle_1"
    },
    "system_path": {
        "speaker": "Рассказчик",
        "text": "Ты замечаешь следы на полу и приоткрытую дверь сбоку.",
        "next": "middle_1"
    },
    "middle_1": {
        "speaker": "Рассказчик",
        "text": "В конце коридора что-то шевельнулось.",
        "next": "choice_2"
    },
    "choice_2": {
        "speaker": "Рассказчик",
        "text": "Как поступить?",
        "choices": [
            {
                "text": "Окликнуть того, кто там стоит",
                "next": "character_path",
                "trust": 1,
                "knowledge": 0,
                "fear": 1,
                "noise": 2,
                "time": -1
            },
            {
                "text": "Молча проверить дверь",
                "next": "score_path",
                "trust": 0,
                "knowledge": 1,
                "fear": 0,
                "noise": 0,
                "time": -1,
                "item": "key"
            }
        ]
    },
    "character_path": {
        "speaker": "Рассказчик",
        "text": "В ответ слышится только эхо, но шаги становятся ближе.",
        "next": "middle_2"
    },
    "score_path": {
        "speaker": "Рассказчик",
        "text": "За дверью ты находишь схему здания и путь к лестнице.",
        "next": "middle_2"
    },
    "middle_2": {
        "speaker": "Рассказчик",
        "text": "Теперь ты точно знаешь: в коридоре кроме тебя есть кто-то еще.",
        "next": "choice_3"
    },
    "choice_3": {
        "speaker": "Рассказчик",
        "text": "Последнее решение:",
        "choices": [
            {
                "text": "Бежать к лестнице",
                "next": "stairs_path",
                "trust": 1,
                "knowledge": 0,
                "fear": 1,
                "noise": 2,
                "time": -1
            },
            {
                "text": "Спрятаться и дождаться тишины",
                "next": "library_path",
                "trust": 0,
                "knowledge": 1,
                "fear": -1,
                "noise": 0,
                "time": -2,
                "item": "note"
            }
        ]
    },
    "design_path": {
        "speaker": "Рассказчик",
        "text": "Ты срываешься с места, пока тень за спиной начинает двигаться быстрее.",
        "next": "final_check"
    },
    "code_path": {
        "speaker": "Рассказчик",
        "text": "Ты замираешь в темноте и стараешься не издать ни звука.",
        "next": "final_check"
    },
    "stairs_path": {
        "speaker": "Рассказчик",
        "text": "Ты несешься к лестнице. Перила холодные, ступени мокрые, а за спиной скребет что-то металлическое.",
        "next": "stairs_choice"
    },
    "stairs_choice": {
        "speaker": "Рассказчик",
        "text": "На площадке две двери: одна ведет к аварийному выходу, другая - в темное крыло школы.",
        "choices": [
            {
                "text": "Открыть аварийную дверь ключом",
                "next": "exit_door",
                "trust": 1,
                "knowledge": 1,
                "fear": -1,
                "noise": 1,
                "time": -1,
                "requires": "key"
            },
            {
                "text": "Сверить путь с планом школы",
                "next": "map_route",
                "trust": 0,
                "knowledge": 2,
                "fear": 0,
                "noise": 0,
                "time": -1,
                "requires": "map"
            },
            {
                "text": "Толкнуть дверь плечом",
                "next": "loud_route",
                "trust": 1,
                "knowledge": 0,
                "fear": 2,
                "noise": 3,
                "time": -2
            }
        ]
    },
    "library_path": {
        "speaker": "Рассказчик",
        "text": "Ты проскальзываешь в библиотеку. Между стеллажами пахнет пылью, мокрой бумагой и чем-то озоновым.",
        "next": "library_choice"
    },
    "library_choice": {
        "speaker": "Рассказчик",
        "text": "На столе лежит фонарик, а на доске мелом написано: 'Не верь первому звонку'.",
        "choices": [
            {
                "text": "Взять фонарик",
                "next": "flashlight_scene",
                "trust": 0,
                "knowledge": 1,
                "fear": -1,
                "noise": 0,
                "time": -1,
                "item": "flashlight"
            },
            {
                "text": "Прочитать записку внимательнее",
                "next": "note_scene",
                "trust": 0,
                "knowledge": 2,
                "fear": 0,
                "noise": 0,
                "time": -1,
                "requires": "note"
            },
            {
                "text": "Сразу выйти через запасной проход",
                "next": "silent_route",
                "trust": 1,
                "knowledge": 0,
                "fear": 1,
                "noise": 1,
                "time": -1
            }
        ]
    },
    "exit_door": {
        "speaker": "Рассказчик",
        "text": "Ключ подходит не сразу. Замок сопротивляется, затем щелкает, и в щель врывается холодный воздух.",
        "next": "alarm_scene"
    },
    "map_route": {
        "speaker": "Рассказчик",
        "text": "На плане ты замечаешь служебный коридор за лестницей. Он длиннее, зато обходит место, откуда доносятся шаги.",
        "next": "alarm_scene"
    },
    "loud_route": {
        "speaker": "Рассказчик",
        "text": "Дверь поддается с глухим ударом. Где-то внизу тут же просыпается звонок, хотя уроки давно закончились.",
        "next": "alarm_scene"
    },
    "flashlight_scene": {
        "speaker": "Рассказчик",
        "text": "Фонарик моргает слабым желтым светом. На полу проявляются следы, ведущие не к выходу, а к кабинету директора.",
        "next": "principal_choice"
    },
    "note_scene": {
        "speaker": "Рассказчик",
        "text": "В записке сказано, что звонок повторяется три раза. После третьего коридор пустеет ровно на минуту.",
        "next": "principal_choice"
    },
    "silent_route": {
        "speaker": "Рассказчик",
        "text": "Ты выходишь через узкий проход между стеллажами. Пол скрипит, но шаги в коридоре на мгновение отдаляются.",
        "next": "principal_choice"
    },
    "alarm_scene": {
        "speaker": "Рассказчик",
        "text": "Звонок режет воздух. В окнах отражается не твое лицо, а силуэт в школьной форме, стоящий прямо за плечом.",
        "next": "last_choice"
    },
    "principal_choice": {
        "speaker": "Рассказчик",
        "text": "У кабинета директора дверь приоткрыта. Внутри слышен старый магнитофон: он повторяет твое имя.",
        "choices": [
            {
                "text": "Осветить кабинет фонариком",
                "next": "truth_scene",
                "trust": 0,
                "knowledge": 2,
                "fear": -1,
                "noise": 0,
                "time": -1,
                "requires": "flashlight"
            },
            {
                "text": "Ждать третьего звонка",
                "next": "timed_escape",
                "trust": 0,
                "knowledge": 2,
                "fear": 0,
                "noise": 0,
                "time": -1,
                "requires": "note"
            },
            {
                "text": "Захлопнуть дверь и бежать",
                "next": "panic_escape",
                "trust": 2,
                "knowledge": 0,
                "fear": 2,
                "noise": 2,
                "time": -2
            }
        ]
    },
    "truth_scene": {
        "speaker": "Рассказчик",
        "text": "Луч фонаря выхватывает журнал посещений. Последняя строка написана сегодняшней датой, но твоей рукой.",
        "next": "last_choice"
    },
    "timed_escape": {
        "speaker": "Рассказчик",
        "text": "Ты считаешь удары сердца. После третьего звонка коридор пустеет, словно школа задержала дыхание.",
        "next": "last_choice"
    },
    "panic_escape": {
        "speaker": "Рассказчик",
        "text": "Ты бежишь, не разбирая дороги. Двери хлопают одна за другой, и каждая звучит как ответ на твой страх.",
        "next": "last_choice"
    },
    "last_choice": {
        "speaker": "Рассказчик",
        "text": "До выхода осталось несколько шагов. Но школьный коридор вытягивается, будто не хочет отпускать тебя.",
        "choices": [
            {
                "text": "Сохранять тишину и идти по памяти",
                "next": "quiet_final",
                "trust": 0,
                "knowledge": 1,
                "fear": -1,
                "noise": -1,
                "time": -1
            },
            {
                "text": "Рвануть к свету у двери",
                "next": "brave_final",
                "trust": 2,
                "knowledge": 0,
                "fear": 1,
                "noise": 2,
                "time": -1
            },
            {
                "text": "Использовать все, что удалось найти",
                "next": "prepared_final",
                "trust": 1,
                "knowledge": 1,
                "fear": -2,
                "noise": 0,
                "time": -1,
                "requires_any": ["map", "key", "note", "flashlight"]
            }
        ]
    },
    "quiet_final": {
        "speaker": "Рассказчик",
        "text": "Ты идешь медленно, почти не дыша. Когда ручка двери оказывается в ладони, шаги за спиной исчезают.",
        "next": "final_check"
    },
    "brave_final": {
        "speaker": "Рассказчик",
        "text": "Ты бросаешься вперед. Свет ударяет в глаза, и на секунду кажется, что весь коридор разбивается на осколки.",
        "next": "final_check"
    },
    "prepared_final": {
        "speaker": "Рассказчик",
        "text": "Карта, ключ, записка и свет фонаря складываются в один путь. Теперь школа уже не лабиринт, а задача.",
        "next": "final_check"
    },
    "time_out": {
        "speaker": "Рассказчик",
        "text": "Ты слишком долго искал выход. Звонок звучит снова, и коридор меняется быстрее, чем ты успеваешь сделать шаг.",
        "next": "final_check"
    },
    "final_check": {
        "speaker": "Рассказчик",
        "text": "Шаги уже совсем рядом. Сейчас все решится.",
        "next": "ending"
    }
}


# -----------------------------
# КЛАСС КНОПКИ
# -----------------------------
class Button:
    def __init__(self, x, y, w, h, text, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.enabled = enabled

    def draw(self, surface, mouse_pos):
        if not self.enabled:
            color = GRAY
            text_color = SOFT_DARK
        elif self.rect.collidepoint(mouse_pos):
            color = LIGHT_BLUE
            text_color = BLACK
        else:
            color = BLUE
            text_color = BLACK

        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)

        label_font = text_font
        if label_font.size(self.text)[0] > self.rect.width - 30:
            label_font = small_font

        label = label_font.render(self.text, True, text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def is_clicked(self, event):
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


# -----------------------------
# ФУНКЦИИ РИСОВАНИЯ
# -----------------------------
def draw_background():
    screen.blit(background_img, (0, 0))


def draw_character():
    screen.blit(character_img, (70, 60))


def draw_text_box(speaker, text):
    box_rect = pygame.Rect(60, 470, 880, 150)

    panel = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    panel.fill((12, 12, 12, 230))
    screen.blit(panel, box_rect.topleft)

    pygame.draw.rect(screen, LIGHT_GRAY, box_rect, 2, border_radius=16)

    speaker_surface = name_font.render(speaker, True, BOX_NAME_COLOR)
    screen.blit(speaker_surface, (85, 490))

    wrapped_lines = wrap_text(text, text_font, 820)

    y = 535
    for line in wrapped_lines:
        line_surface = text_font.render(line, True, BOX_TEXT_COLOR)
        screen.blit(line_surface, (85, y))
        y += 32


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines


def get_inventory_text():
    if len(inventory) == 0:
        return "Инвентарь: пусто"

    item_names = []
    for item in inventory:
        item_names.append(ITEM_NAMES.get(item, item))

    return "Инвентарь: " + ", ".join(item_names)


def draw_inventory():
    panel_rect = pygame.Rect(25, 15, 360, 90)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 120))
    screen.blit(panel, panel_rect.topleft)
    pygame.draw.rect(screen, LIGHT_GRAY, panel_rect, 1, border_radius=10)

    title = small_font.render(get_inventory_text(), True, WHITE)
    screen.blit(title, (40, 28))

    y = 55
    for item in inventory[:2]:
        description = ITEM_DESCRIPTIONS.get(item, "")
        line = small_font.render("- " + ITEM_NAMES.get(item, item) + ": " + description, True, MENU_HINT_COLOR)
        screen.blit(line, (40, y))
        y += 22


def draw_save_message(y=438):
    if save_message == "":
        return

    message = small_font.render(save_message, True, YELLOW)
    screen.blit(message, (60, y))


def draw_stats():
    trust_text = small_font.render(f"Смелость: {trust}", True, STAT_COLOR)
    knowledge_text = small_font.render(f"Внимательность: {knowledge}", True, STAT_COLOR)
    fear_text = small_font.render(f"Страх: {fear}", True, STAT_COLOR)
    noise_text = small_font.render(f"Шум: {noise}", True, STAT_COLOR)
    time_text = small_font.render(f"Время: {time_left}", True, STAT_COLOR)

    screen.blit(trust_text, (730, 15))
    screen.blit(knowledge_text, (730, 40))
    screen.blit(fear_text, (730, 65))
    screen.blit(noise_text, (730, 90))
    screen.blit(time_text, (730, 115))


def draw_menu():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    title = title_font.render("Школьный Коридор", True, MENU_TITLE_COLOR)
    subtitle = text_font.render("Мини-хоррор новелла", True, MENU_TEXT_COLOR)

    info_1 = small_font.render("Сделай выбор и попробуй выбраться из темной школы.", True, MENU_TEXT_COLOR)
    info_2 = small_font.render("Нажми START, чтобы начать.", True, MENU_HINT_COLOR)
    info_3 = small_font.render("L - загрузить сохранение", True, MENU_HINT_COLOR)

    title_shadow = title_font.render("Школьный Коридор", True, SHADOW_COLOR)
    subtitle_shadow = text_font.render("Мини-хоррор новелла", True, SHADOW_COLOR)

    screen.blit(title_shadow, (273, 133))
    screen.blit(subtitle_shadow, (333, 198))

    screen.blit(title, (270, 130))
    screen.blit(subtitle, (330, 195))
    screen.blit(info_1, (220, 260))
    screen.blit(info_2, (350, 290))
    screen.blit(info_3, (385, 320))
    draw_save_message(335)


def draw_result():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(110, 70, 780, 520)
    pygame.draw.rect(screen, DARK, panel, border_radius=20)
    pygame.draw.rect(screen, LIGHT_GRAY, panel, 2, border_radius=20)

    title = title_font.render("Финал", True, WHITE)
    screen.blit(title, (420, 100))

    ending_title, ending_text = get_ending()

    ending_surface = name_font.render(ending_title, True, RED)
    screen.blit(ending_surface, (360, 180))

    lines = wrap_text(ending_text, text_font, 620)
    y = 250
    for line in lines:
        line_surface = text_font.render(line, True, MENU_TEXT_COLOR)
        screen.blit(line_surface, (180, y))
        y += 38

    stats_1 = text_font.render(f"Смелость: {trust}", True, WHITE)
    stats_2 = text_font.render(f"Внимательность: {knowledge}", True, WHITE)
    stats_3 = text_font.render(f"Страх: {fear}", True, WHITE)
    stats_4 = text_font.render(f"Шум: {noise}", True, WHITE)
    stats_5 = text_font.render(f"Время: {time_left}", True, WHITE)
    items = small_font.render(get_inventory_text(), True, MENU_HINT_COLOR)

    screen.blit(stats_1, (180, 410))
    screen.blit(stats_2, (180, 450))
    screen.blit(stats_3, (430, 410))
    screen.blit(stats_4, (430, 450))
    screen.blit(stats_5, (650, 410))
    screen.blit(items, (180, 485))

    if last_choice != "":
        choice_surface = small_font.render(f"Последний выбор: {last_choice}", True, MENU_HINT_COLOR)
        screen.blit(choice_surface, (180, 520))

    restart_surface = small_font.render("R - перезапуск, L - загрузка, ESC - выход", True, LIGHT_GRAY)
    screen.blit(restart_surface, (180, 560))


def get_ending():
    total = trust + knowledge

    if time_left == 0:
        return (
            "Слишком поздно",
            "Школа забрала твое время. Выход был рядом, но коридор успел перестроиться, и дверь исчезла из стены."
        )
    elif noise >= 7:
        return (
            "Разбуженный коридор",
            "Ты выбрался, но слишком много дверей хлопнуло по пути. Теперь школа знает твой голос и будет ждать возвращения."
        )
    elif fear >= 6:
        return (
            "Паника",
            "Ты добрался до выхода, но страх спутал все воспоминания. Снаружи безопасно, однако ты не уверен, что вышел один."
        )
    elif len(inventory) >= 3 and trust >= 2 and knowledge >= 3:
        return (
            "Полный побег",
            "Ты собрал достаточно подсказок и не потерял решимость. Дверь открылась, а школьный коридор остался позади как разгаданная ловушка."
        )
    elif trust >= 2 and knowledge >= 2:
        return (
            "Побег",
            "Ты сохранил хладнокровие и не потерял бдительность. Благодаря этому тебе удалось выбраться из школы."
        )
    elif knowledge > trust:
        return (
            "Холодный расчет",
            "Ты выжил благодаря внимательности. Ты замечал детали, которых хватило, чтобы найти путь наружу."
        )
    elif trust > knowledge:
        return (
            "Рывок в темноту",
            "Ты почти ничего не знал о происходящем, но решился действовать сразу. Это и спасло тебя в последний момент."
        )
    elif total == 0:
        return (
            "Слишком поздно",
            "Ты слишком долго медлил. Когда в коридоре стало тихо, было уже поздно что-либо менять."
        )
    else:
        return (
            "Сквозь страх",
            "Ты выбрался, но еще долго будешь помнить этот коридор, мигающий свет и шаги за спиной."
        )


def choice_is_available(choice):
    if "requires" in choice:
        return choice["requires"] in inventory

    if "requires_any" in choice:
        for item in choice["requires_any"]:
            if item in inventory:
                return True
        return False

    return True


def get_choice_lock_text(choice):
    if "requires" in choice:
        item = ITEM_NAMES.get(choice["requires"], choice["requires"])
        return "Нужно: " + item

    if "requires_any" in choice:
        names = []
        for item in choice["requires_any"]:
            names.append(ITEM_NAMES.get(item, item))
        return "Нужен предмет: " + " / ".join(names)

    return ""


def build_choice_buttons(choices):
    buttons = []
    button_height = 55
    gap = 18
    total_height = len(choices) * button_height + (len(choices) - 1) * gap
    y = 330 - max(0, total_height - 128) // 2

    for choice in choices:
        button = Button(500, y, 430, button_height, choice["text"], choice_is_available(choice))
        buttons.append(button)
        y += button_height + gap

    return buttons


def draw_choice_buttons(choices):
    buttons = build_choice_buttons(choices)
    mouse_pos = pygame.mouse.get_pos()

    for index, button in enumerate(buttons):
        button.draw(screen, mouse_pos)

        choice = choices[index]
        if not choice_is_available(choice):
            lock_text = small_font.render(get_choice_lock_text(choice), True, YELLOW)
            screen.blit(lock_text, (button.rect.x + 14, button.rect.y + button.rect.height + 2))

    return buttons


def add_item(item):
    global save_message

    if item not in inventory:
        inventory.append(item)
        item_name = ITEM_NAMES.get(item, item)
        save_message = "Найден предмет: " + item_name


def apply_choice(choice):
    global current_node
    global trust
    global knowledge
    global fear
    global noise
    global time_left
    global last_choice
    global save_message

    if not choice_is_available(choice):
        save_message = get_choice_lock_text(choice)
        return

    trust = max(0, trust + choice.get("trust", 0))
    knowledge = max(0, knowledge + choice.get("knowledge", 0))
    fear = max(0, fear + choice.get("fear", 0))
    noise = max(0, noise + choice.get("noise", 0))
    time_left = max(0, time_left + choice.get("time", 0))

    last_choice = choice["text"]
    save_message = ""

    if "item" in choice:
        add_item(choice["item"])

    if time_left == 0:
        current_node = "time_out"
    else:
        current_node = choice["next"]


def save_game():
    global save_message

    data = {
        "game_state": game_state,
        "current_node": current_node,
        "trust": trust,
        "knowledge": knowledge,
        "fear": fear,
        "noise": noise,
        "time_left": time_left,
        "last_choice": last_choice,
        "inventory": inventory
    }

    with SAVE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    save_message = "Игра сохранена"


def load_game():
    global game_state
    global current_node
    global trust
    global knowledge
    global fear
    global noise
    global time_left
    global last_choice
    global inventory
    global save_message

    if not SAVE_PATH.exists():
        save_message = "Сохранение не найдено"
        return

    with SAVE_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    loaded_node = data.get("current_node", "intro_1")
    if loaded_node not in story:
        loaded_node = "intro_1"

    game_state = data.get("game_state", "story")
    if game_state not in ("menu", "story", "result"):
        game_state = "story"

    current_node = loaded_node
    trust = data.get("trust", 0)
    knowledge = data.get("knowledge", 0)
    fear = data.get("fear", 0)
    noise = data.get("noise", 0)
    time_left = data.get("time_left", 8)
    last_choice = data.get("last_choice", "")
    inventory = data.get("inventory", [])
    save_message = "Игра загружена"


def reset_game():
    global game_state
    global current_node
    global trust
    global knowledge
    global fear
    global noise
    global time_left
    global last_choice
    global inventory
    global save_message

    game_state = "menu"
    current_node = "intro_1"
    trust = 0
    knowledge = 0
    fear = 0
    noise = 0
    time_left = 8
    last_choice = ""
    inventory = []
    save_message = ""


# -----------------------------
# КНОПКИ МЕНЮ
# -----------------------------
start_button = Button(360, 360, 280, 70, "START")
exit_button = Button(360, 450, 280, 70, "EXIT")

# -----------------------------
# ОСНОВНОЙ ЦИКЛ
# -----------------------------
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if start_button.is_clicked(event):
                game_state = "story"

            if exit_button.is_clicked(event):
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                load_game()

        elif game_state == "story":
            node = story[current_node]

            if "choices" in node:
                choices = node["choices"]
                buttons = build_choice_buttons(choices)

                for index, button in enumerate(buttons):
                    if button.is_clicked(event):
                        apply_choice(choices[index])

            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if current_node == "final_check":
                            game_state = "result"
                        else:
                            current_node = node["next"]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game()

                if event.key == pygame.K_l:
                    load_game()

        elif game_state == "result":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

                if event.key == pygame.K_l:
                    load_game()

                if event.key == pygame.K_ESCAPE:
                    running = False

    if game_state == "menu":
        draw_menu()
        mouse_pos = pygame.mouse.get_pos()
        start_button.draw(screen, mouse_pos)
        exit_button.draw(screen, mouse_pos)

    elif game_state == "story":
        draw_background()
        draw_character()
        draw_inventory()
        draw_stats()

        node = story[current_node]
        draw_text_box(node["speaker"], node["text"])
        draw_save_message()

        if "choices" in node:
            draw_choice_buttons(node["choices"])
            hint = small_font.render("S - сохранить, L - загрузить", True, BOX_HINT_COLOR)
            screen.blit(hint, (635, 590))
        else:
            hint = small_font.render("SPACE - дальше, S - сохранить, L - загрузить", True, BOX_HINT_COLOR)
            screen.blit(hint, (515, 590))

    elif game_state == "result":
        draw_result()

    pygame.display.flip()

pygame.quit()
sys.exit()
