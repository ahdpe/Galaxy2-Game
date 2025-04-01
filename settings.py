# settings.py
import pygame

# --- Экран и FPS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Цвета ---
# Определяем цвета ДО того, как они используются в других константах
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
HIGHLIGHT_COLOR = YELLOW

# --- Размеры объектов ---
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 50
BULLET_WIDTH = 8
BULLET_HEIGHT = 20
ENEMY_BULLET_WIDTH = 6
ENEMY_BULLET_HEIGHT = 12
POWERUP_WIDTH = 30
POWERUP_HEIGHT = 30
ENEMY_BASIC_SIZE = (45, 35)
ENEMY_TANK_SIZE = (55, 45)
ENEMY_SHOOTER_SIZE = (40, 40)
SHIELD_ACTIVE_SIZE = (PLAYER_WIDTH + 10, PLAYER_HEIGHT + 10)

# --- Имена файлов ассетов ---
# Графика
IMG_PLAYER = 'player.png'
IMG_BULLET = 'bullet.png'
IMG_ENEMY_BULLET = 'enemy_bullet.png'
IMG_GAME_BG = 'background.jpg'
IMG_SHIELD_POWERUP = 'shield_powerup.png'
IMG_GUN_POWERUP = 'gun_powerup.png'
IMG_SHIELD_ACTIVE = 'shield_active.png'
IMG_ENEMY_BASIC = 'enemy.png'
IMG_ENEMY_TANK = 'enemy_tank.png'
IMG_ENEMY_SHOOTER = 'enemy_shooter.png'
IMG_INTRO_BG = 'intro_background.png'
IMG_OUTRO_BG = 'outro_background.png'
# Звуки
SND_SHOOT = 'laser.wav'
SND_EXPLOSION = 'explosion.wav'
SND_PLAYER_HIT = 'player_hit.wav'
SND_POWERUP = 'powerup.wav'
SND_ENEMY_HIT = 'enemy_hit.wav'
SND_MENU_CHANGE = 'menu_change.wav'
SND_MENU_SELECT = 'menu_select.wav'
# Музыка
MUS_BACKGROUND = 'music.mp3'           # Музыка во время игры
MUS_INTRO = 'intro_music.mp3'          # Музыка для экрана интро (замените!)
MUS_OUTRO = 'outro_music.mp3'          # Музыка для экрана аутро (замените!)

# --- Статы врагов ---
ENEMY_STATS = {
    'basic': {'health': 1, 'speed_mult': 1.0, 'score': 10, 'img_key': 'basic', 'size': ENEMY_BASIC_SIZE, 'color': GREEN, 'shoot_freq_mod': 1.0},
    'tank': {'health': 3, 'speed_mult': 0.7, 'score': 30, 'img_key': 'tank', 'size': ENEMY_TANK_SIZE, 'color': PURPLE, 'shoot_freq_mod': 1.5},
    'shooter': {'health': 1, 'speed_mult': 0.9, 'score': 25, 'img_key': 'shooter', 'size': ENEMY_SHOOTER_SIZE, 'color': ORANGE, 'shoot_freq_mod': 0.6},
} # 'img_key' для связи со словарем загруженных изображений в assets.py

# --- Настройки игры ---
PLAYER_START_X = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
PLAYER_START_Y = SCREEN_HEIGHT - PLAYER_HEIGHT - 20
PLAYER_SPEED = 6
PLAYER_LIVES_START = 3
SHIELD_DURATION = 5000      # в миллисекундах
RAPID_FIRE_DURATION = 8000  # в миллисекундах
BASE_SHOOT_DELAY = 400      # в миллисекундах
RAPID_FIRE_SHOOT_DELAY = 150 # в миллисекундах
BULLET_SPEED = 8
ENEMY_BULLET_SPEED = 5

# --- Настройки врагов (спавн, движение) ---
ENEMY_SPAWN_Y_START = 50
ENEMY_X_GAP = 70
ENEMY_Y_GAP = 50
BASE_ENEMY_SPEED = 1.5
BASE_ENEMY_SHOOT_DELAY = 1800 # в миллисекундах
LEVEL1_BASIC_COUNT = 4
LEVEL5_MAX_ROWS = 6
LEVEL5_MAX_COLS = 10
LEVEL5_MAX_ENEMIES = LEVEL5_MAX_ROWS * LEVEL5_MAX_COLS

# --- Настройки бонусов ---
POWERUP_SPAWN_CHANCE = 0.12 # 12% шанс спавна бонуса при уничтожении врага
POWERUP_SPEED = 3
POWERUP_TYPES = ['shield', 'gun']

# --- Настройки сложности ---
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
DIFFICULTY_SETTINGS = {
    "easy":   {"speed_mult": 0.75, "shoot_delay_mult": 1.3, "score_mult": 0.8},
    "medium": {"speed_mult": 1.0,  "shoot_delay_mult": 1.0, "score_mult": 1.0},
    "hard":   {"speed_mult": 1.25, "shoot_delay_mult": 0.75, "score_mult": 1.2}
}

# --- UI ---
LEVEL_DISPLAY_DURATION = 2000 # в миллисекундах
COPYRIGHT_TEXT = "Made by Andrei Osipov"

# --- Шрифты (Инициализация перенесена в main.py, т.к. требует pygame.font.init()) ---
# FONT_SIZE_NORMAL = 36
# FONT_SIZE_SMALL = 24
# FONT_SIZE_COPYRIGHT = 18
# FONT_SIZE_LARGE = 60
# FONT_SIZE_XLARGE = 74

# --- Другие глобальные настройки ---
difficulty_levels = DIFFICULTY_LEVELS # Для удобства доступа из main.py
NUM_STARS = 80  # Количество звезд на фоне во время игры

# --- Настройки эффектов ---
# Этот блок должен идти ПОСЛЕ определения цветов
SPARK_DURATION = 120          # мс, короткая вспышка
SPARK_RADIUS_MIN = 2
SPARK_RADIUS_MAX = 5
SPARK_COUNT = 5               # Кол-во искр за раз
EXPLOSION_DURATION = 350      # мс, подольше
EXPLOSION_RADIUS_START = 5
EXPLOSION_RADIUS_END = 30
EXPLOSION_COLOR_START = YELLOW # Использует YELLOW, определенный выше
EXPLOSION_COLOR_END = RED     # Использует RED, определенный выше