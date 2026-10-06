import pygame
from functions import resource_path

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
            "explosion": self.cargar_sonido(resource_path("audio/sonido-explo-granada.mp3"), 0.7),
            "fight": self.cargar_sonido(resource_path("audio/fight-deep-voice.mp3"), 0.9)
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




