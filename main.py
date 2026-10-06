# ========================================================
#                       G O R I L A S 
# 
#                    By Juan Eguia, 2026
#  
# ========================================================
import pygame
import sys
from constants import *
from class_game import Game

# ========================================================
#   MAIN FUNCTION
#  
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



