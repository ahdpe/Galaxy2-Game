# game_logic.py
import random
import math
from settings import * # Импортируем все настройки
from game_objects import Enemy # Нужен класс Enemy

# Глобальные переменные состояния игры, которые изменяются этими функциями
# Их придется передавать как параметры или использовать более сложную структуру (например, класс Game)
# Пока оставим их в main.py и будем передавать/возвращать

def get_wave_composition(current_level):
    # Логика расчета состава волны (без изменений)
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

def spawn_enemies(current_level, images): # Принимает images
    """Создает список объектов Enemy для нового уровня."""
    new_enemies = [] # Создаем новый список
    # enemy_direction = 1 # Убрали - направление теперь по типам в main.py
    composition, rows, cols = get_wave_composition(current_level)
    enemy_pool = []; max_enemy_width_in_wave = 0
    for type, count in composition.items(): enemy_pool.extend([type] * count)
    random.shuffle(enemy_pool)

    if enemy_pool:
        try: max_enemy_width_in_wave=max(ENEMY_STATS[etype]['size'][0] for etype in set(enemy_pool))
        except KeyError: max_enemy_width_in_wave = ENEMY_BASIC_SIZE[0] # Используем константу
    if max_enemy_width_in_wave == 0: max_enemy_width_in_wave = ENEMY_BASIC_SIZE[0]

    grid_width=(cols-1)*ENEMY_X_GAP+max_enemy_width_in_wave
    current_spawn_x_start=max(10,(SCREEN_WIDTH-grid_width)//2)
    enemy_index=0
    for row in range(rows):
        for col in range(cols):
            if enemy_index<len(enemy_pool):
                enemy_type=enemy_pool[enemy_index]
                enemy_stats=ENEMY_STATS[enemy_type]
                cell_center_x=current_spawn_x_start+col*ENEMY_X_GAP+max_enemy_width_in_wave//2
                enemy_x=cell_center_x-enemy_stats['size'][0]//2
                enemy_y=ENEMY_SPAWN_Y_START+row*ENEMY_Y_GAP
                # Создаем врага, передавая images
                new_enemies.append(Enemy(enemy_x, enemy_y, enemy_type, images))
                enemy_index+=1
            else: break
    # return new_enemies, enemy_direction # ИЗМЕНЕНО: Возвращаем только список
    return new_enemies # ИЗМЕНЕНО: Возвращаем только список

def update_difficulty(current_level, difficulty_level):
    """Рассчитывает и возвращает текущую скорость и задержку стрельбы."""
    base_sp=min(BASE_ENEMY_SPEED+(current_level-1)*0.15, 6.0)
    base_sh_delay=max(BASE_ENEMY_SHOOT_DELAY-(current_level-1)*60, 350)
    diff_mods=DIFFICULTY_SETTINGS[difficulty_level]
    current_enemy_speed=base_sp*diff_mods["speed_mult"]
    current_enemy_shoot_delay=base_sh_delay*diff_mods["shoot_delay_mult"]
    return current_enemy_speed, current_enemy_shoot_delay

def spawn_powerup(x, y, powerups_list): # Принимает список бонусов и модифицирует его
    """Добавляет бонус в список, если возможно."""
    if len(powerups_list) < 3:
        powerup_type = random.choice(POWERUP_TYPES)
        powerup_rect = pygame.Rect(x - POWERUP_WIDTH // 2, y, POWERUP_WIDTH, POWERUP_HEIGHT)
        powerups_list.append([powerup_rect, powerup_type]) # Модифицируем переданный список