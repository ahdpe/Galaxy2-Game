# assets.py
import pygame
import sys
import os
from settings import * # Импортируем все константы имен файлов и размеров

def _get_asset_path(filename):
    """Вспомогательная функция для поиска пути к файлу."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        filepath = filename # Пробуем без base_path
    if not os.path.exists(filepath):
        raise pygame.error(f"Файл не найден: {filename}")
    return filepath

def load_image(filename, size=None, use_colorkey=False, colorkey_color=BLACK):
    """Загружает изображение."""
    try:
        filepath = _get_asset_path(filename)
        try: image = pygame.image.load(filepath)
        except pygame.error as load_error: print(f"Ошибка Pygame {filename}: {load_error}"); return None

        if image.get_alpha() is None and not use_colorkey: image = image.convert()
        elif use_colorkey: image = image.convert(); image.set_colorkey(colorkey_color)
        else: image = image.convert_alpha()

        if size: image = pygame.transform.scale(image, size)
        return image
    except Exception as e: print(f"Не удалось загрузить/обработать: {filename}. Ошибка: {e}"); return None

def load_sound(filename, sound_enabled_flag):
    """Загружает звук, если звук включен."""
    if not sound_enabled_flag: return None
    try:
        filepath = _get_asset_path(filename)
        sound = pygame.mixer.Sound(filepath)
        return sound
    except pygame.error as e: print(f"Не удалось загрузить звук: {filename}. Ошибка: {e}"); return None

def load_all_assets(sound_enabled_flag):
    """Загружает все игровые ассеты и возвращает словари."""
    images = {
        'player': load_image(IMG_PLAYER, (PLAYER_WIDTH, PLAYER_HEIGHT)),
        'bullet': load_image(IMG_BULLET, (BULLET_WIDTH, BULLET_HEIGHT)),
        'enemy_bullet': load_image(IMG_ENEMY_BULLET, (ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT)),
        'game_bg': load_image(IMG_GAME_BG, (SCREEN_WIDTH, SCREEN_HEIGHT)),
        'shield_powerup': load_image(IMG_SHIELD_POWERUP, (POWERUP_WIDTH, POWERUP_HEIGHT)),
        'gun_powerup': load_image(IMG_GUN_POWERUP, (POWERUP_WIDTH, POWERUP_HEIGHT)),
        'shield_active': load_image(IMG_SHIELD_ACTIVE, SHIELD_ACTIVE_SIZE),
        'basic': load_image(IMG_ENEMY_BASIC, ENEMY_BASIC_SIZE), # Используем ключи из ENEMY_STATS
        'tank': load_image(IMG_ENEMY_TANK, ENEMY_TANK_SIZE),
        'shooter': load_image(IMG_ENEMY_SHOOTER, ENEMY_SHOOTER_SIZE),
        'intro_bg': load_image(IMG_INTRO_BG, (SCREEN_WIDTH, SCREEN_HEIGHT)),
        'outro_bg': load_image(IMG_OUTRO_BG, (SCREEN_WIDTH, SCREEN_HEIGHT)),
    }
    sounds = {
        'shoot': load_sound(SND_SHOOT, sound_enabled_flag),
        'explosion': load_sound(SND_EXPLOSION, sound_enabled_flag),
        'player_hit': load_sound(SND_PLAYER_HIT, sound_enabled_flag),
        'powerup': load_sound(SND_POWERUP, sound_enabled_flag),
        'enemy_hit': load_sound(SND_ENEMY_HIT, sound_enabled_flag),
        'menu_change': load_sound(SND_MENU_CHANGE, sound_enabled_flag),
        'menu_select': load_sound(SND_MENU_SELECT, sound_enabled_flag),
    }
    # Загрузка музыки отдельно в main.py
    return images, sounds

def play_sound(sound_obj):
    """Безопасно проигрывает звук."""
    if sound_obj:
        try:
            sound_obj.play()
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")