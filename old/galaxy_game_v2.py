import pygame
import random
import sys
import os

# --- Инициализация Pygame и Микшера ---
pygame.init()
try:
    pygame.mixer.init() # Инициализация звука
    sound_enabled = True
except pygame.error as e:
    print(f"Не удалось инициализировать микшер звука: {e}. Звук будет отключен.")
    sound_enabled = False

# --- Настройки экрана ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Улучшенная Галактика (Волны Врагов - от Andrei Osipov)")

# --- Цвета ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150) # Для копирайта
ORANGE = (255, 165, 0) # Для врага-стрелка
PURPLE = (128, 0, 128) # Для врага-танка

# --- Настройки Космического Фона (Звезды) ---
NUM_STARS = 150
stars = []
for _ in range(NUM_STARS):
    x = random.randrange(0, screen_width)
    y = random.randrange(0, screen_height)
    speed = random.choice([1, 2, 3])
    size = speed
    brightness = 100 + 50 * speed
    color = (brightness, brightness, brightness)
    stars.append([x, y, speed, size, color])

# --- Загрузка Ассетов (Графика и Звуки) ---
def load_image(filename, size=None, use_colorkey=False, colorkey_color=BLACK):
    """Функция для безопасной загрузки изображений с поддержкой colorkey."""
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
             filepath = filename
             if not os.path.exists(filepath):
                 raise pygame.error(f"Файл не найден: {filename}")

        try:
            image = pygame.image.load(filepath)
        except pygame.error as load_error:
            print(f"Ошибка Pygame при загрузке {filename}: {load_error}")
            return None # Не удалось даже загрузить

        # Обработка прозрачности
        if image.get_alpha() is None and not use_colorkey:
             image = image.convert() # Для оптимизации, если нет альфа-канала и colorkey не нужен
        elif use_colorkey:
             image = image.convert()
             image.set_colorkey(colorkey_color)
        else:
             image = image.convert_alpha() # Если есть альфа-канал

        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as e:
        print(f"Не удалось загрузить или обработать изображение: {filename}. Ошибка: {e}")
        return None

def load_sound(filename):
    if not sound_enabled:
        return None
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
             filepath = filename
             if not os.path.exists(filepath):
                  raise pygame.error(f"Файл не найден: {filename}")

        sound = pygame.mixer.Sound(filepath)
        return sound
    except pygame.error as e:
        print(f"Не удалось загрузить звук: {filename}. Ошибка: {e}")
        return None

# --- Размеры и Загрузка Изображений ---
player_width = 60
player_height = 50
bullet_width = 8
bullet_height = 20
enemy_bullet_width = 6
enemy_bullet_height = 12
powerup_width = 30
powerup_height = 30

player_img = load_image('player.png', (player_width, player_height))
bullet_img = load_image('bullet.png', (bullet_width, bullet_height))
enemy_bullet_img = load_image('enemy_bullet.png', (enemy_bullet_width, enemy_bullet_height))
background_img = load_image('background.jpg', (screen_width, screen_height))
powerup_shield_img = load_image('shield_powerup.png', (powerup_width, powerup_height))
powerup_gun_img = load_image('gun_powerup.png', (powerup_width, powerup_height))
shield_active_img = load_image('shield_active.png', (player_width + 10, player_height + 10))

# --- Новые типы врагов: Размеры и Изображения ---
enemy_basic_size = (45, 35)
enemy_tank_size = (55, 45)
enemy_shooter_size = (40, 40)

# Загружаем изображения для каждого типа врага
# !!!ВАЖНО: Убедитесь, что у вас есть файлы enemy_basic.png, enemy_tank.png, enemy_shooter.png
# или замените имена файлов на свои, или оставьте None для отрисовки прямоугольников.
enemy_img_basic = load_image('enemy.png', enemy_basic_size) # Используем старое имя для базового
enemy_img_tank = load_image('enemy_tank.png', enemy_tank_size)
enemy_img_shooter = load_image('enemy_shooter.png', enemy_shooter_size)

# --- Данные о типах врагов ---
ENEMY_STATS = {
    'basic': {
        'health': 1,
        'speed_mult': 1.0, # Множитель базовой скорости врагов
        'score': 10,
        'img': enemy_img_basic,
        'size': enemy_basic_size,
        'color': GREEN, # Резервный цвет
        'shoot_freq_mod': 1.0 # Модификатор частоты стрельбы (1.0 = стандарт)
    },
    'tank': {
        'health': 3,
        'speed_mult': 0.7,
        'score': 30,
        'img': enemy_img_tank,
        'size': enemy_tank_size,
        'color': PURPLE,
        'shoot_freq_mod': 1.5 # Стреляет реже базового
    },
    'shooter': {
        'health': 1, # Хрупкий, но опасный
        'speed_mult': 0.9,
        'score': 25,
        'img': enemy_img_shooter,
        'size': enemy_shooter_size,
        'color': ORANGE,
        'shoot_freq_mod': 0.6 # Стреляет чаще базового
    },
    # Добавьте сюда другие типы врагов по аналогии
}

# --- Загрузка Звуков ---
shoot_sound = load_sound('laser.wav')
explosion_sound = load_sound('explosion.wav')
player_hit_sound = load_sound('player_hit.wav')
powerup_sound = load_sound('powerup.wav')
enemy_hit_sound = load_sound('enemy_hit.wav') # Звук попадания по врагу (не смертельного)

# --- Фоновая музыка ---
if sound_enabled:
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        music_filepath = os.path.join(base_path, 'music.mp3')
        if not os.path.exists(music_filepath): music_filepath = 'music.mp3'
        if not os.path.exists(music_filepath): raise pygame.error("Файл music.mp3 не найден")
        pygame.mixer.music.load(music_filepath)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Не удалось загрузить или воспроизвести фоновую музыку: {e}")

# --- Настройки Игрока ---
player_start_x = (screen_width - player_width) // 2
player_start_y = screen_height - player_height - 20
player_speed = 6
player_rect = pygame.Rect(player_start_x, player_start_y, player_width, player_height)
player_lives_start = 3
player_lives = player_lives_start
player_shield_active = False
player_shield_timer = 0
shield_duration = 5000
rapid_fire_active = False
rapid_fire_timer = 0
rapid_fire_duration = 8000
base_shoot_delay = 400
rapid_fire_shoot_delay = 150
current_shoot_delay = base_shoot_delay

# --- Класс Врага ---
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.width, self.height = stats['size']
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.max_health = stats['health']
        self.health = self.max_health
        self.speed_mult = stats['speed_mult']
        self.score_value = stats['score']
        self.image = stats['img']
        self.color = stats['color'] # Резервный цвет
        self.shoot_mod = stats['shoot_freq_mod']

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0: self.health = 0
        # Можно добавить визуальный эффект попадания здесь

    def draw(self, surface):
        img_to_draw = self.image
        # Опционально: показать повреждения танка
        if self.type == 'tank' and self.health < self.max_health:
             # Простой вариант: слегка затемнить или изменить цвет
             # Более сложный: наложить изображение трещин
             # Пока просто рисуем как есть или резервным цветом
             pass # Оставляем стандартное изображение/цвет

        if img_to_draw:
            surface.blit(img_to_draw, self.rect)
        else:
            # Рисуем прямоугольник с цветом, зависящим от здоровья (простой индикатор)
            health_ratio = self.health / self.max_health
            # Интерполяция цвета от полного (self.color) до красного
            r = int(self.color[0] * health_ratio + RED[0] * (1 - health_ratio))
            g = int(self.color[1] * health_ratio + RED[1] * (1 - health_ratio))
            b = int(self.color[2] * health_ratio + RED[2] * (1 - health_ratio))
            current_color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.rect(surface, current_color, self.rect)

    def is_alive(self):
        return self.health > 0

# --- Настройки Врагов ---
enemies = [] # Список для хранения объектов Enemy
enemy_spawn_rows_base = 3 # Базовое кол-во рядов
enemy_spawn_cols_base = 6 # Базовое кол-во колонок
enemy_spawn_x_start = 50
enemy_spawn_y_start = 50
enemy_x_gap = 70
enemy_y_gap = 50

base_enemy_speed = 1.5 # Глобальная базовая скорость
base_enemy_shoot_delay = 1800 # Базовая задержка выстрела (глобальная)
enemy_speed = base_enemy_speed # Текущая глобальная скорость (модификатор для всех)
enemy_shoot_delay = base_enemy_shoot_delay # Текущая глоб. задержка
enemy_direction = 1
move_down_flag = False

# --- Настройки Пуль ---
bullets = []
enemy_bullets = []
bullet_speed = 8
enemy_bullet_speed = 5
can_shoot = True
shoot_timer = 0

# --- Настройки Бонусов ---
powerups = []
powerup_spawn_chance = 0.12 # Немного уменьшим шанс из-за более крепких врагов
powerup_speed = 3
powerup_types = ['shield', 'gun']

# --- Уровни, Счет и Шрифты ---
score = 0
level = 1
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
copyright_font = pygame.font.Font(None, 18)
copyright_text = "Made by Andrei Osipov"
copyright_color = GREY
level_start_display_time = 0 # Время показа "Уровень N"
level_display_duration = 2000 # 2 секунды

# --- Функции ---
def get_wave_composition(current_level):
    """Определяет типы и количество врагов для уровня."""
    composition = {}
    total_enemies = 0

    rows = min(enemy_spawn_rows_base + (current_level // 2), 6)
    cols = min(enemy_spawn_cols_base + (current_level // 3), 10)
    max_possible_enemies = rows * cols

    # Определяем доступные типы врагов и их пропорции
    if current_level < 3:
        # Только базовые
        composition['basic'] = max_possible_enemies
    elif current_level < 6:
        # Базовые и стрелки
        num_shooters = max_possible_enemies // 4
        composition['shooter'] = num_shooters
        composition['basic'] = max_possible_enemies - num_shooters
    elif current_level < 10:
        # Базовые, стрелки и танки
        num_tanks = max_possible_enemies // 5
        num_shooters = max_possible_enemies // 4
        composition['tank'] = num_tanks
        composition['shooter'] = num_shooters
        composition['basic'] = max_possible_enemies - num_tanks - num_shooters
    else:
        # Больше танков и стрелков
        num_tanks = max_possible_enemies // 4
        num_shooters = max_possible_enemies // 3
        composition['tank'] = num_tanks
        composition['shooter'] = num_shooters
        composition['basic'] = max(0, max_possible_enemies - num_tanks - num_shooters) # Гарантируем не отрицательное

    # Ограничим общее количество, чтобы не было слишком много сразу
    total_enemies = sum(composition.values())
    # print(f"Level {current_level}: Spawning {total_enemies} enemies. Comp: {composition}") # Отладка

    return composition, rows, cols


def spawn_enemies(current_level):
    """Создает волну врагов в зависимости от уровня."""
    enemies.clear()
    composition, rows, cols = get_wave_composition(current_level)

    # Преобразуем словарь количества в список типов для случайного выбора
    enemy_pool = []
    for type, count in composition.items():
        enemy_pool.extend([type] * count)
    random.shuffle(enemy_pool) # Перемешиваем, чтобы типы были распределены случайно

    grid_width = (cols - 1) * enemy_x_gap + enemy_basic_size[0] # Ширина по базовому размеру для расчета старта
    current_spawn_x_start = max(10, (screen_width - grid_width) // 2)

    enemy_index = 0
    for row in range(rows):
        for col in range(cols):
            if enemy_index < len(enemy_pool):
                enemy_type = enemy_pool[enemy_index]
                enemy_stats = ENEMY_STATS[enemy_type]
                # Центрируем врага в его ячейке сетки
                cell_center_x = current_spawn_x_start + col * enemy_x_gap + enemy_basic_size[0] // 2
                enemy_x = cell_center_x - enemy_stats['size'][0] // 2
                enemy_y = enemy_spawn_y_start + row * enemy_y_gap
                enemies.append(Enemy(enemy_x, enemy_y, enemy_type))
                enemy_index += 1
            else:
                break # Если врагов в пуле меньше, чем ячеек

def spawn_powerup(x, y):
    if len(powerups) < 3: # Позволим чуть больше бонусов
        powerup_type = random.choice(powerup_types)
        powerup_rect = pygame.Rect(x - powerup_width // 2, y, powerup_width, powerup_height)
        powerups.append([powerup_rect, powerup_type])

def draw_text(text, font_obj, color, surface, x, y, center=False):
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

def draw_lives(surface, x, y, lives, img):
    if img:
        try:
            img_scaled = pygame.transform.scale(img, (30, 25))
            for i in range(lives):
                img_rect = img_scaled.get_rect(topleft=(x + 40 * i, y))
                surface.blit(img_scaled, img_rect)
        except Exception as e:
             print(f"Ошибка масштабирования иконки жизней: {e}")
             draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y)
    else:
        draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y)

def update_difficulty(current_level):
    """Обновляет глобальные параметры сложности."""
    global enemy_speed, enemy_shoot_delay
    # Скорость увеличивается, но медленнее, т.к. есть типы врагов
    enemy_speed = min(base_enemy_speed + (current_level - 1) * 0.15, 4.0)
    # Задержка выстрела уменьшается, но тоже медленнее
    enemy_shoot_delay = max(base_enemy_shoot_delay - (current_level - 1) * 60, 500)

# --- Переменные состояния игры ---
running = True
game_over = False
paused = False
clock = pygame.time.Clock()
FPS = 60
last_enemy_shot_time = pygame.time.get_ticks()

# --- Сброс игры (Функция) ---
def reset_game():
    global player_rect, player_lives, level, score, enemy_direction, game_over, paused
    global last_enemy_shot_time, current_shoot_delay, player_shield_active, rapid_fire_active
    global level_start_display_time

    player_rect.topleft = (player_start_x, player_start_y)
    player_lives = player_lives_start
    level = 1
    score = 0
    update_difficulty(level)
    spawn_enemies(level)
    bullets.clear()
    enemy_bullets.clear()
    powerups.clear()
    enemy_direction = 1
    player_shield_active = False
    rapid_fire_active = False
    current_shoot_delay = base_shoot_delay
    game_over = False
    paused = False
    can_shoot = True
    last_enemy_shot_time = pygame.time.get_ticks() + 1000 # Небольшая задержка перед первым выстрелом врагов
    level_start_display_time = pygame.time.get_ticks() # Показать "Уровень 1"

    if sound_enabled:
        try:
           pygame.mixer.music.rewind()
           pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Ошибка при перезапуске музыки: {e}")

# --- Первоначальная настройка ---
reset_game() # Используем функцию для инициализации и перезапуска

# --- Игровой цикл ---
while running:
    current_time = pygame.time.get_ticks()

    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: # Пауза на P
                paused = not paused
                if sound_enabled:
                    if paused: pygame.mixer.music.pause()
                    else: pygame.mixer.music.unpause()
            # Клавиши управления работают только если не пауза
            if not paused:
                if game_over and event.key == pygame.K_r: # Перезапуск по R
                    reset_game()
                elif not game_over and event.key == pygame.K_SPACE and can_shoot:
                    bullet_x = player_rect.centerx - bullet_width // 2
                    bullet_y = player_rect.top
                    bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))
                    if shoot_sound:
                        try: shoot_sound.play()
                        except Exception as e: print(f"Ошибка воспроизведения звука выстрела: {e}")
                    can_shoot = False
                    shoot_timer = current_time

    # --- Логика Паузы ---
    if paused:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        draw_text("ПАУЗА", pygame.font.Font(None, 74), YELLOW, screen, screen_width // 2, screen_height // 2 - 50, center=True)
        draw_text("Нажмите P чтобы продолжить", font, WHITE, screen, screen_width // 2, screen_height // 2 + 20, center=True)
        copyright_surface = copyright_font.render(copyright_text, True, copyright_color)
        copyright_rect = copyright_surface.get_rect(bottomright=(screen_width - 10, screen_height - 5))
        screen.blit(copyright_surface, copyright_rect)
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- Основная игровая логика (если не Game Over и не Пауза) ---
    if not game_over:
        # --- Обновление Космического Фона ---
        for star in stars:
            star[1] += star[2]
            if star[1] > screen_height:
                star[1] = random.randrange(-20, 0)
                star[0] = random.randrange(0, screen_width)

        # --- Управление игроком ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < screen_width:
            player_rect.x += player_speed

        # --- Логика Бонусов ---
        if player_shield_active and current_time - player_shield_timer > shield_duration:
            player_shield_active = False
        if rapid_fire_active and current_time - rapid_fire_timer > rapid_fire_duration:
            rapid_fire_active = False
            current_shoot_delay = base_shoot_delay

        # --- Перезарядка выстрела ---
        if not can_shoot and current_time - shoot_timer > current_shoot_delay:
            can_shoot = True

        # --- Движение пуль игрока ---
        bullets = [b for b in bullets if b.bottom > 0]
        for bullet in bullets:
            bullet.y -= bullet_speed

        # --- Движение пуль врагов ---
        enemy_bullets = [b for b in enemy_bullets if b.top < screen_height]
        for bullet in enemy_bullets:
            bullet.y += enemy_bullet_speed

        # --- Движение врагов ---
        move_down_flag = False
        current_enemy_speed = 0 # Определим реальную скорость для этого кадра

        if enemies:
            min_x = min(e.rect.left for e in enemies)
            max_x = max(e.rect.right for e in enemies)
            # Используем enemy_speed (глобальный модификатор) и speed_mult конкретного врага
            # Для проверки границ возьмем средний speed_mult или просто глобальный enemy_speed
            step = enemy_speed * enemy_direction

            if (max_x + step > screen_width) or (min_x + step < 0):
                move_down_flag = True
            else:
                current_enemy_speed = step # Сохраняем боковое смещение

            # Двигаем всех врагов
            for enemy in enemies:
                 # Каждый тип движется со своей скоростью (глоб * множитель типа)
                 effective_speed = enemy_speed * enemy.speed_mult
                 if move_down_flag:
                     enemy.rect.y += enemy_y_gap // 2 # Двигаем вниз на пол-ячейки
                 else:
                     enemy.rect.x += effective_speed * enemy_direction

            if move_down_flag:
                enemy_direction *= -1
                # Коррекция после смены направления
                for enemy in enemies:
                      correction = enemy_speed * enemy.speed_mult * enemy_direction
                      enemy.rect.x += correction

        # --- Стрельба Врагов ---
        # Используем глобальную задержку, но учитываем модификатор частоты врага
        # Проверяем, прошло ли достаточно времени с последнего выстрела (по базовой задержке)
        if enemies and current_time - last_enemy_shot_time > enemy_shoot_delay:
             potential_shooters = []
             # Находим нижних врагов в каждой колонке
             enemy_cols_x = sorted(list({e.rect.x for e in enemies})) # Может быть неточно из-за разной скорости/ширины
             # Лучше группировать по близости X
             cols_grouped = {}
             for enemy in enemies:
                 found_col = False
                 for x_key in cols_grouped:
                     # Если враг достаточно близок к существующей колонке
                     if abs(enemy.rect.centerx - x_key) < enemy_x_gap / 2:
                         cols_grouped[x_key].append(enemy)
                         found_col = True
                         break
                 if not found_col:
                     cols_grouped[enemy.rect.centerx] = [enemy]

             # Выбираем нижнего врага из каждой колонки
             for x_col, col_enemies_list in cols_grouped.items():
                  if col_enemies_list:
                      bottom_enemy = max(col_enemies_list, key=lambda e: e.rect.bottom)
                      potential_shooters.append(bottom_enemy)

             if potential_shooters:
                 # Выбираем случайного стрелка, НО даем приоритет "Shooter" типу
                 shooters = [e for e in potential_shooters if e.type == 'shooter']
                 non_shooters = [e for e in potential_shooters if e.type != 'shooter']

                 chosen_shooter = None
                 if shooters and random.random() < 0.6: # 60% шанс что выстрелит шутер, если он есть
                      chosen_shooter = random.choice(shooters)
                 elif non_shooters:
                      chosen_shooter = random.choice(non_shooters)
                 elif shooters: # Если есть только шутеры
                      chosen_shooter = random.choice(shooters)

                 if chosen_shooter:
                    # Проверяем индивидуальную готовность врага к выстрелу (на основе его модификатора)
                    # Это не таймер, а просто шанс, основанный на модификаторе
                    time_since_last_shot = current_time - last_enemy_shot_time
                    required_delay_for_this_enemy = enemy_shoot_delay * chosen_shooter.shoot_mod

                    # Небольшая случайность, чтобы не все стреляли синхронно после паузы
                    random_delay_mod = random.uniform(0.8, 1.2)

                    if time_since_last_shot > required_delay_for_this_enemy * random_delay_mod :
                        bullet_x = chosen_shooter.rect.centerx - enemy_bullet_width // 2
                        bullet_y = chosen_shooter.rect.bottom
                        enemy_bullets.append(pygame.Rect(bullet_x, bullet_y, enemy_bullet_width, enemy_bullet_height))
                        last_enemy_shot_time = current_time # Сбрасываем ГЛОБАЛЬНЫЙ таймер


        # --- Движение бонусов ---
        powerups = [p for p in powerups if p[0].top < screen_height]
        for powerup in powerups:
            powerup[0].y += powerup_speed

        # --- Проверка столкновений ---
        # Пули игрока с врагами
        bullets_hit_indices = set()
        enemies_damaged_indices = set() # Индексы врагов, получивших урон

        for i, bullet in enumerate(bullets):
            if i in bullets_hit_indices: continue
            for j, enemy in enumerate(enemies):
                # Проверяем только живых врагов
                if enemy.is_alive() and bullet.colliderect(enemy.rect):
                    bullets_hit_indices.add(i)
                    enemy.take_damage(1) # Наносим урон
                    enemies_damaged_indices.add(j) # Отмечаем, что враг получил урон
                    if not enemy.is_alive():
                        # Враг уничтожен
                        score += enemy.score_value * level
                        if explosion_sound:
                             try: explosion_sound.play()
                             except: pass
                        if random.random() < powerup_spawn_chance:
                            spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                    else:
                        # Враг ранен, но жив (например, танк)
                        if enemy_hit_sound:
                             try: enemy_hit_sound.play()
                             except: pass
                    break # Пуля исчезает после первого попадания

        # Удаляем попавшие пули
        if bullets_hit_indices:
             bullets = [b for i, b in enumerate(bullets) if i not in bullets_hit_indices]

        # Удаляем уничтоженных врагов (после цикла проверки пуль)
        enemies = [e for e in enemies if e.is_alive()]


        # Пули врагов с игроком
        enemy_bullets_to_remove_indices = set()
        player_hit_this_frame = False # Флаг, чтобы избежать мульти-хита за кадр
        for i, bullet in enumerate(enemy_bullets):
            if player_rect.colliderect(bullet) and not player_hit_this_frame:
                enemy_bullets_to_remove_indices.add(i)
                player_hit_this_frame = True # Попадание обработано
                if player_shield_active:
                    player_shield_active = False
                    if player_hit_sound: try: player_hit_sound.play() # Звук поломки щита
                                         except: pass
                else:
                    player_lives -= 1
                    if player_hit_sound: try: player_hit_sound.play()
                                         except: pass
                    # Можно добавить короткую неуязвимость после попадания
                    player_rect.topleft = (player_start_x, player_start_y) # Возврат на старт
                    if player_lives <= 0:
                        game_over = True
                # Нет break, продолжаем удалять все пули, коснувшиеся игрока в этот кадр

        if enemy_bullets_to_remove_indices:
             enemy_bullets = [b for i, b in enumerate(enemy_bullets) if i not in enemy_bullets_to_remove_indices]

        # Враги с игроком или достигли низа
        enemies_collided_or_reached_bottom = False
        enemies_to_remove_on_collision = []

        for i, enemy in enumerate(enemies):
            # Столкновение врага с игроком
            if player_rect.colliderect(enemy.rect):
                 enemies_to_remove_on_collision.append(i) # Помечаем врага на удаление
                 if player_shield_active:
                     player_shield_active = False
                     # Враг уничтожается об щит, даем очки
                     score += enemy.score_value // 2 * level # Половинa очков за таран щита
                     if explosion_sound: try: explosion_sound.play()
                                           except: pass
                 else:
                    # Игрок теряет жизнь, враг уничтожается
                    player_lives -= 1
                    if player_hit_sound: try: player_hit_sound.play()
                                         except: pass
                    player_rect.topleft = (player_start_x, player_start_y)
                    if player_lives <= 0:
                        game_over = True
                        enemies_collided_or_reached_bottom = True # Выходим из цикла проверки

            # Проверка, достигли ли враги низа
            # Используем player_start_y как границу "вторжения"
            elif enemy.rect.bottom >= player_start_y:
                 game_over = True
                 player_lives = 0 # Мгновенный проигрыш
                 enemies_collided_or_reached_bottom = True # Выходим из цикла проверки

            if enemies_collided_or_reached_bottom: break # Выход из for enemy in enemies...

        # Удаляем врагов, столкнувшихся с игроком (делаем это после цикла)
        if enemies_to_remove_on_collision:
             # Удаляем с конца, чтобы не сбить индексы
             indices_to_remove = sorted(enemies_to_remove_on_collision, reverse=True)
             for index in indices_to_remove:
                 # Проверяем, что индекс все еще валиден (враг мог быть убит пулей в том же кадре)
                 if index < len(enemies):
                     # Вместо del используем take_damage, чтобы гарантировать 0 хп и потенциальные эффекты смерти
                     enemies[index].take_damage(enemies[index].max_health * 10) # Огромный урон для гарантии

        # Еще раз отфильтруем мертвых врагов после столкновений
        enemies = [e for e in enemies if e.is_alive()]


        # Проверяем game_over еще раз после всех столкновений
        if game_over:
            if sound_enabled:
                 try: pygame.mixer.music.stop()
                 except: pass
            continue

        # Игрок с бонусами
        powerups_collided_indices = set()
        for i, powerup in enumerate(powerups):
            powerup_rect, powerup_type = powerup
            if player_rect.colliderect(powerup_rect):
                powerups_collided_indices.add(i)
                if powerup_sound: try: powerup_sound.play(); except: pass
                if powerup_type == 'shield':
                    player_shield_active = True
                    player_shield_timer = current_time
                elif powerup_type == 'gun':
                    rapid_fire_active = True
                    rapid_fire_timer = current_time
                    current_shoot_delay = rapid_fire_shoot_delay

        if powerups_collided_indices:
            powerups = [p for i, p in enumerate(powerups) if i not in powerups_collided_indices]

        # --- Проверка победы на уровне ---
        if not enemies: # Если список врагов пуст
            level += 1
            update_difficulty(level)
            spawn_enemies(level)
            bullets.clear()
            enemy_bullets.clear()
            powerups.clear()
            player_rect.topleft = (player_start_x, player_start_y)
            # Сброс бонусов при переходе уровня - опционально
            # player_shield_active = False
            # rapid_fire_active = False
            # current_shoot_delay = base_shoot_delay
            last_enemy_shot_time = current_time + 1500 # Задержка перед стрельбой на новом уровне
            level_start_display_time = current_time # Показать "Уровень N"


    # --- Отрисовка ---
    # Фон
    screen.fill(BLACK)
    if background_img: # Сначала статичный фон, если есть
        screen.blit(background_img, (0,0))
    else: # Если нет картинки фона, рисуем звезды поверх черного
         for star in stars:
            try: pygame.draw.circle(screen, star[4], (star[0], star[1]), star[3])
            except: pass # Пропуск ошибки отрисовки звезды

    # Рисуем врагов (используя их метод draw)
    for enemy in enemies:
        enemy.draw(screen)

    # Рисуем пули игрока
    for bullet in bullets:
        if bullet_img: screen.blit(bullet_img, bullet)
        else: pygame.draw.rect(screen, RED, bullet)

    # Рисуем пули врагов
    for bullet in enemy_bullets:
        if enemy_bullet_img: screen.blit(enemy_bullet_img, bullet)
        else: pygame.draw.rect(screen, YELLOW, bullet)

    # Рисуем бонусы
    for powerup_rect, powerup_type in powerups:
        img_to_draw = None
        color_fallback = BLUE
        if powerup_type == 'shield': img_to_draw = powerup_shield_img
        elif powerup_type == 'gun': img_to_draw = powerup_gun_img; color_fallback = RED
        if img_to_draw: screen.blit(img_to_draw, powerup_rect)
        else: pygame.draw.rect(screen, color_fallback, powerup_rect)

    # Рисуем игрока
    if player_img: screen.blit(player_img, player_rect)
    else: pygame.draw.rect(screen, WHITE, player_rect)

    # Рисуем активный щит
    if player_shield_active:
        if shield_active_img:
            shield_rect = shield_active_img.get_rect(center=player_rect.center)
            screen.blit(shield_active_img, shield_rect)
        else:
            pygame.draw.circle(screen, BLUE, player_rect.center, player_width // 2 + 5, 2)

    # UI (Счет, Уровень, Жизни)
    draw_text(f"Счет: {score}", font, WHITE, screen, 10, 10)
    draw_text(f"Уровень: {level}", font, WHITE, screen, screen_width - 150, 10)
    draw_lives(screen, 10, screen_height - 40, player_lives, player_img)

    # Отображение "Уровень N" в начале уровня
    if current_time - level_start_display_time < level_display_duration and not game_over and not paused:
         level_font = pygame.font.Font(None, 60)
         draw_text(f"УРОВЕНЬ {level}", level_font, YELLOW, screen, screen_width // 2, screen_height // 2 - 60, center=True)

    # Если игра окончена
    if game_over:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        draw_text("ИГРА ОКОНЧЕНА", pygame.font.Font(None, 74), RED, screen, screen_width // 2, screen_height // 2 - 50, center=True)
        draw_text(f"Ваш счет: {score}", font, WHITE, screen, screen_width // 2, screen_height // 2 + 10, center=True)
        draw_text(f"Достигнут уровень: {level}", small_font, WHITE, screen, screen_width // 2, screen_height // 2 + 45, center=True)
        draw_text("Нажмите R для перезапуска", font, YELLOW, screen, screen_width // 2, screen_height // 2 + 85, center=True)

    # Копирайт (всегда поверх, кроме паузы)
    if not paused:
        try:
             copyright_surface = copyright_font.render(copyright_text, True, copyright_color)
             copyright_rect = copyright_surface.get_rect(bottomright=(screen_width - 10, screen_height - 5))
             screen.blit(copyright_surface, copyright_rect)
        except Exception as e:
            print(f"Ошибка отрисовки копирайта: {e}")

    # --- Обновление экрана ---
    pygame.display.flip()

    # --- Контроль FPS ---
    clock.tick(FPS)

# --- Завершение Pygame ---
if sound_enabled:
    try: pygame.mixer.music.stop()
    except: pass
pygame.quit()
sys.exit()