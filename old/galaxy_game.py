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
pygame.display.set_caption("Улучшенная Галактика (от Andrei Osipov)")

# --- Цвета ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150) # Для копирайта

# --- Настройки Космического Фона (Звезды) ---
NUM_STARS = 150 # Количество звезд
stars = [] # Список для хранения звезд [x, y, speed, size, color]

# Заполняем список звезд начальными значениями
for _ in range(NUM_STARS):
    x = random.randrange(0, screen_width)
    y = random.randrange(0, screen_height)
    # Разные скорости для эффекта параллакса
    speed = random.choice([1, 2, 3])
    size = speed # Размер зависит от скорости (быстрые = больше/ближе)
    # Цвет зависит от скорости (быстрые = ярче)
    brightness = 100 + 50 * speed # От 150 до 250
    color = (brightness, brightness, brightness)
    stars.append([x, y, speed, size, color])

# --- Загрузка Ассетов (Графика и Звуки) ---
# Функция для безопасной загрузки изображений
def load_image(filename, size=None):
    try:
        # Пытаемся найти файл рядом со скриптом
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
             # Если не нашли, пробуем просто имя файла (для случая, если он в рабочей директории)
             filepath = filename
             if not os.path.exists(filepath):
                 raise pygame.error(f"Файл не найден: {filename}")

        image = pygame.image.load(filepath).convert_alpha() # convert_alpha для прозрачности
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Не удалось загрузить изображение: {filename}. Ошибка: {e}")
        return None # Возвращаем None, если загрузка не удалась

# Функция для безопасной загрузки звуков
def load_sound(filename):
    if not sound_enabled:
        return None
    try:
        # Пытаемся найти файл рядом со скриптом
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
             # Если не нашли, пробуем просто имя файла
             filepath = filename
             if not os.path.exists(filepath):
                  raise pygame.error(f"Файл не найден: {filename}")

        sound = pygame.mixer.Sound(filepath)
        return sound
    except pygame.error as e:
        print(f"Не удалось загрузить звук: {filename}. Ошибка: {e}")
        return None # Возвращаем None, если загрузка не удалась

# Размеры объектов (используются и для Rect, и для масштабирования картинок)
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

# Загрузка изображений (Убедись, что файлы лежат рядом со скриптом или укажи путь)
player_img = load_image('player.png', (player_width, player_height))
enemy_img = load_image('enemy.png', (enemy_width, enemy_height))
bullet_img = load_image('bullet.png', (bullet_width, bullet_height))
enemy_bullet_img = load_image('enemy_bullet.png', (enemy_bullet_width, enemy_bullet_height))
background_img = load_image('background.jpg', (screen_width, screen_height)) # Статичный фон (опционально)
powerup_shield_img = load_image('shield_powerup.png', (powerup_width, powerup_height))
powerup_gun_img = load_image('gun_powerup.png', (powerup_width, powerup_height))
shield_active_img = load_image('shield_active.png', (player_width + 10, player_height + 10)) # Изображение активного щита

# Загрузка звуков (Убедись, что файлы лежат рядом со скриптом или укажи путь)
shoot_sound = load_sound('laser.wav')
explosion_sound = load_sound('explosion.wav')
player_hit_sound = load_sound('player_hit.wav')
powerup_sound = load_sound('powerup.wav')

# Фоновая музыка
if sound_enabled:
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        music_filepath = os.path.join(base_path, 'music.mp3')

        if not os.path.exists(music_filepath):
            music_filepath = 'music.mp3' # Пробуем без пути
            if not os.path.exists(music_filepath):
                 raise pygame.error("Файл music.mp3 не найден")

        pygame.mixer.music.load(music_filepath)
        pygame.mixer.music.set_volume(0.4) # Громкость музыки (0.0 до 1.0)
        pygame.mixer.music.play(-1) # -1 значит зациклить музыку
    except pygame.error as e:
        print(f"Не удалось загрузить или воспроизвести фоновую музыку: {e}")

# --- Настройки Игрока ---
player_start_x = (screen_width - player_width) // 2
player_start_y = screen_height - player_height - 20
player_speed = 6
player_rect = pygame.Rect(player_start_x, player_start_y, player_width, player_height)
player_lives = 3
player_shield_active = False
player_shield_timer = 0
shield_duration = 5000 # 5 секунд в миллисекундах
rapid_fire_active = False
rapid_fire_timer = 0
rapid_fire_duration = 8000 # 8 секунд
base_shoot_delay = 400 # Базовая задержка выстрела
rapid_fire_shoot_delay = 150

# --- Настройки Врагов ---
enemies = [] # Список для хранения врагов [rect]
enemy_spawn_rows = 4
enemy_spawn_cols = 8
enemy_spawn_x_start = 50 # Базовое начало X, будет центрироваться в spawn_enemies
enemy_spawn_y_start = 50
enemy_x_gap = 70
enemy_y_gap = 50

# Динамические параметры врагов (зависят от уровня)
base_enemy_speed = 1.5
base_enemy_shoot_delay = 1500 # Миллисекунды между выстрелами врагов (общий)
enemy_speed = base_enemy_speed
enemy_shoot_delay = base_enemy_shoot_delay
enemy_direction = 1
move_down_flag = False

# --- Настройки Пуль ---
bullets = [] # Пули игрока
enemy_bullets = [] # Пули врагов
bullet_speed = 8
enemy_bullet_speed = 5
can_shoot = True
shoot_timer = 0
current_shoot_delay = base_shoot_delay # Текущая задержка зависит от бонуса

# --- Настройки Бонусов (Power-ups) ---
powerups = [] # Список активных бонусов на экране [rect, type]
powerup_spawn_chance = 0.15 # Шанс появления бонуса при уничтожении врага (15%)
powerup_speed = 3
powerup_types = ['shield', 'gun']

# --- Уровни, Счет и Шрифты ---
score = 0
level = 1
font = pygame.font.Font(None, 36) # Стандартный шрифт
small_font = pygame.font.Font(None, 24) # Для доп. информации
copyright_font = pygame.font.Font(None, 18) # Маленький шрифт для копирайта
copyright_text = "Made by Andrei Osipov"
copyright_color = GREY

# --- Функции ---
def spawn_enemies(current_level):
    """Создает врагов в зависимости от уровня."""
    enemies.clear()
    rows = min(enemy_spawn_rows + (current_level // 3), 6)
    cols = min(enemy_spawn_cols + (current_level // 5), 10)

    # Центрируем сетку врагов для разного количества колонок
    grid_width = (cols - 1) * enemy_x_gap + enemy_width
    current_spawn_x_start = (screen_width - grid_width) // 2
    if current_spawn_x_start < 10: current_spawn_x_start = 10 # Ограничим слева

    for row in range(rows):
        for col in range(cols):
            enemy_x = current_spawn_x_start + col * enemy_x_gap
            enemy_y = enemy_spawn_y_start + row * enemy_y_gap
            enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
            enemies.append(enemy_rect)

def spawn_powerup(x, y):
    """Создает бонус в указанной точке."""
    # Ограничим количество бонусов на экране (например, не больше 2)
    if len(powerups) < 2:
        powerup_type = random.choice(powerup_types)
        powerup_rect = pygame.Rect(x - powerup_width // 2, y, powerup_width, powerup_height)
        powerups.append([powerup_rect, powerup_type])

def draw_text(text, font_obj, color, surface, x, y, center=False):
    """Удобная функция для отрисовки текста."""
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
    """Рисует жизни игрока."""
    if img: # Если есть иконка игрока
        try:
            img_scaled = pygame.transform.scale(img, (30, 25))
            for i in range(lives):
                img_rect = img_scaled.get_rect()
                img_rect.x = x + 40 * i # Небольшой отступ между иконками
                img_rect.y = y
                surface.blit(img_scaled, img_rect)
        except Exception as e: # Если масштабирование не удалось
             print(f"Ошибка масштабирования иконки жизней: {e}")
             draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y) # Резервный вариант
    else: # Если иконки нет, рисуем текстом
        draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y)

def update_difficulty(current_level):
    """Обновляет сложность игры на основе уровня."""
    global enemy_speed, enemy_shoot_delay
    enemy_speed = min(base_enemy_speed + (current_level - 1) * 0.2, 5)
    enemy_shoot_delay = max(base_enemy_shoot_delay - (current_level - 1) * 70, 400)

# --- Переменные состояния игры ---
running = True
game_over = False
paused = False
clock = pygame.time.Clock()
FPS = 60
last_enemy_shot_time = pygame.time.get_ticks()

# --- Первоначальная настройка ---
update_difficulty(level)
spawn_enemies(level)

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
                    if paused:
                        pygame.mixer.music.pause() # Пауза музыки
                    else:
                        pygame.mixer.music.unpause() # Возобновить музыку
            # Клавиши управления работают только если не пауза
            if not paused:
                if game_over and event.key == pygame.K_r: # Перезапуск по R
                    # --- Сброс игры ---
                    player_rect.x = player_start_x
                    player_rect.y = player_start_y
                    player_lives = 3
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
                    paused = False # Выходим из паузы, если она была при game over
                    can_shoot = True
                    last_enemy_shot_time = pygame.time.get_ticks() # Сброс таймера врагов
                    if sound_enabled:
                        try:
                           pygame.mixer.music.rewind() # Перемотать музыку на начало
                           pygame.mixer.music.play(-1) # Начать играть заново
                        except pygame.error as e:
                            print(f"Ошибка при перезапуске музыки: {e}")
                elif not game_over and event.key == pygame.K_SPACE and can_shoot:
                    # Создаем пулю над центром игрока
                    bullet_x = player_rect.centerx - bullet_width // 2
                    bullet_y = player_rect.top
                    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
                    bullets.append(bullet_rect)
                    if shoot_sound:
                        try: shoot_sound.play()
                        except Exception as e: print(f"Ошибка воспроизведения звука выстрела: {e}")
                    can_shoot = False # Запрещаем стрелять сразу
                    shoot_timer = current_time # Запускаем таймер перезарядки

    # --- Логика Паузы ---
    if paused:
        # Экран паузы
        # Затемнение
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Черный, полупрозрачный
        screen.blit(overlay, (0,0))
        # Текст
        draw_text("ПАУЗА", pygame.font.Font(None, 74), YELLOW, screen, screen_width // 2, screen_height // 2 - 50, center=True)
        draw_text("Нажмите P чтобы продолжить", font, WHITE, screen, screen_width // 2, screen_height // 2 + 20, center=True)
        # Копирайт на паузе
        copyright_surface = copyright_font.render(copyright_text, True, copyright_color)
        copyright_rect = copyright_surface.get_rect(bottomright=(screen_width - 10, screen_height - 5))
        screen.blit(copyright_surface, copyright_rect)

        pygame.display.flip()
        clock.tick(FPS) # Продолжаем тикать, чтобы не нагружать процессор
        continue # Пропускаем остальной игровой цикл

    # --- Основная игровая логика (если не Game Over и не Пауза) ---
    if not game_over:
        # --- Обновление Космического Фона ---
        for star in stars:
            star[1] += star[2] # Двигаем звезду вниз
            if star[1] > screen_height: # Если звезда ушла за нижний край
                star[1] = random.randrange(-20, 0) # Перемещаем ее наверх
                star[0] = random.randrange(0, screen_width) # Новая X позиция

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
        if not can_shoot:
            if current_time - shoot_timer > current_shoot_delay:
                can_shoot = True

        # --- Движение пуль игрока ---
        bullets = [b for b in bullets if b.bottom > 0] # Удаляем улетевшие
        for bullet in bullets:
            bullet.y -= bullet_speed # Двигаем оставшиеся

        # --- Движение пуль врагов ---
        enemy_bullets = [b for b in enemy_bullets if b.top < screen_height]
        for bullet in enemy_bullets:
            bullet.y += enemy_bullet_speed

        # --- Движение врагов ---
        move_down_flag = False
        if enemies: # Только если есть враги
            # Находим крайние X координаты текущих врагов
            min_x = min(e.left for e in enemies)
            max_x = max(e.right for e in enemies)

            # Проверяем, не выйдет ли крайний враг за экран при следующем шаге
            if (max_x + (enemy_speed * enemy_direction) > screen_width) or \
               (min_x + (enemy_speed * enemy_direction) < 0):
                move_down_flag = True

            # Двигаем всех врагов
            for enemy_rect in enemies:
                 if move_down_flag:
                     enemy_rect.y += enemy_height // 2 # Двигаем вниз
                 else:
                     enemy_rect.x += enemy_speed * enemy_direction # Двигаем вбок

            # Если двигались вниз, меняем направление и корректируем X
            if move_down_flag:
                enemy_direction *= -1
                # Коррекция нужна, чтобы враги не застряли у края после смены направления
                correction = enemy_speed * enemy_direction
                for enemy_rect in enemies:
                      enemy_rect.x += correction

        # --- Стрельба Врагов ---
        if enemies and current_time - last_enemy_shot_time > enemy_shoot_delay:
             # Выбираем случайного врага из нижнего ряда каждой колонки
             potential_shooters = []
             enemy_cols_x = sorted(list({e.x for e in enemies})) # Уникальные X-координаты колонок
             for x_col in enemy_cols_x:
                 col_enemies = [e for e in enemies if e.x == x_col]
                 if col_enemies:
                     bottom_enemy = max(col_enemies, key=lambda e: e.y)
                     potential_shooters.append(bottom_enemy)

             if potential_shooters:
                 shooter_rect = random.choice(potential_shooters)
                 bullet_x = shooter_rect.centerx - enemy_bullet_width // 2
                 bullet_y = shooter_rect.bottom
                 enemy_bullet_rect = pygame.Rect(bullet_x, bullet_y, enemy_bullet_width, enemy_bullet_height)
                 enemy_bullets.append(enemy_bullet_rect)
                 last_enemy_shot_time = current_time # Сбрасываем таймер

        # --- Движение бонусов ---
        powerups = [p for p in powerups if p[0].top < screen_height]
        for powerup in powerups:
            powerup[0].y += powerup_speed # powerup[0] это rect

        # --- Проверка столкновений ---
        # Пули игрока с врагами
        bullets_hit_indices = set()
        enemies_hit_indices = set()

        for i, bullet in enumerate(bullets):
            if i in bullets_hit_indices: continue # Пропускаем уже помеченные пули
            for j, enemy_rect in enumerate(enemies):
                if j not in enemies_hit_indices and bullet.colliderect(enemy_rect):
                    bullets_hit_indices.add(i)
                    enemies_hit_indices.add(j)
                    score += 10 * level
                    if explosion_sound:
                         try: explosion_sound.play()
                         except Exception as e: print(f"Ошибка воспроизведения звука взрыва: {e}")
                    # Шанс выпадения бонуса
                    if random.random() < powerup_spawn_chance:
                        spawn_powerup(enemy_rect.centerx, enemy_rect.centery)
                    break # Одна пуля - один враг

        # Удаляем столкнувшиеся объекты (эффективнее)
        if enemies_hit_indices:
            # Сначала удаляем врагов с конца списка, чтобы индексы не сместились
            sorted_indices = sorted(list(enemies_hit_indices), reverse=True)
            for index in sorted_indices:
                 if 0 <= index < len(enemies): # Доп. проверка
                     del enemies[index]
        if bullets_hit_indices:
             bullets = [b for i, b in enumerate(bullets) if i not in bullets_hit_indices]


        # Пули врагов с игроком
        enemy_bullets_to_remove_indices = set()
        for i, bullet in enumerate(enemy_bullets):
            if player_rect.colliderect(bullet):
                enemy_bullets_to_remove_indices.add(i)
                if player_shield_active:
                    player_shield_active = False # Щит поглотил удар
                    if player_hit_sound: # Звук поломки щита?
                         try: player_hit_sound.play()
                         except Exception as e: print(f"Ошибка воспр. звука попадания (щит): {e}")
                else:
                    player_lives -= 1
                    if player_hit_sound:
                         try: player_hit_sound.play()
                         except Exception as e: print(f"Ошибка воспр. звука попадания (игрок): {e}")
                    # Мигание или короткая неуязвимость? (Не реализовано)
                    player_rect.x = player_start_x # Возвращаем на старт
                    player_rect.y = player_start_y
                    if player_lives <= 0:
                        game_over = True
                break # Хватит одного попадания за кадр

        if enemy_bullets_to_remove_indices:
             enemy_bullets = [b for i, b in enumerate(enemy_bullets) if i not in enemy_bullets_to_remove_indices]


        # Враги с игроком или достигли низа
        enemies_collided_indices = set()
        for i, enemy_rect in enumerate(enemies):
            if player_rect.colliderect(enemy_rect):
                 enemies_collided_indices.add(i) # Помечаем врага на удаление
                 if player_shield_active:
                     player_shield_active = False
                     if explosion_sound:
                         try: explosion_sound.play()
                         except Exception as e: print(f"Ошибка воспр. звука взрыва (таран щита): {e}")
                     score += 5 * level
                 else:
                    player_lives -= 1
                    if player_hit_sound:
                        try: player_hit_sound.play()
                        except Exception as e: print(f"Ошибка воспр. звука попадания (таран): {e}")
                    player_rect.x = player_start_x
                    player_rect.y = player_start_y
                    if player_lives <= 0:
                        game_over = True
                 # После столкновения с игроком (или щитом) выходим из проверки этого врага
                 continue # Переходим к следующему врагу

            # Проверка, достигли ли враги низа
            if enemy_rect.bottom >= player_start_y - 10:
                 game_over = True
                 player_lives = 0 # Мгновенный проигрыш

        # Удаляем врагов, столкнувшихся с игроком (или дошедших до щита)
        if enemies_collided_indices:
             sorted_indices = sorted(list(enemies_collided_indices), reverse=True)
             for index in sorted_indices:
                 if 0 <= index < len(enemies):
                     del enemies[index]

        # Проверяем game_over после всех проверок столкновений
        if game_over:
            if sound_enabled:
                 try: pygame.mixer.music.stop()
                 except pygame.error as e: print(f"Ошибка остановки музыки: {e}")
            continue # Переходим к следующей итерации для отрисовки Game Over

        # Игрок с бонусами
        powerups_collided_indices = set()
        for i, powerup in enumerate(powerups):
            powerup_rect, powerup_type = powerup
            if player_rect.colliderect(powerup_rect):
                powerups_collided_indices.add(i)
                if powerup_sound:
                     try: powerup_sound.play()
                     except Exception as e: print(f"Ошибка воспр. звука бонуса: {e}")
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
        if not enemies:
            level += 1
            update_difficulty(level)
            spawn_enemies(level)
            # Очищаем экран от старых пуль и бонусов
            bullets.clear()
            enemy_bullets.clear()
            powerups.clear()
            player_rect.x = player_start_x
            player_rect.y = player_start_y
            # Сбрасываем бонусы игрока при переходе
            player_shield_active = False
            rapid_fire_active = False
            current_shoot_delay = base_shoot_delay
            # Даем передышку
            last_enemy_shot_time = current_time + 2000
            # TODO: Можно показать сообщение "Уровень N"


    # --- Отрисовка ---
    # Фон
    screen.fill(BLACK) # Базовый черный космос

    # Отрисовка Звезд
    for star in stars:
        # star[0]=x, star[1]=y, star[4]=color, star[3]=size (радиус)
        try:
            pygame.draw.circle(screen, star[4], (star[0], star[1]), star[3])
        except TypeError as e:
             # print(f"Ошибка отрисовки звезды: {star} - {e}") # Отладка
             pass # Пропускаем звезду, если данные некорректны

    # Опциональный статичный фон поверх звезд
    if background_img:
        screen.blit(background_img, (0,0))

    # Рисуем врагов
    for enemy_rect in enemies:
        if enemy_img:
            screen.blit(enemy_img, enemy_rect)
        else:
            pygame.draw.rect(screen, GREEN, enemy_rect)

    # Рисуем пули игрока
    for bullet in bullets:
        if bullet_img:
             screen.blit(bullet_img, bullet)
        else:
             pygame.draw.rect(screen, RED, bullet)

    # Рисуем пули врагов
    for bullet in enemy_bullets:
        if enemy_bullet_img:
             screen.blit(enemy_bullet_img, bullet)
        else:
             pygame.draw.rect(screen, YELLOW, bullet)

    # Рисуем бонусы
    for powerup_rect, powerup_type in powerups:
        img_to_draw = None
        color_fallback = BLUE # По умолчанию для щита
        if powerup_type == 'shield' and powerup_shield_img:
            img_to_draw = powerup_shield_img
        elif powerup_type == 'gun' and powerup_gun_img:
            img_to_draw = powerup_gun_img
            color_fallback = RED # Для пушки

        if img_to_draw:
            screen.blit(img_to_draw, powerup_rect)
        else:
            pygame.draw.rect(screen, color_fallback, powerup_rect)

    # Рисуем игрока
    if player_img:
        screen.blit(player_img, player_rect)
    else:
        pygame.draw.rect(screen, WHITE, player_rect)

    # Рисуем активный щит поверх игрока
    if player_shield_active:
        if shield_active_img:
            shield_rect = shield_active_img.get_rect(center=player_rect.center)
            screen.blit(shield_active_img, shield_rect)
        else:
            pygame.draw.circle(screen, BLUE, player_rect.center, player_width // 2 + 5, 2)

    # Отображаем UI (Счет, Уровень, Жизни)
    draw_text(f"Счет: {score}", font, WHITE, screen, 10, 10)
    draw_text(f"Уровень: {level}", font, WHITE, screen, screen_width - 150, 10)
    draw_lives(screen, 10, screen_height - 40, player_lives, player_img) # Используем player_img для иконок жизней

    # Если игра окончена
    if game_over:
        # Затемнение фона
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        # Текст Game Over
        draw_text("ИГРА ОКОНЧЕНА", pygame.font.Font(None, 74), RED, screen, screen_width // 2, screen_height // 2 - 50, center=True)
        draw_text(f"Ваш счет: {score}", font, WHITE, screen, screen_width // 2, screen_height // 2 + 10, center=True)
        draw_text(f"Достигнут уровень: {level}", small_font, WHITE, screen, screen_width // 2, screen_height // 2 + 45, center=True)
        draw_text("Нажмите R для перезапуска", font, YELLOW, screen, screen_width // 2, screen_height // 2 + 85, center=True)

    # Отрисовка копирайта (всегда поверх всего, кроме может быть паузы)
    if not paused: # Не рисуем если на паузе, т.к. там своя отрисовка копирайта
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
    except: pass # Игнорируем ошибки при остановке музыки
pygame.quit()
sys.exit()