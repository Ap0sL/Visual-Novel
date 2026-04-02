import pygame

pygame.init()

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Визуальная новелла - Базовая структура")

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

# Диалоги
dialogues = [
    ("Рассказчик", "Привет, сюда что то потом добавлю."),
    ("Персонаж", "Это базовая структура."),
    ("Персонаж", "Тяп ляп.")
]

dialogue_index = 0
state = "dialogue"   # dialogue / choice / result
choice = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "dialogue" and event.key == pygame.K_SPACE:
                dialogue_index += 1
                if dialogue_index >= len(dialogues):
                    state = "choice"

            elif state == "choice":
                if event.key == pygame.K_1:
                    choice = "Ты выбрал первый вариант."
                    state = "result"
                elif event.key == pygame.K_2:
                    choice = "Ты выбрал второй вариант."
                    state = "result"

    screen.fill((240, 240, 240))

    # Окно текста
    pygame.draw.rect(screen, (200, 200, 200), (50, 300, 700, 150))

    if state == "dialogue":
        name, text = dialogues[dialogue_index]
        screen.blit(font.render(name, True, (0, 0, 0)), (70, 320))
        screen.blit(small_font.render(text, True, (0, 0, 0)), (70, 370))
        screen.blit(small_font.render("SPACE - дальше", True, (50, 50, 50)), (600, 420))

    elif state == "choice":
        screen.blit(font.render("Сделай выбор:", True, (0, 0, 0)), (70, 320))
        screen.blit(small_font.render("1 - Первый вариант", True, (0, 0, 0)), (70, 370))
        screen.blit(small_font.render("2 - Второй вариант", True, (0, 0, 0)), (70, 400))

    elif state == "result":
        screen.blit(font.render("Результат", True, (0, 0, 0)), (70, 320))
        screen.blit(small_font.render(choice, True, (0, 0, 0)), (70, 370))

    pygame.display.flip()

pygame.quit()