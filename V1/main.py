# main.py
import pygame
import random
import sys
import os
import math

# --- Импорт из других модулей ---
from settings import *
import assets
import game_objects
import game_logic
import drawing

# --- Инициализация Pygame и Микшера ---
pygame.init()
sound_enabled = False
try:
    pygame.mixer.init()
    sound_enabled = True
    print("Микшер звука инициализирован.")
except pygame.error as e:
    print(f"Не удалось инициализировать микшер звука: {e}. Звук будет отключен.")

# --- Экран ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Улучшенная Галактика (Модульная - от Andrei Osipov)")
clock = pygame.time.Clock()

# --- Загрузка Ассетов ---
images, sounds = assets.load_all_assets(sound_enabled)
# ... (проверки фонов без изменений) ...
if images.get('intro_bg') is None: print("ПРЕДУПРЕЖДЕНИЕ: Файл intro_background.png не найден или не удалось загрузить.")
if images.get('outro_bg') is None: print("ПРЕДУПРЕЖДЕНИЕ: Файл outro_background.png не найден или не удалось загрузить (проверьте формат!).")
if images.get('game_bg') is None: print("ПРЕДУПРЕЖДЕНИЕ: Файл background.jpg не найден или не удалось загрузить.")


# --- Шрифты ---
# ... (без изменений) ...
try:
    font_normal = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, 24)
    font_copyright = pygame.font.Font(None, 18); font_large = pygame.font.Font(None, 60)
    font_xlarge = pygame.font.Font(None, 74); copyright_color = GREY
except Exception as e:
    print(f"Ошибка загрузки шрифтов: {e}")
    font_normal = pygame.font.SysFont(None, 36); font_small = pygame.font.SysFont(None, 24)
    font_copyright = pygame.font.SysFont(None, 18); font_large = pygame.font.SysFont(None, 60)
    font_xlarge = pygame.font.SysFont(None, 74); copyright_color = (150, 150, 150)


# --- Игровые переменные ---
# ... (остальные переменные без изменений) ...
game_state = "INTRO"; running = True; paused = False
player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
player_lives = PLAYER_LIVES_START; player_shield_active = False; player_shield_timer = 0
rapid_fire_active = False; rapid_fire_timer = 0; current_shoot_delay = BASE_SHOOT_DELAY
can_shoot = True; shoot_timer = 0
enemies = []; bullets = []; enemy_bullets = []; powerups = []; effects = []
enemy_speed = BASE_ENEMY_SPEED; enemy_shoot_delay = BASE_ENEMY_SHOOT_DELAY
enemy_directions_by_type = {}; last_enemy_shot_time = 0; score = 0; level = 1
level_start_display_time = 0; enemy_x_remainders = {}
current_music_track = None # <<< НОВОЕ: Отслеживание текущего музыкального файла

# --- Настройки сложности и меню ---
# ... (без изменений) ...
difficulty_level = "medium"
try: selected_difficulty_index = difficulty_levels.index(difficulty_level)
except ValueError: print(f"ПРЕДУПРЕЖДЕНИЕ: Сложность '{difficulty_level}' не найдена. Установлена первая."); selected_difficulty_index = 0; difficulty_level = difficulty_levels[0]
except NameError: print("КРИТИЧЕСКАЯ ОШИБКА: difficulty_levels не импортирован!"); pygame.quit(); sys.exit()

# Фон (звезды для геймплея)
# ... (без изменений) ...
stars_game = []
for _ in range(NUM_STARS): x = random.randrange(0, SCREEN_WIDTH); y = random.randrange(0, SCREEN_HEIGHT); sp = random.choice([1, 2, 3]); sz = sp; br = 100 + 50 * sp; cl = (br, br, br); stars_game.append([x, y, sp, sz, cl])

# --- Функция создания эффекта ---
# ... (без изменений) ...
def create_effect(effect_type, position):
    now = pygame.time.get_ticks()
    if effect_type == 'spark':
        for _ in range(SPARK_COUNT): effects.append({'type': 'spark','pos': position,'start_time': now,'duration': SPARK_DURATION,'offset': (random.uniform(-5, 5), random.uniform(-5, 5)),'radius': random.randint(SPARK_RADIUS_MIN, SPARK_RADIUS_MAX)})
    elif effect_type == 'explosion': effects.append({'type': 'explosion','pos': position,'start_time': now,'duration': EXPLOSION_DURATION})


# --- НОВЫЕ: Вспомогательные функции для музыки ---
def stop_music(fade_duration=500):
    """Останавливает или плавно заглушает текущую музыку."""
    global current_music_track
    if sound_enabled and pygame.mixer.music.get_busy():
        if fade_duration > 0:
            pygame.mixer.music.fadeout(fade_duration)
        else:
            pygame.mixer.music.stop()
    current_music_track = None # Сбрасываем текущий трек

def play_music(track_filename, volume=1.0, loops=-1, fade_in_ms=0):
    """Загружает и проигрывает музыкальный трек, если он еще не играет."""
    global current_music_track
    if not sound_enabled:
        return
    # Проверяем, не играет ли уже этот трек
    if current_music_track == track_filename and pygame.mixer.music.get_busy():
        return # Уже играет, ничего не делаем

    # Если играет что-то другое, останавливаем плавно
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(300) # Короткое затухание перед сменой

    try:
        filepath = assets._get_asset_path(track_filename)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loops, fade_ms=fade_in_ms)
        current_music_track = track_filename # Обновляем текущий трек
        print(f"Playing music: {track_filename}")
    except Exception as e:
        print(f"Error playing music {track_filename}: {e}")
        current_music_track = None # Сбрасываем при ошибке

# --- Сброс игры (Функция) ---
def reset_game():
    global player_rect, player_lives, level, score, enemies, enemy_directions_by_type
    global bullets, enemy_bullets, powerups, paused, can_shoot, shoot_timer
    global player_shield_active, rapid_fire_active, current_shoot_delay, last_enemy_shot_time
    global enemy_speed, enemy_shoot_delay, level_start_display_time
    global enemy_x_remainders, effects # <<< Доступ к effects нужен

    # ... (остальные сбросы без изменений) ...
    player_rect.topleft = (PLAYER_START_X, PLAYER_START_Y); player_lives = PLAYER_LIVES_START
    level = 1; score = 0
    enemy_speed, enemy_shoot_delay = game_logic.update_difficulty(level, difficulty_level)
    enemies = game_logic.spawn_enemies(level, images); enemy_directions_by_type.clear()
    for e_type in ENEMY_STATS.keys(): enemy_directions_by_type[e_type] = 1
    enemy_x_remainders.clear(); bullets.clear(); enemy_bullets.clear(); powerups.clear(); effects.clear()
    paused = False; can_shoot = True; shoot_timer = 0
    player_shield_active = False; rapid_fire_active = False; current_shoot_delay = BASE_SHOOT_DELAY
    last_enemy_shot_time = pygame.time.get_ticks() + 1500; level_start_display_time = pygame.time.get_ticks()

    # --- ИЗМЕНЕНО: Используем новую функцию для игровой музыки ---
    play_music(MUS_BACKGROUND, volume=0.4) # Играем фоновую музыку для игры


# --- Основной игровой цикл ---
while running:
    current_time = pygame.time.get_ticks()
    events = pygame.event.get()

    # --- Состояние: INTRO (Меню) ---
    if game_state == "INTRO":
        play_music(MUS_INTRO, volume=0.6) # <<< Запускаем музыку интро (если еще не играет)

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_difficulty_index=(selected_difficulty_index - 1)%len(difficulty_levels); assets.play_sound(sounds.get('menu_change'))
                elif event.key == pygame.K_DOWN: selected_difficulty_index=(selected_difficulty_index + 1)%len(difficulty_levels); assets.play_sound(sounds.get('menu_change'))
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    difficulty_level=difficulty_levels[selected_difficulty_index]
                    assets.play_sound(sounds.get('menu_select'))
                    # stop_music() # Плавно остановим музыку интро перед рестартом
                    reset_game()   # reset_game теперь сам запустит нужную музыку
                    game_state="PLAYING"
                elif event.key == pygame.K_ESCAPE:
                    stop_music(fade_duration=300) # Плавно выключим перед выходом
                    running = False
        # ... (отрисовка интро без изменений) ...
        screen.fill(BLACK); intro_bg_img=images.get('intro_bg');
        if intro_bg_img: screen.blit(intro_bg_img, (0,0))
        else: drawing.draw_text("Улучшенная Галактика", font_xlarge, WHITE, screen, SCREEN_WIDTH//2, 100, center=True)
        drawing.draw_text("Выберите сложность:", font_normal, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-60, center=True)
        for i, level_name in enumerate(difficulty_levels): color=HIGHLIGHT_COLOR if i==selected_difficulty_index else WHITE; drawing.draw_text(level_name.upper(), font_normal, color, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-20+i*40, center=True)
        controls_y_start=SCREEN_HEIGHT//2+80; drawing.draw_text("Управление:", font_small, WHITE, screen, 100, controls_y_start); drawing.draw_text("Стрелки Влево/Вправо - Движение", font_small, WHITE, screen, 100, controls_y_start+25); drawing.draw_text("Пробел - Стрелять", font_small, WHITE, screen, 100, controls_y_start+50); drawing.draw_text("P - Пауза", font_small, WHITE, screen, 100, controls_y_start+75); drawing.draw_text("Нажмите ENTER для старта", font_normal, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-70, center=True); drawing.draw_text("Нажмите ESC для выхода", font_small, GREY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-40, center=True);
        try: copyright_surface=font_copyright.render(COPYRIGHT_TEXT,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(SCREEN_WIDTH-10,SCREEN_HEIGHT-5)); screen.blit(copyright_surface,copyright_rect)
        except Exception as e: print(f"Ошибка копирайта (интро): {e}")


    # --- Состояние: PLAYING (Игра) ---
    elif game_state == "PLAYING":
        game_over_flag = False

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if sound_enabled:
                        if paused: pygame.mixer.music.pause() # Пауза/возобновление игровой музыки
                        else: pygame.mixer.music.unpause()
                elif not paused and event.key == pygame.K_SPACE and can_shoot:
                    bullets.append(pygame.Rect(player_rect.centerx-BULLET_WIDTH//2,player_rect.top,BULLET_WIDTH,BULLET_HEIGHT)); assets.play_sound(sounds.get('shoot')); can_shoot=False; shoot_timer=current_time

        if paused:
            # ... (отрисовка паузы без изменений) ...
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0)); drawing.draw_text("ПАУЗА", font_xlarge, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-50, center=True); drawing.draw_text("Нажмите P чтобы продолжить", font_normal, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+20, center=True);
            try: copyright_surface=font_copyright.render(COPYRIGHT_TEXT,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(SCREEN_WIDTH-10,SCREEN_HEIGHT-5)); screen.blit(copyright_surface,copyright_rect)
            except Exception as e: print(f"Ошибка копирайта (пауза): {e}")
            pygame.display.flip(); clock.tick(FPS); continue

        # --- Основная игровая логика ---
        # ... (логика движения, стрельбы, эффектов, столкновений БЕЗ ИЗМЕНЕНИЙ) ...
        for star in stars_game: star[1]+=star[2]; star[0]=random.randrange(0,SCREEN_WIDTH) if star[1]>SCREEN_HEIGHT else star[0]; star[1]=random.randrange(-20,0) if star[1]>SCREEN_HEIGHT else star[1]
        keys=pygame.key.get_pressed(); player_rect.x-=PLAYER_SPEED if keys[pygame.K_LEFT] and player_rect.left>0 else 0; player_rect.x+=PLAYER_SPEED if keys[pygame.K_RIGHT] and player_rect.right<SCREEN_WIDTH else 0
        if player_shield_active and current_time-player_shield_timer>SHIELD_DURATION: player_shield_active=False
        if rapid_fire_active and current_time-rapid_fire_timer>RAPID_FIRE_DURATION: rapid_fire_active=False; current_shoot_delay=BASE_SHOOT_DELAY
        if not can_shoot and current_time-shoot_timer>current_shoot_delay: can_shoot=True
        bullets=[b for b in bullets if b.bottom>0]; [bullet.move_ip(0,-BULLET_SPEED) for bullet in bullets]
        enemy_bullets=[b for b in enemy_bullets if b.top<SCREEN_HEIGHT]; [bullet.move_ip(0,ENEMY_BULLET_SPEED) for bullet in enemy_bullets]
        effects = [effect for effect in effects if current_time - effect['start_time'] < effect['duration']]
        move_down_flags_by_type = {e_type: False for e_type in enemy_directions_by_type}; min_max_x_by_type = {}; enemies_present_ids = {id(e) for e in enemies}
        if enemies:
            active_types = set(e.type for e in enemies)
            for e_type in active_types:
                enemies_of_type = [e for e in enemies if e.type == e_type];
                if not enemies_of_type:
                    if e_type in enemy_directions_by_type: del enemy_directions_by_type[e_type]; continue
                min_x = min(e.rect.left for e in enemies_of_type); max_x = max(e.rect.right for e in enemies_of_type); min_max_x_by_type[e_type] = {'min': min_x, 'max': max_x}; direction = enemy_directions_by_type.get(e_type, 1); step = enemy_speed * direction
                if (max_x + step > SCREEN_WIDTH and direction > 0) or (min_x + step < 0 and direction < 0): move_down_flags_by_type[e_type] = True
            types_to_reverse_after_move = set()
            for enemy in enemies:
                e_type = enemy.type; enemy_id = id(enemy)
                if e_type not in enemy_directions_by_type: continue
                y_move = 0
                if move_down_flags_by_type.get(e_type, False): y_move = ENEMY_Y_GAP // 2; types_to_reverse_after_move.add(e_type)
                direction = enemy_directions_by_type[e_type]; ideal_x_move_float = enemy_speed * enemy.speed_mult * direction; current_remainder = enemy_x_remainders.get(enemy_id, 0.0); total_potential_move = current_remainder + ideal_x_move_float; actual_x_move_int = int(total_potential_move); enemy_x_remainders[enemy_id] = total_potential_move - actual_x_move_int; enemy.rect.move_ip(actual_x_move_int, y_move)
            for e_type in types_to_reverse_after_move:
                 if e_type in enemy_directions_by_type: enemy_directions_by_type[e_type] *= -1
        if enemies and current_time-last_enemy_shot_time>enemy_shoot_delay:
             potential_shooters=[]; cols_grouped={};
             for enemy in enemies:
                 found_col=False;
                 for x_key in cols_grouped:
                     if abs(enemy.rect.centerx-x_key)<ENEMY_X_GAP/1.5: cols_grouped[x_key].append(enemy); found_col=True; break
                 if not found_col: cols_grouped[enemy.rect.centerx]=[enemy]
             [potential_shooters.append(max(col_enemies_list, key=lambda e: e.rect.bottom)) for x_col, col_enemies_list in cols_grouped.items() if col_enemies_list]
             if potential_shooters:
                 shooters=[e for e in potential_shooters if e.type=='shooter']; non_shooters=[e for e in potential_shooters if e.type!='shooter']; chosen_shooter=None
                 if shooters and random.random()<0.7: chosen_shooter=random.choice(shooters)
                 elif non_shooters: chosen_shooter=random.choice(non_shooters)
                 elif shooters: chosen_shooter=random.choice(shooters)
                 if chosen_shooter:
                    actual_shoot_delay = enemy_shoot_delay * chosen_shooter.shoot_mod
                    if current_time - last_enemy_shot_time > actual_shoot_delay * (0.8 + random.random() * 0.4):
                         bullet_x=chosen_shooter.rect.centerx-ENEMY_BULLET_WIDTH//2; bullet_y=chosen_shooter.rect.bottom; enemy_bullets.append(pygame.Rect(bullet_x,bullet_y,ENEMY_BULLET_WIDTH,ENEMY_BULLET_HEIGHT)); last_enemy_shot_time=current_time
        powerups=[p for p in powerups if p[0].top<SCREEN_HEIGHT]; [powerup[0].move_ip(0,POWERUP_SPEED) for powerup in powerups]
        enemies_destroyed_this_frame_ids = set()
        bullets_hit_indices=set(); enemies_damaged_this_frame=False
        temp_bullets = []
        for i, bullet in enumerate(bullets):
            bullet_collided = False
            possible_targets = [enemy for enemy in enemies if abs(enemy.rect.centerx - bullet.centerx) < enemy.width + BULLET_WIDTH and id(enemy) not in enemies_destroyed_this_frame_ids]
            for enemy in possible_targets:
                 enemy_id = id(enemy)
                 if enemy.is_alive() and bullet.colliderect(enemy.rect):
                    bullet_collided = True; create_effect('spark', bullet.center); enemy.take_damage(1); enemies_damaged_this_frame = True
                    if not enemy.is_alive(): create_effect('explosion', enemy.rect.center); enemies_destroyed_this_frame_ids.add(enemy_id); score_increase=int(enemy.score_value*level*DIFFICULTY_SETTINGS[difficulty_level]["score_mult"]); score+=score_increase; assets.play_sound(sounds.get('explosion'));
                    if random.random()<POWERUP_SPAWN_CHANCE: game_logic.spawn_powerup(enemy.rect.centerx,enemy.rect.centery, powerups)
                    else: assets.play_sound(sounds.get('enemy_hit'))
                    break
            if not bullet_collided: temp_bullets.append(bullet)
        bullets = temp_bullets
        enemy_bullets_to_remove_indices=set(); player_hit_this_frame=False
        for i,bullet in enumerate(enemy_bullets):
            if not player_hit_this_frame and player_rect.colliderect(bullet):
                enemy_bullets_to_remove_indices.add(i); player_hit_this_frame=True; create_effect('spark', bullet.center); assets.play_sound(sounds.get('player_hit'))
                if player_shield_active: player_shield_active=False
                else:
                    player_lives-=1
                    if player_lives <= 0: create_effect('explosion', player_rect.center); game_over_flag=True; break
                    else: player_rect.topleft=(PLAYER_START_X,PLAYER_START_Y)
        if enemy_bullets_to_remove_indices: enemy_bullets=[b for i,b in enumerate(enemy_bullets) if i not in enemy_bullets_to_remove_indices]
        if not game_over_flag:
            enemies_collided_or_reached_bottom = False; enemies_to_keep = []
            for enemy in enemies:
                enemy_id = id(enemy)
                if enemy_id in enemies_destroyed_this_frame_ids: continue
                collided_with_player = False; reached_bottom = False
                if player_rect.colliderect(enemy.rect):
                    collided_with_player = True; enemies_destroyed_this_frame_ids.add(enemy_id); assets.play_sound(sounds.get('explosion')); create_effect('explosion', enemy.rect.center)
                    if player_shield_active: player_shield_active = False; create_effect('spark', player_rect.center); score_increase = int(enemy.score_value // 2 * level * DIFFICULTY_SETTINGS[difficulty_level]["score_mult"]); score += score_increase
                    else:
                        player_lives -= 1; assets.play_sound(sounds.get('player_hit')); create_effect('explosion', player_rect.center)
                        if player_lives <= 0: game_over_flag = True; enemies_collided_or_reached_bottom = True
                        else: player_rect.topleft = (PLAYER_START_X, PLAYER_START_Y)
                elif enemy.rect.bottom >= PLAYER_START_Y: reached_bottom = True; enemies_destroyed_this_frame_ids.add(enemy_id); game_over_flag = True; player_lives = 0; enemies_collided_or_reached_bottom = True
                if not collided_with_player and not reached_bottom: enemies_to_keep.append(enemy)
                if enemies_collided_or_reached_bottom:
                    if game_over_flag:
                        for rem_enemy in enemies: enemies_destroyed_this_frame_ids.add(id(rem_enemy))
                    break
            enemies = enemies_to_keep
        for enemy_id in enemies_destroyed_this_frame_ids:
            if enemy_id in enemy_x_remainders: del enemy_x_remainders[enemy_id]
        current_enemy_ids = {id(e) for e in enemies}; keys_to_delete = set(enemy_x_remainders.keys()) - current_enemy_ids
        for key in keys_to_delete:
             if key in enemy_x_remainders: del enemy_x_remainders[key]
        powerups_collided_indices=set()
        for i,powerup in enumerate(powerups):
            powerup_rect,powerup_type=powerup
            if player_rect.colliderect(powerup_rect):
                powerups_collided_indices.add(i); assets.play_sound(sounds.get('powerup'))
                if powerup_type=='shield': player_shield_active=True; player_shield_timer=current_time
                elif powerup_type=='gun': rapid_fire_active=True; rapid_fire_timer=current_time; current_shoot_delay=RAPID_FIRE_SHOOT_DELAY
        if powerups_collided_indices: powerups=[p for i,p in enumerate(powerups) if i not in powerups_collided_indices]

        # --- Проверка победы на уровне ---
        if not game_over_flag and not enemies:
            # ... (логика смены уровня без изменений, кроме очистки эффектов) ...
            level+=1; enemy_speed, enemy_shoot_delay = game_logic.update_difficulty(level, difficulty_level); enemies = game_logic.spawn_enemies(level, images); enemy_directions_by_type.clear(); active_types_new_level = set(e.type for e in enemies)
            for e_type in active_types_new_level: enemy_directions_by_type[e_type] = 1
            enemy_x_remainders.clear(); bullets.clear(); enemy_bullets.clear(); powerups.clear(); effects.clear(); player_rect.topleft=(PLAYER_START_X, PLAYER_START_Y); last_enemy_shot_time=current_time+2000; level_start_display_time=current_time

        # --- Переход в GAME_OVER ---
        if game_over_flag:
            stop_music(fade_duration=0) # <<< Резко останавливаем игровую музыку
            game_state="GAME_OVER";
            # ... (остальные сбросы без изменений) ...
            player_shield_active=False; rapid_fire_active=False; current_shoot_delay=BASE_SHOOT_DELAY; bullets.clear(); enemy_bullets.clear(); powerups.clear(); enemies.clear(); enemy_x_remainders.clear(); effects.clear()
            continue

        # --- Отрисовка Игрового Экрана ---
        # ... (отрисовка объектов, эффектов, UI БЕЗ ИЗМЕНЕНИЙ) ...
        screen.fill(BLACK); game_bg_img = images.get('game_bg')
        if game_bg_img: screen.blit(game_bg_img,(0,0))
        else: [pygame.draw.circle(screen,star[4],(star[0],star[1]),star[3]) for star in stars_game]
        [enemy.draw(screen) for enemy in enemies]
        for effect in effects:
            time_elapsed = current_time - effect['start_time']; progress = time_elapsed / effect['duration']
            if effect['type'] == 'spark':
                spark_x = effect['pos'][0] + effect['offset'][0]; spark_y = effect['pos'][1] + effect['offset'][1]; current_radius = int(effect['radius'] * (1 - progress))
                if current_radius > 0: pygame.draw.circle(screen, ORANGE, (int(spark_x), int(spark_y)), current_radius)
            elif effect['type'] == 'explosion':
                current_radius = int(EXPLOSION_RADIUS_START + (EXPLOSION_RADIUS_END - EXPLOSION_RADIUS_START) * progress)
                r = int(EXPLOSION_COLOR_START[0] + (EXPLOSION_COLOR_END[0] - EXPLOSION_COLOR_START[0]) * progress); g = int(EXPLOSION_COLOR_START[1] + (EXPLOSION_COLOR_END[1] - EXPLOSION_COLOR_START[1]) * progress); b = int(EXPLOSION_COLOR_START[2] + (EXPLOSION_COLOR_END[2] - EXPLOSION_COLOR_START[2]) * progress); current_color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
                if current_radius > 0 : pygame.draw.circle(screen, current_color, effect['pos'], current_radius, 2);
                if current_radius > 5: pygame.draw.circle(screen, WHITE, effect['pos'], current_radius // 2, 1)
        bullet_img_asset = images.get('bullet');
        for bullet in bullets: screen.blit(bullet_img_asset, bullet) if bullet_img_asset else pygame.draw.rect(screen, RED, bullet)
        enemy_bullet_img_asset = images.get('enemy_bullet');
        for bullet in enemy_bullets: screen.blit(enemy_bullet_img_asset, bullet) if enemy_bullet_img_asset else pygame.draw.rect(screen, YELLOW, bullet)
        shield_powerup_img = images.get('shield_powerup'); gun_powerup_img = images.get('gun_powerup');
        for powerup_rect, powerup_type in powerups: img = shield_powerup_img if powerup_type == 'shield' else gun_powerup_img; color = BLUE if powerup_type == 'shield' else RED; screen.blit(img, powerup_rect) if img else pygame.draw.rect(screen, color, powerup_rect)
        player_img_asset = images.get('player'); screen.blit(player_img_asset, player_rect) if player_img_asset else pygame.draw.rect(screen, WHITE, player_rect)
        shield_active_img_asset = images.get('shield_active')
        if player_shield_active: screen.blit(shield_active_img_asset, shield_active_img_asset.get_rect(center=player_rect.center)) if shield_active_img_asset else pygame.draw.circle(screen, BLUE, player_rect.center, PLAYER_WIDTH//2+5, 2)
        drawing.draw_text(f"Счет: {score}", font_normal, WHITE, screen, 10, 10); drawing.draw_text(f"Уровень: {level}", font_normal, WHITE, screen, SCREEN_WIDTH-150, 10); drawing.draw_text(f"Сложность: {difficulty_level.upper()}", font_small, WHITE, screen, SCREEN_WIDTH-150, 40); drawing.draw_lives(screen, 10, SCREEN_HEIGHT-40, player_lives, player_img_asset, font_normal);
        if current_time-level_start_display_time<LEVEL_DISPLAY_DURATION: drawing.draw_text(f"УРОВЕНЬ {level}", font_large, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-60, center=True)
        if not paused:
            try: copyright_surface=font_copyright.render(COPYRIGHT_TEXT,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(SCREEN_WIDTH-10,SCREEN_HEIGHT-5)); screen.blit(copyright_surface,copyright_rect)
            except Exception as e: print(f"Ошибка копирайта (игра): {e}")


    # --- Состояние: GAME_OVER ---
    elif game_state == "GAME_OVER":
        # Музыку уже остановили при переходе в это состояние
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    assets.play_sound(sounds.get('menu_select'))
                    reset_game() # Запустит игровую музыку
                    game_state = "PLAYING"
                elif event.key == pygame.K_m:
                     assets.play_sound(sounds.get('menu_change'))
                     play_music(MUS_INTRO, volume=0.6) # <<< Запускаем музыку интро
                     game_state = "INTRO"
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                     assets.play_sound(sounds.get('menu_change'))
                     play_music(MUS_OUTRO, volume=0.5) # <<< Запускаем музыку аутро
                     game_state = "OUTRO"
        # ... (отрисовка Game Over без изменений) ...
        screen.fill(BLACK); game_bg_img = images.get('game_bg');
        if game_bg_img: screen.blit(game_bg_img,(0,0));
        overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,200)); screen.blit(overlay,(0,0)); drawing.draw_text("ИГРА ОКОНЧЕНА", font_xlarge, RED, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-100, center=True); drawing.draw_text(f"Ваш счет: {score}", font_normal, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30, center=True); drawing.draw_text(f"Достигнут уровень: {level}", font_small, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+5, center=True); drawing.draw_text(f"(Сложность: {difficulty_level.upper()})", font_small, GREY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+35, center=True); drawing.draw_text("Нажмите R для перезапуска", font_normal, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+80, center=True); drawing.draw_text("Нажмите M для возврата в меню", font_normal, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+120, center=True); drawing.draw_text("Нажмите ESC/Q для выхода", font_normal, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+160, center=True);
        try: copyright_surface=font_copyright.render(COPYRIGHT_TEXT,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(SCREEN_WIDTH-10,SCREEN_HEIGHT-5)); screen.blit(copyright_surface,copyright_rect)
        except Exception as e: print(f"Ошибка копирайта (Game Over): {e}")


    # --- Состояние: OUTRO ---
    elif game_state == "OUTRO":
        play_music(MUS_OUTRO, volume=0.5) # <<< Запускаем музыку аутро (если еще не играет)

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music(fade_duration=300) # <<< Плавно выключаем перед выходом
                    running = False
                elif event.key == pygame.K_m:
                     assets.play_sound(sounds.get('menu_change'))
                     # stop_music() # Можно не останавливать, play_music сама переключит
                     play_music(MUS_INTRO, volume=0.6) # <<< Запускаем музыку интро
                     game_state = "INTRO"
        # ... (отрисовка аутро без изменений) ...
        screen.fill(BLACK); outro_bg_img = images.get('outro_bg');
        if outro_bg_img: screen.blit(outro_bg_img, (0,0))
        else: drawing.draw_text("Спасибо за игру!", font_large, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-50, center=True)
        drawing.draw_text(f"Финальный счет: {score}", font_normal, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+50, center=True); drawing.draw_text("Нажмите ESC для выхода", font_normal, YELLOW, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-100, center=True); drawing.draw_text("Нажмите M для возврата в меню", font_small, GREY, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT-60, center=True);
        try: copyright_surface=font_copyright.render(COPYRIGHT_TEXT,True,copyright_color); copyright_rect=copyright_surface.get_rect(bottomright=(SCREEN_WIDTH-10,SCREEN_HEIGHT-5)); screen.blit(copyright_surface,copyright_rect)
        except Exception as e: print(f"Ошибка копирайта (аутро): {e}")


    # --- Обновление экрана ---
    pygame.display.flip()

    # --- Контроль FPS ---
    clock.tick(FPS)

# --- Завершение Pygame ---
stop_music(fade_duration=0) # <<< Останавливаем любую музыку перед выходом
if sound_enabled:
    # try: pygame.mixer.music.stop() # Уже сделано в stop_music()
    # except Exception: pass
    pass # Дополнительных действий не требуется
pygame.quit()
sys.exit()