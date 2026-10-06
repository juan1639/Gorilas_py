# ========================================================
#                       G O R I L A S 
# 
#                    By Juan Eguia, 2026
#  
# ========================================================
import pygame
import math
import random
import sys
import os

# ========================================================
#   CONSTANTS
#  
# ========================================================
WIDTH = 1200
HEIGHT = 700
FPS = 60

PPM = 10
GRAVITY = 9.8 * PPM
WIND_FORCE = 0.3 * PPM
MAX_WIND = 10
ANGLE_RANGE = (0, 90)
SPEED_RANGE = (1, 100)
SUBSTEP = 1 / 240
SELF_GRACE = 0.25

ROUNDS_TO_WIN = 2
ROUND_PAUSE = 2.5
EXPLOSION_TIME = 0.5
CRATER_R = 24

BUILDING_MIN_W = 70
BUILDING_MAX_W = 110
BUILDING_MIN_H = 100
BUILDING_MAX_H = 360
#GORILLA_W = 28
GORILLA_W = 42
#GORILLA_H = 40
GORILLA_H = 60

ARLEKIN_H = 68
ARLEKIN_W = 180

SKY_COLOR = (15, 20, 55)
BUILDING_COLORS = [(110, 110, 130), (150, 80, 80), (80, 130, 140), (130, 130, 90)]
WINDOW_ON = (250, 220, 90)
WINDOW_OFF = (40, 40, 55)
GORILLA_COLORS = [(170, 110, 60), (120, 150, 210)]
BANANA_COLOR = (255, 235, 60)
TEXT_COLOR = (240, 240, 240)
ACTIVE_COLOR = (255, 235, 60)
P2_COLOR = (130, 200, 30)
DIM_COLOR = (150, 150, 170)
FLAG_COLOR = (230, 70, 70)
ARLEKIN_COLOR = (200, 201, 202)
ARLEKIN_COLOR_FONT = (160, 0, 0)

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
    imagen_original = pygame.image.load(img_to_load).convert_alpha()
    
    # Redimensiona la imagen para que quepa exactamente en el rectángulo de tu sprite
    image = pygame.transform.scale(imagen_original, (size_x, size_y))
    image.set_colorkey((5, 5, 5))

    return image

# ========================================================
def draw_gorilla(surface, sprite):
    # Reemplaza las 4 líneas de pygame.draw.rect por esta:
    print(f"Gorila_rect: {sprite[1]}")
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

# ========================================================
class Game:
    def __init__(self):
        self.sonidos = Sonidos()
        self.scores = [0, 0]
        self.round = 1
        self.new_round()

    # ------------------------------------------------
    def new_round(self):
        self.city, self.buildings = build_city()
        left = [b for b in self.buildings if b.centerx < WIDTH * 0.45]
        right = [b for b in self.buildings if b.centerx > WIDTH * 0.55]

        self.gorila_sprite = cargar_img("img/gorila_sprite.png", GORILLA_W, GORILLA_H)
        self.gorillas = []

        for b in (random.choice(left), random.choice(right)):
            cx = random.randint(b.left + GORILLA_W // 2 + 4, b.right - GORILLA_W // 2 - 4)
            gorila_rect = self.gorila_sprite.get_rect()
            gorila_rect = (cx, b.top - GORILLA_H)
            #self.gorillas.append(pygame.Rect(cx - GORILLA_W // 2, b.top - GORILLA_H, GORILLA_W, GORILLA_H))
            self.gorillas.append((self.gorila_sprite, gorila_rect))
        
        self.wind = random.choice([w for w in range(-MAX_WIND, MAX_WIND + 1) if w != 0])
        self.hits = []
        self.fields = [["", ""], ["", ""]]
        self.message = ""
        self.round_text = ""
        self.round_winner = None
        self.timer = 0.0
        self.current = (self.round - 1) % 2
        self.phase = "angle"

    # ------------------------------------------------
    def end_turn(self):
        self.current = 1 - self.current
        self.fields[self.current] = ["", ""]
        self.message = ""
        self.phase = "angle"

    # ------------------------------------------------
    def handle_key(self, event):
        if self.phase == "match_over":
            if event.key == pygame.K_SPACE:
                self.__init__()
            return
        
        if self.phase not in ("angle", "speed"):
            return
        
        idx = 0 if self.phase == "angle" else 1
        text = self.fields[self.current][idx]

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.sonidos.reproducir("key")
            self.submit(idx)
        
        elif event.key == pygame.K_BACKSPACE:
            self.sonidos.reproducir("numkey")
            self.fields[self.current][idx] = text[:-1]
        
        elif len(event.unicode) == 1 and event.unicode in "0123456789" and len(text) < 3:
            self.sonidos.reproducir("numkey")
            self.fields[self.current][idx] = text + event.unicode

    # ------------------------------------------------
    def submit(self, idx):
        text = self.fields[self.current][idx]

        if not text:
            return
        
        lo, hi = ANGLE_RANGE if idx == 0 else SPEED_RANGE
        value = int(text)

        if not lo <= value <= hi:
            self.message = f"Introduce un valor entre {lo} y {hi}"
            self.fields[self.current][idx] = ""
            return
        
        self.message = ""

        if idx == 0:
            self.phase = "speed"
        else:
            self.launch()

    # ------------------------------------------------
    def launch(self):
        angle = math.radians(int(self.fields[self.current][0]))
        speed = int(self.fields[self.current][1])
        gorilla = self.gorillas[self.current]
        direction = 1 if self.current == 0 else -1
        #self.bx = float(gorilla[1][0].centerx)
        self.bx = float(gorilla[1][0])
        self.by = float(gorilla[1][1])
        self.bvx = direction * speed * math.cos(angle) * PPM
        self.bvy = -speed * math.sin(angle) * PPM
        self.btime = 0.0
        self.phase = "flying"

    # ------------------------------------------------
    def step_banana(self, dt):
        remaining = dt

        while remaining > 0 and self.phase == "flying":
            h = min(SUBSTEP, remaining)
            remaining -= h
            self.bvx += self.wind * WIND_FORCE * h
            self.bvy += GRAVITY * h
            self.bx += self.bvx * h
            self.by += self.bvy * h
            self.btime += h
            self.check_banana()

    # ------------------------------------------------
    def check_banana(self):
        if self.bx < 0 or self.bx >= WIDTH or self.by >= HEIGHT:
            self.end_turn()
            return
        
        if self.by < 0:
            return
        
        point = (int(self.bx), int(self.by))

        for i, gorilla in enumerate(self.gorillas):
            # Convert simple tuple in pygame.rect:
            gorilla_rect = pygame.Rect(gorilla[1][0], gorilla[1][1], GORILLA_W, GORILLA_H)

            if i == self.current and self.btime < SELF_GRACE:
                continue

            if gorilla_rect.collidepoint(point):
                self.explode(point)
                return
            
        if self.city.get_at(point)[3] > 0:
            self.explode(point)

    # ------------------------------------------------
    def explode(self, point):
        pygame.draw.circle(self.city, (0, 0, 0, 0), point, CRATER_R)
        self.explosion_pos = point
        self.hits = [i for i, g in enumerate(self.gorillas) if circle_hits_rect(point, CRATER_R, g)]
        self.timer = 0.0
        self.phase = "exploding"

    # ------------------------------------------------
    def finish_explosion(self):
        if not self.hits:
            self.end_turn()
            return
        
        if len(self.hits) == 2:
            self.round_winner = None
            self.round_text = "Empate: se repite la ronda"
        else:
            self.round_winner = 1 - self.hits[0]
            self.scores[self.round_winner] += 1
            self.round_text = f"Jugador {self.round_winner + 1} gana la ronda"
        
        self.timer = 0.0
        self.phase = "round_over"

    # ------------------------------------------------
    def update(self, dt):
        if self.phase == "flying":
            self.step_banana(dt)
        
        elif self.phase == "exploding":
            self.timer += dt

            if self.timer >= EXPLOSION_TIME:
                self.finish_explosion()
        
        elif self.phase == "round_over":
            self.timer += dt

            if self.timer >= ROUND_PAUSE:
                if self.round_winner is None:
                    self.new_round()
                elif self.scores[self.round_winner] >= ROUNDS_TO_WIN:
                    self.phase = "match_over"
                else:
                    self.round += 1
                    self.new_round()

    # ------------------------------------------------
    def draw_player_panel(self, surface, font, player):
        active = player == self.current and self.phase in ("angle", "speed")
        color = ACTIVE_COLOR if player == self.current else DIM_COLOR
        blink = (pygame.time.get_ticks() // 400) % 2 == 0
        lines = [f"Jugador {player + 1}"]

        for idx, label in enumerate(("Ángulo", "Velocidad")):
            value = self.fields[player][idx]
            editing = active and ((self.phase == "angle") == (idx == 0))
            cursor = "_" if editing and blink else ""
            lines.append(f"{label}: {value}{cursor}")
        
        for i, line in enumerate(lines):
            img = font.render(line, True, color)

            if player == 0:
                surface.blit(img, (15, 10 + i * 24))
            else:
                surface.blit(img, img.get_rect(topright=(WIDTH - 20, 10 + i * 24)))

    # ------------------------------------------------
    def draw(self, surface, font, big_font):
        surface.fill(SKY_COLOR)
        surface.blit(self.city, (0, 0))

        for i, gorilla in enumerate(self.gorillas):
            if i not in self.hits:
                #draw_gorilla(surface, gorilla, GORILLA_COLORS[i])
                draw_gorilla(surface, gorilla)
        
        if self.phase == "flying" and self.by > -200:
            draw_banana(surface, (self.bx, self.by), self.btime)
        
        if self.phase == "exploding":
            draw_explosion(surface, self.explosion_pos, self.timer / EXPLOSION_TIME)

        draw_wind_flag(surface, font, self.wind)
        self.draw_player_panel(surface, font, 0)
        self.draw_player_panel(surface, font, 1)
        score = f"[ Ronda {self.round} ]    Jugador_1  [ {self.scores[0]} - {self.scores[1]} ]  Jugador_2"
        draw_centered(surface, font, score, 18)

        if self.phase == "angle":
            draw_centered(surface, font, f"Jugador {self.current + 1}: introduce el ángulo (0-90) y pulsa Enter", 150, ACTIVE_COLOR)
        elif self.phase == "speed":
            draw_centered(surface, font, f"Jugador {self.current + 1}: introduce la velocidad (1-100) y pulsa Enter", 150, ACTIVE_COLOR)
        
        if self.message:
            draw_centered(surface, font, self.message, 180, FLAG_COLOR)
        
        if self.phase == "round_over":
            draw_centered(surface, big_font, self.round_text, HEIGHT // 2 - 40)
        elif self.phase == "match_over":
            draw_centered(surface, big_font, f"¡Jugador {self.round_winner + 1} gana la partida!", HEIGHT // 2 - 50)
            draw_centered(surface, font, f"Marcador final: {self.scores[0]} - {self.scores[1]}", HEIGHT // 2)
            draw_centered(surface, font, "Espacio para jugar de nuevo", HEIGHT // 2 + 35)

# ====================================================================================
class Sonidos:
    """Funcion constructora"""
    def __init__(self):
        pygame.mixer.init()
        self.sonidos = self.cargar_sonidos()
    
    # -------------------------------------------------------------------------
    def cargar_sonidos(self):
        """Cargar todos los sonidos en un diccionario."""
        return {
            "aplausos": self.cargar_sonido(resource_path("audio/aplausoseagle.mp3"), 0.6),
            "fireworks": self.cargar_sonido(resource_path("audio/fireworks.mp3"), 0.5),
            "head-shot": self.cargar_sonido(resource_path("audio/head-shot.mp3"), 0.7),
            "key": self.cargar_sonido(resource_path("audio/key.wav"), 0.8),
            "numkey": self.cargar_sonido(resource_path("audio/numkey.wav"), 0.8),
            "explosion": self.cargar_sonido(resource_path("audio/sonido-explo-granada.mp3"), 0.7)
        }
    
    # -------------------------------------------------------------------------
    def cargar_sonido(self, ruta, volumen=1.0):
        """Carga un sonido específico con el volumen indicado."""
        sonido = pygame.mixer.Sound(ruta)
        sonido.set_volume(volumen)
        return sonido
    
    # -------------------------------------------------------------------------
    def reproducir(self, nombre, duracion=None):
        """Reproduce un sonido si está en el diccionario."""
        if nombre in self.sonidos:
            if duracion == None:
                self.sonidos[nombre].play()
            else:
                self.sonidos[nombre].play(maxtime=duracion)

# ========================================================
#   MAIN FUNCTION
# ========================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gorillas_py  |  By Juan Eguia, 2026")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    big_font = pygame.font.Font(None, 64)

    game = Game()

    # Set running=True to 'while' until running=False:
    running = True

    # ===========================================
    #   MAIN LOOP
    # ===========================================
    while running:
        dt = min(clock.tick(FPS) / 1000, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event)
        
        game.update(dt)
        game.draw(screen, font, big_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ========================================================
#   Init game  ( invoke game() function )
# ========================================================
if __name__ == "__main__":
    main()




