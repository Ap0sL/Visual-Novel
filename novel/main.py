
import pygame
import sys
from pathlib import Path

pygame.init()

#ОКНА
WIDTH = 1000
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Novel Prototype")
clock = pygame.time.Clock()

# ПУТЬ К ФАЙЛАМ
BASE_DIR = Path(__file__).resolve().parent
CHARACTER_PATH = BASE_DIR / "assets" / "characters" / "visitor.png"
BACKGROUND_PATH = BASE_DIR / "assets" / "backgrounds" / "school.png"

# ЦВЕТА
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DARK = (18, 18, 18)
SOFT_DARK = (35, 35, 35)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
BLUE = (120, 170, 255)
LIGHT_BLUE = (210, 230, 255)
RED = (220, 100, 100)
MENU_TITLE_COLOR = (255, 255, 255)
MENU_TEXT_COLOR = (235, 235, 235)
MENU_HINT_COLOR = (210, 210, 210)
SHADOW_COLOR = (0, 0, 0)
STAT_COLOR = (255, 255, 255)
BOX_TEXT_COLOR = (240, 240, 240)
BOX_NAME_COLOR = (255, 255, 255)
BOX_HINT_COLOR = (200, 200, 200)

# ШРИФТЫ
title_font = pygame.font.SysFont("arial", 48, bold=True)
name_font = pygame.font.SysFont("arial", 32, bold=True)
text_font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 22)

# ТУТ Я ЗАГРУЖАЮ ИЗОБРАЖЕНИЯ
character_img = pygame.image.load(str(CHARACTER_PATH)).convert_alpha()
character_img = pygame.transform.smoothscale(character_img, (220, 420))

background_img = pygame.image.load(str(BACKGROUND_PATH)).convert()
background_img = pygame.transform.smoothscale(background_img, (WIDTH, HEIGHT))

# ОСНОВА(данные) ИГРЫ
game_state = "menu"
current_node = "intro_1"

trust = 0
knowledge = 0
last_choice = ""

#сценарий
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
                "knowledge": 0
            },
            {
                "text": "Осмотреть коридор вокруг",
                "next": "system_path",
                "trust": 0,
                "knowledge": 1
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
                "knowledge": 0
            },
            {
                "text": "Молча проверить дверь",
                "next": "score_path",
                "trust": 0,
                "knowledge": 1
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
                "next": "design_path",
                "trust": 1,
                "knowledge": 0
            },
            {
                "text": "Спрятаться и дождаться тишины",
                "next": "code_path",
                "trust": 0,
                "knowledge": 1
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
    "final_check": {
        "speaker": "Рассказчик",
        "text": "Шаги уже совсем рядом. Сейчас все решится.",
        "next": "ending"
    }
}

#КНОПКИ
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface, mouse_pos):
        color = LIGHT_BLUE if self.rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)

        label = text_font.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

#ФУНКЦИИ РИСОВАНИЯ
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


def draw_stats():
    trust_text = small_font.render(f"Смелость: {trust}", True, STAT_COLOR)
    knowledge_text = small_font.render(f"Внимательность: {knowledge}", True, STAT_COLOR)

    screen.blit(trust_text, (730, 15))
    screen.blit(knowledge_text, (730, 40))


def draw_menu():
    draw_background()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    title = title_font.render("Школьный Коридор", True, MENU_TITLE_COLOR)
    subtitle = text_font.render("Мини-хоррор новелла", True, MENU_TEXT_COLOR)

    info_1 = small_font.render("Сделай выбор и попробуй выбраться из темной школы.", True, MENU_TEXT_COLOR)
    info_2 = small_font.render("Нажми START, чтобы начать.", True, MENU_HINT_COLOR)

    title_shadow = title_font.render("Школьный Коридор", True, SHADOW_COLOR)
    subtitle_shadow = text_font.render("Мини-хоррор новелла", True, SHADOW_COLOR)

    screen.blit(title_shadow, (273, 133))
    screen.blit(subtitle_shadow, (333, 198))

    screen.blit(title, (270, 130))
    screen.blit(subtitle, (330, 195))
    screen.blit(info_1, (220, 260))
    screen.blit(info_2, (350, 290))


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

    screen.blit(stats_1, (180, 410))
    screen.blit(stats_2, (180, 450))

    if last_choice != "":
        choice_surface = small_font.render(f"Последний выбор: {last_choice}", True, MENU_HINT_COLOR)
        screen.blit(choice_surface, (180, 500))

    restart_surface = small_font.render("Нажми R для перезапуска или ESC для выхода", True, LIGHT_GRAY)
    screen.blit(restart_surface, (180, 560))


def get_ending():
    total = trust + knowledge

    if trust >= 2 and knowledge >= 2:
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


def draw_choice_buttons(choices):
    buttons = []
    mouse_pos = pygame.mouse.get_pos()

    y = 330
    for choice in choices:
        button = Button(520, y, 360, 55, choice["text"])
        button.draw(screen, mouse_pos)
        buttons.append(button)
        y += 75

    return buttons


def reset_game():
    global game_state
    global current_node
    global trust
    global knowledge
    global last_choice

    game_state = "menu"
    current_node = "intro_1"
    trust = 0
    knowledge = 0
    last_choice = ""

# кнопки в меню
start_button = Button(360, 360, 280, 70, "START")
exit_button = Button(360, 450, 280, 70, "EXIT")

# ОСНОВНОЙ ЦИКЛ ИГРЫ
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

        elif game_state == "story":
            node = story[current_node]

            if "choices" in node:
                choices = node["choices"]

                button_1 = Button(520, 330, 360, 55, choices[0]["text"])
                button_2 = Button(520, 405, 360, 55, choices[1]["text"])

                if button_1.is_clicked(event):
                    trust += choices[0]["trust"]
                    knowledge += choices[0]["knowledge"]
                    last_choice = choices[0]["text"]
                    current_node = choices[0]["next"]

                if button_2.is_clicked(event):
                    trust += choices[1]["trust"]
                    knowledge += choices[1]["knowledge"]
                    last_choice = choices[1]["text"]
                    current_node = choices[1]["next"]

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if current_node == "final_check":
                        game_state = "result"
                    else:
                        current_node = node["next"]

        elif game_state == "result":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

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
        draw_stats()

        node = story[current_node]
        draw_text_box(node["speaker"], node["text"])

        if "choices" in node:
            draw_choice_buttons(node["choices"])
        else:
            hint = small_font.render("Нажми SPACE, чтобы продолжить", True, BOX_HINT_COLOR)
            screen.blit(hint, (600, 590))

    elif game_state == "result":
        draw_result()

    pygame.display.flip()

pygame.quit()
sys.exit()
