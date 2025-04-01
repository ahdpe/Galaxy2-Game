from PIL import Image, ImageDraw
import random
import os

# Размеры из игрового кода (убедись, что они совпадают!)
player_width = 60
player_height = 50
enemy_width = 45
enemy_height = 35
bullet_width = 8
bullet_height = 20
enemy_bullet_width = 6
enemy_bullet_height = 12
powerup_width = 30
powerup_height = 30
shield_active_width = player_width + 10
shield_active_height = player_height + 10
screen_width = 800
screen_height = 600

# --- Создание папки для ассетов (если не существует) ---
# Поместит все в подпапку 'assets', можешь изменить или убрать,
# если хочешь файлы прямо рядом со скриптом.
# asset_dir = "assets"
# if not os.path.exists(asset_dir):
#     os.makedirs(asset_dir)
# path = lambda filename: os.path.join(asset_dir, filename)

# Или просто сохранять в текущую директорию:
path = lambda filename: filename


print("Создание placeholder изображений...")

# --- 1. player.png ---
img = Image.new('RGBA', (player_width, player_height), (0, 0, 0, 0)) # Прозрачный фон
draw = ImageDraw.Draw(img)
# Простой треугольный корабль
points = [
    (player_width // 2, 5),              # Вершина
    (5, player_height - 5),             # Левый нижний угол
    (player_width - 5, player_height - 5) # Правый нижний угол
]
draw.polygon(points, fill='lightblue', outline='white')
# Небольшой "кабина"
draw.rectangle(
    (player_width // 2 - 4, player_height // 2, player_width // 2 + 4, player_height // 2 + 8),
    fill='white'
)
img.save(path('player.png'))
print(f"Создано: {path('player.png')}")

# --- 2. enemy.png ---
img = Image.new('RGBA', (enemy_width, enemy_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Простой прямоугольный враг с "рогами"
draw.rectangle( (5, 10, enemy_width - 5, enemy_height - 5), fill='lightgreen', outline='darkgreen')
draw.rectangle( (10, 5, 15, 15), fill='lightgreen', outline='darkgreen') # Левый рог
draw.rectangle( (enemy_width - 15, 5, enemy_width - 10, 15), fill='lightgreen', outline='darkgreen') # Правый рог
draw.rectangle( (enemy_width // 2 - 3, 0, enemy_width // 2 + 3, 10), fill='red') # "Глаз"
img.save(path('enemy.png'))
print(f"Создано: {path('enemy.png')}")

# --- 3. bullet.png ---
img = Image.new('RGBA', (bullet_width, bullet_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle( (0, 0, bullet_width -1 , bullet_height - 1), fill='red', outline='orange')
img.save(path('bullet.png'))
print(f"Создано: {path('bullet.png')}")

# --- 4. enemy_bullet.png ---
img = Image.new('RGBA', (enemy_bullet_width, enemy_bullet_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle( (0, 0, enemy_bullet_width - 1, enemy_bullet_height - 1), fill='yellow', outline='orange')
img.save(path('enemy_bullet.png'))
print(f"Создано: {path('enemy_bullet.png')}")

# --- 5. background.jpg ---
img = Image.new('RGB', (screen_width, screen_height), (0, 0, 20)) # Темно-синий фон
draw = ImageDraw.Draw(img)
# Добавим звезды
num_stars = 200
for _ in range(num_stars):
    x = random.randint(0, screen_width - 1)
    y = random.randint(0, screen_height - 1)
    size = random.randint(1, 3)
    brightness = random.randint(150, 255)
    color = (brightness, brightness, brightness)
    if size == 1:
        draw.point((x, y), fill=color)
    else:
        draw.ellipse((x, y, x + size - 1, y + size - 1), fill=color)
img.save(path('background.jpg'))
print(f"Создано: {path('background.jpg')}")

# --- 6. shield_powerup.png ---
img = Image.new('RGBA', (powerup_width, powerup_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Синий круг
draw.ellipse( (2, 2, powerup_width - 3, powerup_height - 3), fill='blue', outline='lightblue', width=2)
# Можно добавить букву 'S'
# draw.text((powerup_width//2 - 5, powerup_height//2 - 8), "S", fill="white")
img.save(path('shield_powerup.png'))
print(f"Создано: {path('shield_powerup.png')}")

# --- 7. gun_powerup.png ---
img = Image.new('RGBA', (powerup_width, powerup_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Красный квадрат с молнией или стрелкой вверх
draw.rectangle( (2, 2, powerup_width - 3, powerup_height - 3), fill='red', outline='darkred')
# Простая стрелка вверх
points = [
    (powerup_width // 2, 5),
    (powerup_width // 2 + 5, 15),
    (powerup_width // 2 - 5, 15),
]
draw.polygon(points, fill='yellow')
draw.rectangle( (powerup_width // 2 - 2, 15, powerup_width // 2 + 2, powerup_height - 5), fill='yellow')
img.save(path('gun_powerup.png'))
print(f"Создано: {path('gun_powerup.png')}")

# --- 8. shield_active.png ---
img = Image.new('RGBA', (shield_active_width, shield_active_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Полупрозрачный синий круг/эллипс
# Цвет с альфа-каналом (RGBA): R, G, B, Alpha (0=прозрачный, 255=непрозрачный)
shield_color = (100, 150, 255, 128) # Голубоватый, полупрозрачный
outline_color = (150, 200, 255, 180) # Светлее, чуть менее прозрачный
draw.ellipse( (2, 2, shield_active_width - 3, shield_active_height - 3), fill=shield_color, outline=outline_color, width=3)
img.save(path('shield_active.png'))
print(f"Создано: {path('shield_active.png')}")

print("Все изображения созданы.")