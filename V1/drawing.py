# drawing.py
import pygame
from settings import WHITE # Нужны только цвета и, возможно, размеры

# Шрифты передаются как аргументы, т.к. инициализируются в main.py
def draw_text(text, font_obj, color, surface, x, y, center=False):
    """Универсальная функция отрисовки текста."""
    if not font_obj:
        print("Ошибка: Шрифт не передан в draw_text")
        return
    try:
        textobj = font_obj.render(text, True, color)
        textrect = textobj.get_rect()
        if center:
            textrect.center = (x, y)
        else:
            textrect.topleft = (x, y)
        surface.blit(textobj, textrect)
    except Exception as e:
        print(f"Ошибка при отрисовке текста '{text}': {e}")

def draw_lives(surface, x, y, lives, life_img, font_normal):
    """Рисует иконки жизней или текст."""
    life_icon_width = 30
    life_icon_height = 25
    icon_spacing = 10

    if life_img:
        try:
            # Масштабируем каждый раз или один раз при загрузке? Пока каждый раз.
            img_scaled = pygame.transform.scale(life_img, (life_icon_width, life_icon_height))
            for i in range(lives):
                surface.blit(img_scaled, (x + (life_icon_width + icon_spacing) * i, y))
        except Exception as e:
            print(f"Ошибка отрисовки иконки жизней: {e}")
            # Резервный вариант текстом
            draw_text(f"Жизни: {lives}", font_normal, WHITE, surface, x, y)
    else:
        # Если картинки нет изначально
        draw_text(f"Жизни: {lives}", font_normal, WHITE, surface, x, y)

# Можно добавить другие функции отрисовки (UI, экранов меню/game over и т.д.)