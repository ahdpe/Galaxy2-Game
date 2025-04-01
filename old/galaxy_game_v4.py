# -*- coding: utf-8 -*-
import pygame
import random
import sys
import os
import math

# --- Инициализация Pygame и Микшера ---
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error as e:
    print(f"Не удалось инициализировать микшер звука: {e}. Звук будет отключен.")
    sound_enabled = False

# --- Настройки экрана ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Улучшенная Галактика (Меню/Сложность - от Andrei Osipov)")

# --- Цвета ---
BLACK = (0, 0, 0); WHITE = (255, 255, 255); RED = (255, 0, 0); GREEN = (0, 255, 0)
BLUE = (0, 0, 255); YELLOW = (255, 255, 0); GREY = (150, 150, 150); ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128); HIGHLIGHT_COLOR = YELLOW

# --- Настройки Космического Фона (Звезды) - для геймплея ---
NUM_STARS = 150
stars = []
for _ in range(NUM_STARS):
    x = random.randrange(0, screen_width); y = random.randrange(0, screen_height)
    speed = random.choice([1, 2, 3]); size = speed
    brightness = 100 + 50 * speed; color = (brightness, brightness, brightness)
    stars.append([x, y, speed, size, color])

# --- Загрузка Ассетов (Графика и Звуки) ---
def load_image(filename, size=None, use_colorkey=False, colorkey_color=BLACK):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath): filepath = filename
        if not os.path.exists(filepath): raise pygame.error(f"Файл не найден: {filename}")
        try: image = pygame.image.load(filepath)
        except pygame.error as load_error: print(f"Ошибка Pygame {filename}: {load_error}"); return None
        if image.get_alpha() is None and not use_colorkey: image = image.convert()
        elif use_colorkey: image = image.convert(); image.set_colorkey(colorkey_color)
        else: image = image.convert_alpha()
        if size: image = pygame.transform.scale(image, size)
        return image
    except Exception as e: print(f"Не удалось загрузить/обработать: {filename}. Ошибка: {e}"); return None

def load_sound(filename):
    if not sound_enabled: return None
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath): filepath = filename
        if not os.path.exists(filepath): raise pygame.error(f"Файл не найден: {filename}")
        sound = pygame.mixer.Sound(filepath)
        return sound
    except pygame.error as e: print(f"Не удалось загрузить звук: {filename}. Ошибка: {e}"); return None

# --- Размеры и Загрузка Изображений ---
player_width=60; player_height=50; bullet_width=8; bullet_height=20; enemy_bullet_width=6
enemy_bullet_height=12; powerup_width=30; powerup_height=30
enemy_basic_size=(45, 35); enemy_tank_size=(55, 45); enemy_shooter_size=(40, 40)

player_img = load_image('player.png', (player_width, player_height))
bullet_img = load_image('bullet.png', (bullet_width, bullet_height))
enemy_bullet_img = load_image('enemy_bullet.png', (enemy_bullet_width, enemy_bullet_height))
game_background_img = load_image('background.jpg', (screen_width, screen_height))
powerup_shield_img = load_image('shield_powerup.png', (powerup_width, powerup_height))
powerup_gun_img = load_image('gun_powerup.png', (powerup_width, powerup_height))
shield_active_img = load_image('shield_active.png', (player_width + 10, player_height + 10))
enemy_img_basic = load_image('enemy.png', enemy_basic_size)
enemy_img_tank = load_image('enemy_tank.png', enemy_tank_size)
enemy_img_shooter = load_image('enemy_shooter.png', enemy_shooter_size)
intro_background = load_image('intro_background.png', (screen_width, screen_height))
outro_background = load_image('outro_background.png', (screen_width, screen_height))

# --- Данные о типах врагов ---
ENEMY_STATS = {
    'basic': {'health': 1, 'speed_mult': 1.0, 'score': 10, 'img': enemy_img_basic, 'size': enemy_basic_size, 'color': GREEN, 'shoot_freq_mod': 1.0},
    'tank': {'health': 3, 'speed_mult': 0.7, 'score': 30, 'img': enemy_img_tank, 'size': enemy_tank_size, 'color': PURPLE, 'shoot_freq_mod': 1.5},
    'shooter': {'health': 1, 'speed_mult': 0.9, 'score': 25, 'img': enemy_img_shooter, 'size': enemy_shooter_size, 'color': ORANGE, 'shoot_freq_mod': 0.6},
}

# --- Загрузка Звуков ---
shoot_sound = load_sound('laser.wav'); explosion_sound = load_sound('explosion.wav')
player_hit_sound = load_sound('player_hit.wav'); powerup_sound = load_sound('powerup.wav')
enemy_hit_sound = load_sound('enemy_hit.wav'); menu_change_sound = load_sound('menu_change.wav')
menu_select_sound = load_sound('menu_select.wav')

# --- Настройки Игрока ---
player_start_x=(screen_width-player_width)//2; player_start_y=screen_height-player_height-20
player_speed=6; player_rect = pygame.Rect(player_start_x,player_start_y,player_width,player_height)
player_lives_start=3; player_lives=player_lives_start
player_shield_active=False; player_shield_timer=0; shield_duration=5000
rapid_fire_active=False; rapid_fire_timer=0; rapid_fire_duration=8000
base_shoot_delay=400; rapid_fire_shoot_delay=150; current_shoot_delay=base_shoot_delay; can_shoot=True

# --- Класс Врага ---
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.type = enemy_type; stats = ENEMY_STATS[enemy_type]
        self.width, self.height = stats['size']; self.rect = pygame.Rect(x, y, self.width, self.height)
        self.max_health = stats['health']; self.health = self.max_health
        self.speed_mult = stats['speed_mult']; self.score_value = stats['score']
        self.image = stats['img']; self.color = stats['color']; self.shoot_mod = stats['shoot_freq_mod']
    def take_damage(self, amount): self.health -= amount; self.health = max(0, self.health)
    def draw(self, surface):
        img_to_draw = self.image
        if self.type == 'tank' and self.health < self.max_health: pass
        if img_to_draw: surface.blit(img_to_draw, self.rect)
        else:
            health_ratio = self.health/self.max_health if self.max_health>0 else 0
            r=int(self.color[0]*health_ratio+RED[0]*(1-health_ratio)); g=int(self.color[1]*health_ratio+RED[1]*(1-health_ratio)); b=int(self.color[2]*health_ratio+RED[2]*(1-health_ratio))
            pygame.draw.rect(surface, (max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b))), self.rect)
    def is_alive(self): return self.health > 0

# --- Настройки Врагов ---
enemies = []; enemy_spawn_y_start=50; enemy_x_gap=70; enemy_y_gap=50
base_enemy_speed=1.5; base_enemy_shoot_delay=1800; enemy_speed=base_enemy_speed
enemy_shoot_delay=base_enemy_shoot_delay; enemy_direction=1; move_down_flag=False
LEVEL1_BASIC_COUNT=4; LEVEL5_MAX_ROWS=6; LEVEL5_MAX_COLS=10; LEVEL5_MAX_ENEMIES=LEVEL5_MAX_ROWS*LEVEL5_MAX_COLS

# --- Настройки Сложности ---
difficulty_levels = ["easy", "medium", "hard"]; difficulty_level = "medium"
DIFFICULTY_SETTINGS = {
    "easy":   {"speed_mult": 0.75, "shoot_delay_mult": 1.3, "score_mult": 0.8},
    "medium": {"speed_mult": 1.0,  "shoot_delay_mult": 1.0, "score_mult": 1.0},
    "hard":   {"speed_mult": 1.25, "shoot_delay_mult": 0.75, "score_mult": 1.2} }

# --- Настройки Пуль / Бонусов / UI ---
bullets=[]; enemy_bullets=[]; powerups=[]; bullet_speed=8; enemy_bullet_speed=5; shoot_timer=0
powerup_spawn_chance=0.12; powerup_speed=3; powerup_types=['shield','gun']
score=0; level=1; font=pygame.font.Font(None, 36); small_font=pygame.font.Font(None, 24)
copyright_font=pygame.font.Font(None, 18); copyright_text="Made by Andrei Osipov"; copyright_color=GREY
level_start_display_time=0; level_display_duration=2000

# --- Функции ---
def get_wave_composition(current_level):
    composition={}; rows=0; cols=0; total_enemies=0
    if current_level == 1:
        num_tanks=1; num_shooters=2; num_basic=LEVEL1_BASIC_COUNT; total_enemies=num_tanks+num_shooters+num_basic
        composition={'tank':num_tanks,'shooter':num_shooters,'basic':num_basic}; cols=min(total_enemies,LEVEL5_MAX_COLS); rows=math.ceil(total_enemies/cols) if cols>0 else 0
    elif 2<=current_level<5:
        level1_total=1+2+LEVEL1_BASIC_COUNT; progress=(current_level-1)/4.0; target_total=int(level1_total+(LEVEL5_MAX_ENEMIES-level1_total)*progress)
        total_enemies=max(level1_total,target_total); num_tanks=max(1,int(total_enemies*0.1+(current_level-1)*0.5)); num_shooters=max(2,int(total_enemies*0.2+(current_level-1)))
        num_basic=total_enemies-num_tanks-num_shooters
        if num_basic<0: num_shooters+=num_basic//2; num_tanks+=num_basic-(num_basic//2); num_basic=0
        num_tanks=max(1,num_tanks); num_shooters=max(2,num_shooters); num_basic=max(0,total_enemies-num_tanks-num_shooters)
        composition={'tank':num_tanks,'shooter':num_shooters,'basic':num_basic}; cols=min(LEVEL5_MAX_COLS,6+(current_level//2)); rows=math.ceil(total_enemies/cols) if cols>0 else 0; rows=min(rows,LEVEL5_MAX_ROWS)
    else:
        total_enemies=LEVEL5_MAX_ENEMIES; num_tanks=total_enemies//4; num_shooters=total_enemies//3; num_basic=max(0,total_enemies-num_tanks-num_shooters)
        composition={'tank':num_tanks,'shooter':num_shooters,'basic':num_basic}; rows=LEVEL5_MAX_ROWS; cols=LEVEL5_MAX_COLS
    return composition, rows, cols

def spawn_enemies(current_level):
    global enemy_direction
    enemies.clear(); enemy_direction=1; composition,rows,cols=get_wave_composition(current_level)
    enemy_pool=[]; max_enemy_width_in_wave=0
    for type, count in composition.items(): enemy_pool.extend([type]*count)
    random.shuffle(enemy_pool)
    if enemy_pool:
        try: max_enemy_width_in_wave=max(ENEMY_STATS[etype]['size'][0] for etype in set(enemy_pool))
        except KeyError: max_enemy_width_in_wave=enemy_basic_size[0]
    if max_enemy_width_in_wave==0: max_enemy_width_in_wave=enemy_basic_size[0]
    grid_width=(cols-1)*enemy_x_gap+max_enemy_width_in_wave; current_spawn_x_start=max(10,(screen_width-grid_width)//2)
    enemy_index=0
    for row in range(rows):
        for col in range(cols):
            if enemy_index<len(enemy_pool):
                enemy_type=enemy_pool[enemy_index]; enemy_stats=ENEMY_STATS[enemy_type]; cell_center_x=current_spawn_x_start+col*enemy_x_gap+max_enemy_width_in_wave//2
                enemy_x=cell_center_x-enemy_stats['size'][0]//2; enemy_y=enemy_spawn_y_start+row*enemy_y_gap
                enemies.append(Enemy(enemy_x,enemy_y,enemy_type)); enemy_index+=1
            else: break

def spawn_powerup(x, y):
    if len(powerups)<3: powerup_type=random.choice(powerup_types); powerup_rect=pygame.Rect(x-powerup_width//2,y,powerup_width,powerup_height); powerups.append([powerup_rect,powerup_type])

def draw_text(text, font_obj, color, surface, x, y, center=False):
    try:
        textobj=font_obj.render(text, True, color); textrect=textobj.get_rect()
        if center: textrect.center=(x,y)
        else: textrect.topleft=(x,y)
        surface.blit(textobj, textrect)
    except Exception as e: print(f"Ошибка отрисовки '{text}': {e}")

def draw_lives(surface, x, y, lives, img):
    life_icon_size=(30,25)
    if img:
        try: img_scaled=pygame.transform.scale(img, life_icon_size); [surface.blit(img_scaled, (x+(life_icon_size[0]+10)*i, y)) for i in range(lives)]
        except Exception as e: print(f"Ошибка иконки жизней: {e}"); draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y)
    else: draw_text(f"Жизни: {lives}", font, WHITE, surface, x, y)

def update_difficulty(current_level):
    global enemy_speed, enemy_shoot_delay
    base_sp=min(base_enemy_speed+(current_level-1)*0.15, 6.0); base_sh_delay=max(base_enemy_shoot_delay-(current_level-1)*60, 350)
    diff_mods=DIFFICULTY_SETTINGS[difficulty_level]; enemy_speed=base_sp*diff_mods["speed_mult"]; enemy_shoot_delay=base_sh_delay*diff_mods["shoot_delay_mult"]

# --- Переменные состояния игры и меню ---
game_state="INTRO"; running=True; paused=False; game_over=False; selected_difficulty_index=1
clock=pygame.time.Clock(); FPS=60; last_enemy_shot_time=pygame.time.get_ticks()

# --- Сброс игры (Функция) ---
def reset_game():
    global player_rect, player_lives, level, score, enemy_direction, game_over, paused, last_enemy_shot_time
    global current_shoot_delay, player_shield_active, rapid_fire_active, level_start_display_time, can_shoot
    player_rect.topleft=(player_start_x,player_start_y); player_lives=player_lives_start; level=1; score=0
    update_difficulty(level); spawn_enemies(level); bullets.clear(); enemy_bullets.clear(); powerups.clear()
    player_shield_active=False; rapid_fire_active=False; current_shoot_delay=base_shoot_delay; game_over=False
    paused=False; can_shoot=True; last_enemy_shot_time=pygame.time.get_ticks()+1500; level_start_display_time=pygame.time.get_ticks()
    if sound_enabled:
        try:
            base_path=getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__))); music_filepath=os.path.join(base_path,'music.mp3')
            if not os.path.exists(music_filepath): music_filepath='music.mp3'
            if os.path.exists(music_filepath):
                 pygame.mixer.music.load(music_filepath)
                 pygame.mixer.music.set_volume(0.4)
                 print("Музыка загружена для игры.")
                 pygame.mixer.music.rewind()
                 pygame.mixer.music.play(-1)
            else: print("Файл 'music.mp3' не найден для игры.")
        except pygame.error as e: print(f"Ошибка музыки при рестарте: {e}")

# --- Игровой цикл с состояниями ---
# reset_game() # Не вызываем здесь
# game_state = "INTRO" # Установлено выше

while running:
    current_time = pygame.time.get_ticks()
    events = pygame.event.get()

    # --- Состояние: INTRO (Меню) ---
    if game_state == "INTRO":
        if sound_enabled and pygame.mixer.music.get_busy():
             pygame.mixer.music.fadeout(500)

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_difficulty_index = (selected_difficulty_index - 1) % len(difficulty_levels)
                    if menu_change_sound:
                        try: menu_change_sound.play()
                        except Exception as e: print(f"Ошибка звука menu_change: {e}")
                elif event.key == pygame.K_DOWN:
                    selected_difficulty_index = (selected_difficulty_index + 1) % len(difficulty_levels)
                    if menu_change_sound:
                        try: menu_change_sound.play()
                        except Exception as e: print(f"Ошибка звука menu_change: {e}")
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    difficulty_level = difficulty_levels[selected_difficulty_index]
                    if menu_select_sound:
                        try: menu_select_sound.play()
                        except Exception as e: print(f"Ошибка звука menu_select: {e}")
                    reset_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_ESCAPE: running = False

        screen.fill(BLACK)
        if intro_background: screen.blit(intro_background, (0,0))
        else: draw_text("Улучшенная Галактика", pygame.font.Font(None, 64), WHITE, screen, screen_width//2, 100, center=True)
        draw_text("Выберите сложность:", font, WHITE, screen, screen_width//2, screen_height//2 - 60, center=True)
        for i, level_name in enumerate(difficulty_levels):
            color = HIGHLIGHT_COLOR if i == selected_difficulty_index else WHITE
            draw_text(level_name.upper(), font, color, screen, screen_width//2, screen_height//2 - 20 + i*40, center=True)
        controls_y_start = screen_height//2 + 80
        draw_text("Управление:", small_font, WHITE, screen, 100, controls_y_start)
        draw_text("Стрелки Влево/Вправо - Движение", small_font, WHITE, screen, 100, controls_y_start + 25)
        draw_text("Пробел - Стрелять", small_font, WHITE, screen, 100, controls_y_start + 50)
        draw_text("P - Пауза", small_font, WHITE, screen, 100, controls_y_start + 75)
        draw_text("Нажмите ENTER для старта", font, YELLOW, screen, screen_width//2, screen_height - 70, center=True)
        draw_text("Нажмите ESC для выхода", small_font, GREY, screen, screen_width//2, screen_height - 40, center=True)
        try: copyright_surface=copyright_font.render(copyright_text,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(screen_width-10,screen_height-5)); screen.blit(copyright_surface,copyright_rect)
        except Exception as e: print(f"Ошибка копирайта (интро): {e}")

    # --- Состояние: PLAYING (Игра) ---
    elif game_state == "PLAYING":
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if sound_enabled:
                        if paused: pygame.mixer.music.pause()
                        else: pygame.mixer.music.unpause()
                elif not paused and event.key == pygame.K_SPACE and can_shoot:
                    bullet_x=player_rect.centerx-bullet_width//2; bullet_y=player_rect.top
                    bullets.append(pygame.Rect(bullet_x,bullet_y,bullet_width,bullet_height))
                    if shoot_sound:
                        try: shoot_sound.play()
                        except Exception as e: print(f"Ошибка звука выстрела: {e}")
                    can_shoot=False; shoot_timer=current_time

        if paused:
            overlay=pygame.Surface((screen_width,screen_height), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            draw_text("ПАУЗА", pygame.font.Font(None, 74), YELLOW, screen, screen_width//2, screen_height//2-50, center=True)
            draw_text("Нажмите P чтобы продолжить", font, WHITE, screen, screen_width//2, screen_height//2+20, center=True)
            try: copyright_surface=copyright_font.render(copyright_text,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(screen_width-10,screen_height-5)); screen.blit(copyright_surface,copyright_rect)
            except Exception as e: print(f"Ошибка копирайта (пауза): {e}")
            pygame.display.flip(); clock.tick(FPS); continue

        # --- Основная игровая логика ---
        for star in stars: star[1]+=star[2]; star[0]=random.randrange(0,screen_width) if star[1]>screen_height else star[0]; star[1]=random.randrange(-20,0) if star[1]>screen_height else star[1]
        keys=pygame.key.get_pressed(); player_rect.x -= player_speed if keys[pygame.K_LEFT] and player_rect.left>0 else 0; player_rect.x += player_speed if keys[pygame.K_RIGHT] and player_rect.right<screen_width else 0
        if player_shield_active and current_time-player_shield_timer>shield_duration: player_shield_active=False
        if rapid_fire_active and current_time-rapid_fire_timer>rapid_fire_duration: rapid_fire_active=False; current_shoot_delay=base_shoot_delay
        if not can_shoot and current_time-shoot_timer>current_shoot_delay: can_shoot=True
        bullets=[b for b in bullets if b.bottom>0]; [bullet.move_ip(0,-bullet_speed) for bullet in bullets]
        enemy_bullets=[b for b in enemy_bullets if b.top<screen_height]; [bullet.move_ip(0,enemy_bullet_speed) for bullet in enemy_bullets]
        move_down_flag=False
        if enemies:
            min_x=min(e.rect.left for e in enemies); max_x=max(e.rect.right for e in enemies); step=enemy_speed*enemy_direction
            if (max_x+step>screen_width and enemy_direction>0) or (min_x+step<0 and enemy_direction<0): move_down_flag=True
            if move_down_flag: [enemy.rect.move_ip(0,enemy_y_gap//2) for enemy in enemies]; enemy_direction*=-1
            [enemy.rect.move_ip(enemy_speed*enemy.speed_mult*enemy_direction,0) for enemy in enemies]
        if enemies and current_time-last_enemy_shot_time>enemy_shoot_delay:
             potential_shooters=[]; cols_grouped={}
             for enemy in enemies:
                 found_col=False
                 for x_key in cols_grouped:
                     if abs(enemy.rect.centerx-x_key)<enemy_x_gap/1.5: cols_grouped[x_key].append(enemy); found_col=True; break
                 if not found_col: cols_grouped[enemy.rect.centerx]=[enemy]
             [potential_shooters.append(max(col_enemies_list, key=lambda e: e.rect.bottom)) for x_col, col_enemies_list in cols_grouped.items() if col_enemies_list]
             if potential_shooters:
                 shooters=[e for e in potential_shooters if e.type=='shooter']; non_shooters=[e for e in potential_shooters if e.type!='shooter']; chosen_shooter=None
                 if shooters and random.random()<0.7: chosen_shooter=random.choice(shooters)
                 elif non_shooters: chosen_shooter=random.choice(non_shooters)
                 elif shooters: chosen_shooter=random.choice(shooters)
                 if chosen_shooter:
                    shoot_chance=1.0/(chosen_shooter.shoot_mod+0.5)*0.5
                    if random.random()<shoot_chance: bullet_x=chosen_shooter.rect.centerx-enemy_bullet_width//2; bullet_y=chosen_shooter.rect.bottom; enemy_bullets.append(pygame.Rect(bullet_x,bullet_y,enemy_bullet_width,enemy_bullet_height)); last_enemy_shot_time=current_time
        powerups=[p for p in powerups if p[0].top<screen_height]; [powerup[0].move_ip(0,powerup_speed) for powerup in powerups]
        bullets_hit_indices=set(); enemies_damaged_this_frame=False
        # ИСПРАВЛЕНО: Звуки в столкновениях
        for i, bullet in enumerate(bullets):
            if i in bullets_hit_indices: continue
            for j, enemy in enumerate(enemies):
                if enemy.is_alive() and bullet.colliderect(enemy.rect):
                    bullets_hit_indices.add(i); enemy.take_damage(1); enemies_damaged_this_frame=True
                    if not enemy.is_alive():
                        score_increase=int(enemy.score_value*level*DIFFICULTY_SETTINGS[difficulty_level]["score_mult"]); score+=score_increase
                        if explosion_sound:
                            try: explosion_sound.play()
                            except Exception as e: print(f"Sound Error: {e}")
                        if random.random()<powerup_spawn_chance:
                            spawn_powerup(enemy.rect.centerx,enemy.rect.centery)
                    break
        if enemies_damaged_this_frame and any(e.is_alive() for e in enemies):
             if enemy_hit_sound:
                 try: enemy_hit_sound.play()
                 except Exception as e: print(f"Sound Error: {e}")
        if bullets_hit_indices: bullets=[b for i,b in enumerate(bullets) if i not in bullets_hit_indices]
        enemies=[e for e in enemies if e.is_alive()]
        enemy_bullets_to_remove_indices=set(); player_hit_this_frame=False
        for i,bullet in enumerate(enemy_bullets):
            if not player_hit_this_frame and player_rect.colliderect(bullet):
                enemy_bullets_to_remove_indices.add(i); player_hit_this_frame=True
                if player_shield_active:
                    player_shield_active=False
                    if player_hit_sound:
                        try: player_hit_sound.play()
                        except Exception as e: print(f"Sound Error: {e}")
                else:
                    player_lives-=1
                    if player_hit_sound:
                        try: player_hit_sound.play()
                        except Exception as e: print(f"Sound Error: {e}")
                    player_rect.topleft=(player_start_x,player_start_y)
                    if player_lives<=0: game_over=True; break
        if enemy_bullets_to_remove_indices: enemy_bullets=[b for i,b in enumerate(enemy_bullets) if i not in enemy_bullets_to_remove_indices]
        if not game_over:
            enemies_collided_or_reached_bottom=False
            for i,enemy in enumerate(enemies):
                if player_rect.colliderect(enemy.rect):
                     if player_shield_active:
                         player_shield_active=False
                         score_increase=int(enemy.score_value//2*level*DIFFICULTY_SETTINGS[difficulty_level]["score_mult"]); score+=score_increase
                         if explosion_sound:
                             try: explosion_sound.play()
                             except Exception as e: print(f"Sound Error: {e}")
                         enemy.take_damage(enemy.max_health*10)
                     else:
                         player_lives-=1
                         if player_hit_sound:
                             try: player_hit_sound.play()
                             except Exception as e: print(f"Sound Error: {e}")
                         player_rect.topleft=(player_start_x,player_start_y); enemy.take_damage(enemy.max_health*10)
                         if player_lives<=0: game_over=True; enemies_collided_or_reached_bottom=True
                elif enemy.rect.bottom>=player_start_y:
                     game_over=True; player_lives=0; enemies_collided_or_reached_bottom=True
                if enemies_collided_or_reached_bottom: break
            enemies=[e for e in enemies if e.is_alive()]
        powerups_collided_indices=set()
        for i,powerup in enumerate(powerups):
            powerup_rect,powerup_type=powerup
            if player_rect.colliderect(powerup_rect):
                powerups_collided_indices.add(i)
                if powerup_sound:
                    try: powerup_sound.play()
                    except Exception as e: print(f"Sound Error: {e}")
                if powerup_type=='shield': player_shield_active=True; player_shield_timer=current_time
                elif powerup_type=='gun': rapid_fire_active=True; rapid_fire_timer=current_time; current_shoot_delay=rapid_fire_shoot_delay
        if powerups_collided_indices: powerups=[p for i,p in enumerate(powerups) if i not in powerups_collided_indices]
        if not game_over and not enemies:
            level+=1; update_difficulty(level); spawn_enemies(level); bullets.clear(); enemy_bullets.clear(); powerups.clear()
            player_rect.topleft=(player_start_x,player_start_y); last_enemy_shot_time=current_time+2000; level_start_display_time=current_time
        if game_over:
            game_state="GAME_OVER"
            if sound_enabled: pygame.mixer.music.stop()
            player_shield_active=False; rapid_fire_active=False; current_shoot_delay=base_shoot_delay; continue

        # --- Отрисовка Игрового Экрана ---
        screen.fill(BLACK)
        if game_background_img: screen.blit(game_background_img,(0,0))
        else: # Рисуем звезды, если нет фона
            for star in stars:
                try: pygame.draw.circle(screen, star[4], (star[0], star[1]), star[3])
                except: pass
        # Враги
        for enemy in enemies: enemy.draw(screen)
        # Пули игрока
        for bullet in bullets:
            if bullet_img: screen.blit(bullet_img, bullet)
            else: pygame.draw.rect(screen, RED, bullet)
        # Пули врагов
        for bullet in enemy_bullets:
            if enemy_bullet_img: screen.blit(enemy_bullet_img, bullet)
            else: pygame.draw.rect(screen, YELLOW, bullet)
        # Бонусы - ИСПРАВЛЕНО СНОВА:
        for powerup_rect, powerup_type in powerups:
            img=powerup_shield_img if powerup_type=='shield' else powerup_gun_img
            color=BLUE if powerup_type=='shield' else RED
            # Разделяем blit и draw.rect
            if img:
                screen.blit(img, powerup_rect)
            else:
                pygame.draw.rect(screen, color, powerup_rect)
        # Игрок
        if player_img: screen.blit(player_img, player_rect)
        else: pygame.draw.rect(screen, WHITE, player_rect)
        # Щит игрока
        if player_shield_active:
            if shield_active_img: screen.blit(shield_active_img, shield_active_img.get_rect(center=player_rect.center))
            else: pygame.draw.circle(screen, BLUE, player_rect.center, player_width//2+5, 2)
        # UI Текст
        draw_text(f"Счет: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Уровень: {level}", font, WHITE, screen, screen_width-150, 10)
        draw_text(f"Сложность: {difficulty_level.upper()}", small_font, WHITE, screen, screen_width-150, 40)
        # Жизни
        draw_lives(screen, 10, screen_height-40, player_lives, player_img)
        # Сообщение "Уровень N"
        if current_time-level_start_display_time<level_display_duration:
            draw_text(f"УРОВЕНЬ {level}", pygame.font.Font(None,60), YELLOW, screen, screen_width//2, screen_height//2-60, center=True)
        # Копирайт (только если не пауза)
        if not paused:
            try:
                copyright_surface=copyright_font.render(copyright_text,True,copyright_color)
                copyright_rect=copyright_surface.get_rect(bottomright=(screen_width-10,screen_height-5))
                screen.blit(copyright_surface,copyright_rect)
            except Exception as e:
                 print(f"Ошибка копирайта (игра): {e}")

    # --- Состояние: GAME_OVER ---
    elif game_state == "GAME_OVER":
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if menu_select_sound:
                        try: menu_select_sound.play()
                        except Exception as e: print(f"Ошибка звука menu_select: {e}")
                    reset_game()
                    game_state = "PLAYING"
                elif event.key == pygame.K_m:
                     if menu_change_sound:
                         try: menu_change_sound.play()
                         except Exception as e: print(f"Ошибка звука menu_change: {e}")
                     game_state = "INTRO"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                     if menu_change_sound:
                         try: menu_change_sound.play()
                         except Exception as e: print(f"Ошибка звука menu_change: {e}")
                     game_state = "OUTRO"

        overlay=pygame.Surface((screen_width,screen_height), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
        draw_text("ИГРА ОКОНЧЕНА", pygame.font.Font(None, 74), RED, screen, screen_width//2, screen_height//2-100, center=True)
        draw_text(f"Ваш счет: {score}", font, WHITE, screen, screen_width//2, screen_height//2-30, center=True)
        draw_text(f"Достигнут уровень: {level}", small_font, WHITE, screen, screen_width//2, screen_height//2+5, center=True)
        draw_text(f"(Сложность: {difficulty_level.upper()})", small_font, GREY, screen, screen_width//2, screen_height//2+35, center=True)
        draw_text("Нажмите R для перезапуска", font, YELLOW, screen, screen_width//2, screen_height//2+80, center=True)
        draw_text("Нажмите M для возврата в меню", font, YELLOW, screen, screen_width//2, screen_height//2+120, center=True)
        draw_text("Нажмите ESC для выхода", font, YELLOW, screen, screen_width//2, screen_height//2+160, center=True)

    # --- Состояние: OUTRO ---
    elif game_state == "OUTRO":
        if sound_enabled and pygame.mixer.music.get_busy():
             pygame.mixer.music.fadeout(500)

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_m:
                     if menu_change_sound:
                         try: menu_change_sound.play()
                         except Exception as e: print(f"Ошибка звука menu_change: {e}")
                     game_state = "INTRO"

        screen.fill(BLACK)
        if outro_background: screen.blit(outro_background, (0,0))
        else: draw_text("Спасибо за игру!", pygame.font.Font(None, 64), WHITE, screen, screen_width//2, screen_height//2-50, center=True)
        draw_text(f"Финальный счет: {score}", font, WHITE, screen, screen_width//2, screen_height//2+50, center=True)
        draw_text("Нажмите ESC для выхода", font, YELLOW, screen, screen_width//2, screen_height-100, center=True)
        draw_text("Нажмите M для возврата в меню", small_font, GREY, screen, screen_width//2, screen_height-60, center=True)
        try: copyright_surface=copyright_font.render(copyright_text,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(screen_width-10,screen_height-5)); screen.blit(copyright_surface,copyright_rect)
        except Exception as e: print(f"Ошибка копирайта (аутро): {e}")

    # --- Обновление экрана ---
    pygame.display.flip()

    # --- Контроль FPS ---
    clock.tick(FPS)

# --- Завершение Pygame ---
if sound_enabled: try: pygame.mixer.music.stop() except: pass
pygame.quit()
sys.exit()