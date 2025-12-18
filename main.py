import pygame

pygame.init()

# Окно
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("VN Prototype")

# Шрифт
font = pygame.font.SysFont(None, 32)

# Переменные состояния
scene = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                scene += 1

    screen.fill((255, 255, 255))

    if scene == 0:
        text = "Визуальная Новелла"
    elif scene == 1:
        text = "Базовая структура и логика"
    else:
        text = "Проект в разработке"

    screen.blit(font.render(text, True, (0, 0, 0)), (50, 180))
    pygame.display.flip()

pygame.quit()
