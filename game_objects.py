# game_objects.py
import pygame
from settings import ENEMY_STATS, RED # Нужны статы и цвет для отрисовки

class Enemy:
    def __init__(self, x, y, enemy_type, images): # Передаем словарь images
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]
        self.width, self.height = stats['size']
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.max_health = stats['health']
        self.health = self.max_health
        self.speed_mult = stats['speed_mult']
        self.score_value = stats['score']
        # Получаем изображение из словаря по ключу, указанному в ENEMY_STATS
        self.image = images.get(stats['img_key'])
        self.color = stats['color']
        self.shoot_mod = stats['shoot_freq_mod']

    def take_damage(self, amount):
        self.health -= amount
        self.health = max(0, self.health)

    def draw(self, surface):
        img_to_draw = self.image
        if self.type == 'tank' and self.health < self.max_health:
            # Можно добавить эффект повреждений (например, слегка затемнить)
            # temp_surf = img_to_draw.copy()
            # temp_surf.fill((50, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)
            # surface.blit(temp_surf, self.rect)
            pass # Пока оставляем без эффекта

        if img_to_draw:
            surface.blit(img_to_draw, self.rect)
        else:
            # Резервная отрисовка цветом с учетом здоровья
            health_ratio = self.health / self.max_health if self.max_health > 0 else 0
            r = int(self.color[0]*health_ratio + RED[0]*(1-health_ratio))
            g = int(self.color[1]*health_ratio + RED[1]*(1-health_ratio))
            b = int(self.color[2]*health_ratio + RED[2]*(1-health_ratio))
            current_color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.rect(surface, current_color, self.rect)

    def is_alive(self):
        return self.health > 0

# Можно добавить класс Player, Bullet, Powerup в будущем