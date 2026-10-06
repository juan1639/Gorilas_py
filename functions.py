import pygame
import os
import sys
import math
import random
from constants import *

# ========================================================
#   DECLARE FUNCTIONS
# 
# ========================================================
def build_city():
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    buildings = []
    x = 0

    while x < WIDTH:
        w = random.randint(BUILDING_MIN_W, BUILDING_MAX_W)

        if WIDTH - (x + w) < BUILDING_MIN_W:
            w = WIDTH - x
        
        h = random.randint(BUILDING_MIN_H, BUILDING_MAX_H)
        rect = pygame.Rect(x, HEIGHT - h, w, h)
        draw_building(surface, rect, random.choice(BUILDING_COLORS))
        buildings.append(rect)
        x += w
    
    pygame.draw.rect(surface, ARLEKIN_COLOR, (WIDTH // 2 - ARLEKIN_W // 2, HEIGHT - ARLEKIN_H, ARLEKIN_W, ARLEKIN_H))
    draw_centered(surface, pygame.font.Font(None, 32), " Cafetería ", HEIGHT - ARLEKIN_H + 20, ARLEKIN_COLOR_FONT)
    draw_centered(surface, pygame.font.Font(None, 32), " A R L E K Í N ", HEIGHT - ARLEKIN_H + 46, ARLEKIN_COLOR_FONT)

    return surface, buildings

# ========================================================
def draw_building(surface, rect, color):
    pygame.draw.rect(surface, color, rect)

    for wx in range(rect.left + 8, rect.right - 14, 18):
        for wy in range(rect.top + 10, HEIGHT - 20, 24):
            lit = random.random() < 0.6
            pygame.draw.rect(surface, WINDOW_ON if lit else WINDOW_OFF, (wx, wy, 8, 12))

# ========================================================
def cargar_img(img_to_load, size_x, size_y):
    # Carga la imagen (asegúrate de que el archivo esté en la misma carpeta o ruta correcta)
    imagen_original = pygame.image.load(resource_path(img_to_load)).convert_alpha()
    
    # Redimensiona la imagen para que quepa exactamente en el rectángulo de tu sprite
    image = pygame.transform.scale(imagen_original, (size_x, size_y))
    image.set_colorkey((5, 5, 5))

    return image

# ========================================================
def draw_gorilla(surface, sprite):
    #print(f"Gorila_rect: {sprite[1]}")
    surface.blit(sprite[0], sprite[1])

# ========================================================
def draw_banana(surface, pos, t):
    angle = t * 10
    c, s = math.cos(angle), math.sin(angle)
    points = []
    for px, py in ((-9, -3), (9, -3), (9, 3), (-9, 3)):
        points.append((pos[0] + px * c - py * s, pos[1] + px * s + py * c))
    pygame.draw.polygon(surface, BANANA_COLOR, points)

# ========================================================
def draw_explosion(surface, pos, progress):
    radius = max(1, int(CRATER_R * 1.6 * progress))
    pygame.draw.circle(surface, (255, 140, 30), pos, radius)
    pygame.draw.circle(surface, (255, 230, 120), pos, max(1, radius // 2))

# ========================================================
def draw_wind_flag(surface, font, wind):
    pole_x = WIDTH // 2
    top = 62
    pygame.draw.line(surface, TEXT_COLOR, (pole_x, top), (pole_x, top + 45), 2)
    direction = 1 if wind > 0 else -1
    length = 8 + abs(wind) * 7
    pygame.draw.polygon(
        surface,
        FLAG_COLOR,
        [(pole_x, top), (pole_x, top + 14), (pole_x + direction * length, top + 7)],
    )
    label = font.render(f"Viento: {abs(wind)}", True, DIM_COLOR)
    surface.blit(label, label.get_rect(midtop=(pole_x, top + 48)))

# ========================================================
def circle_hits_rect(center, radius, rect):
    # Convert simple tuple in pygame.rect:
    g_rect = pygame.Rect(rect[1][0], rect[1][1], GORILLA_W, GORILLA_H)

    cx = max(g_rect.left, min(center[0], g_rect.right))
    cy = max(g_rect.top, min(center[1], g_rect.bottom))
    return (center[0] - cx) ** 2 + (center[1] - cy) ** 2 <= radius ** 2

# ========================================================
def draw_centered(surface, font, text, y, color=TEXT_COLOR):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(center=(WIDTH // 2, y)))

# ========================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



