"""
Initialisation et gestion du matériel
"""

import board
import neopixel
import digitalio
from config import Config

class Hardware:
    def __init__(self):
        self.pixels = None
        self.button = None
        self.initialize()
    
    def initialize(self):
        """Initialise tous les composants matériels"""
        self.initialize_neopixel()
        self.initialize_button()
    
    def initialize_neopixel(self):
        """Initialise la matrice NeoPixel"""
        self.pixels = neopixel.NeoPixel(
            getattr(board, f"GP{Config.MATRICE_PIN}"),
            Config.MATRICE_LEDS,
            brightness=Config.MATRICE_LUMINOSITE,
            auto_write=False,
            pixel_order=neopixel.GRB
        )
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
    
    def initialize_button(self):
        """Initialise le bouton poussoir"""
        self.button = digitalio.DigitalInOut(getattr(board, f"GP{Config.BOUTON_PIN}"))
        self.button.direction = digitalio.Direction.INPUT
        if Config.BOUTON_PULLDOWN:
            self.button.pull = digitalio.Pull.DOWN
    
    def get_button_state(self):
        """Retourne l'état actuel du bouton"""
        return self.button.value if self.button else False
    
    def cleanup(self):
        """Nettoie les ressources matérielles"""
        if self.pixels:
            self.pixels.fill((0, 0, 0))
            self.pixels.show()