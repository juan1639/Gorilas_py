import pygame
import random
import math
from class_sonidos import Sonidos
from constants import *
from functions import build_city, cargar_img, draw_wind_flag, draw_centered, draw_gorilla, draw_banana, draw_explosion, circle_hits_rect

# ========================================================
class Game:
    def __init__(self):
        self.sonidos = Sonidos()
        self.flag_fight_text = False
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

        self.sonidos.reproducir("fight")
        self.flag_fight_text = False
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
                self.sonidos.reproducir("explosion")
                self.explode(point)
                return
            
        if self.city.get_at(point)[3] > 0:
            self.sonidos.reproducir("explosion")
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
            self.sonidos.reproducir("aplausos")
        
        self.timer = 0.0
        self.phase = "round_over"

    # ------------------------------------------------
    def update(self, dt):
        if self.phase == "angle" or self.phase == "speed":
            self.timer += dt

            if self.timer >= FIGHT_TEXT_TIME:
                self.timer = 0.0
                self.flag_fight_text = True
        
        elif self.phase == "flying":
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
                    self.sonidos.reproducir("fireworks")
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

        if not self.flag_fight_text:
            draw_centered(surface, pygame.font.Font(None, 96), " Fight! ", HEIGHT // 3, P2_COLOR)

        if self.phase == "angle":
            draw_centered(surface, font, f"Jugador {self.current + 1}: introduce el ángulo (0-90) y pulsa Enter", 150, ACTIVE_COLOR)
        elif self.phase == "speed":
            draw_centered(surface, font, f"Jugador {self.current + 1}: introduce la velocidad (1-100) y pulsa Enter", 150, ACTIVE_COLOR)
        
        if self.message:
            draw_centered(surface, font, self.message, 180, FLAG_COLOR)
        
        if self.phase == "round_over":
            draw_centered(surface, big_font, self.round_text, HEIGHT // 2 - 40)
        elif self.phase == "match_over":
            pygame.draw.rect(surface, BLACK_COLOR, (WIDTH // 2 - WIDTH // 3, HEIGHT // 2 - HEIGHT // 4, WIDTH // 1.5, HEIGHT // 2))
            draw_centered(surface, big_font, f"¡Jugador {self.round_winner + 1} gana la partida!", HEIGHT // 2 - 50)
            draw_centered(surface, font, f"Marcador final:  {self.scores[0]} - {self.scores[1]}", HEIGHT // 2)
            draw_centered(surface, font, "Espacio para jugar de nuevo", HEIGHT // 2 + 35)




