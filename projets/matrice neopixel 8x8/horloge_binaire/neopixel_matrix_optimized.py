"""
Module de contrôle pour matrice LED NeoPixel 8x8
Optimisé pour performances et facilité d'utilisation
"""

import board
import neopixel
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

LED_WIDTH = 8
LED_HEIGHT = 8
NUM_PIXELS = LED_WIDTH * LED_HEIGHT
LED_PIN = board.GP0
BRIGHTNESS = 0.3  # Luminosité (0.0 à 1.0) pour économiser l'énergie


# ============================================================================
# CLASSE PRINCIPALE
# ============================================================================

class NeoPixelMatrix:
    """
    Classe pour gérer une matrice LED NeoPixel.
    
    Attributes:
        width (int): Largeur de la matrice
        height (int): Hauteur de la matrice
        pixels (neopixel.NeoPixel): Objet NeoPixel
    """
    
    def __init__(self, pin, width=8, height=8, brightness=0.3):
        """
        Initialise la matrice LED.
        
        Args:
            pin: Pin GPIO du microcontrôleur
            width: Largeur de la matrice (défaut: 8)
            height: Hauteur de la matrice (défaut: 8)
            brightness: Luminosité de 0.0 à 1.0 (défaut: 0.3)
        """
        self.width = width
        self.height = height
        self.num_pixels = width * height
        self.pixels = neopixel.NeoPixel(
            pin, 
            self.num_pixels, 
            auto_write=False,
            brightness=brightness
        )
        self._buffer = [(0, 0, 0)] * self.num_pixels  # Buffer pour éviter les recalculs
    
    def get_index(self, x, y):
        """
        Convertit les coordonnées (x, y) en index de pixel.
        
        Args:
            x: Coordonnée x (0 à width-1)
            y: Coordonnée y (0 à height-1)
            
        Returns:
            Index du pixel dans la bande LED
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return y * self.width + x
        raise ValueError(f"Coordonnées hors limites: ({x}, {y})")
    
    def get_coords(self, index):
        """
        Convertit un index de pixel en coordonnées (x, y).
        
        Args:
            index: Index du pixel (0 à num_pixels-1)
            
        Returns:
            Tuple (x, y)
        """
        x = index % self.width
        y = index // self.width
        return (x, y)
    
    def set_pixel(self, x, y, color):
        """
        Définit la couleur d'un pixel spécifique.
        
        Args:
            x: Coordonnée x
            y: Coordonnée y
            color: Tuple RGB (r, g, b) avec valeurs 0-255
        """
        index = self.get_index(x, y)
        self._buffer[index] = color
        self.pixels[index] = color
    
    def fill(self, color):
        """
        Remplit toute la matrice avec une couleur.
        
        Args:
            color: Tuple RGB (r, g, b)
        """
        self._buffer = [color] * self.num_pixels
        self.pixels.fill(color)
    
    def clear(self):
        """Éteint tous les LEDs."""
        self.fill((0, 0, 0))
        self.show()
    
    def show(self):
        """Met à jour l'affichage de la matrice."""
        self.pixels.show()
    
    def draw_gradient(self, x_scale=32, y_scale=32, z_value=50):
        """
        Dessine un dégradé de couleurs basé sur les coordonnées.
        
        Args:
            x_scale: Facteur de multiplication pour la composante rouge (défaut: 32)
            y_scale: Facteur de multiplication pour la composante verte (défaut: 32)
            z_value: Valeur constante pour la composante bleue (défaut: 50)
        """
        for i in range(self.num_pixels):
            x, y = self.get_coords(i)
            # Calcul optimisé de la couleur
            color = (
                min(x * x_scale, 255),
                min(y * y_scale, 255),
                min(z_value, 255)
            )
            self._buffer[i] = color
            self.pixels[i] = color
        self.show()
    
    def draw_pattern(self, pattern_func):
        """
        Dessine un motif personnalisé en utilisant une fonction.
        
        Args:
            pattern_func: Fonction qui prend (x, y) et retourne un tuple RGB
            
        Example:
            def checker(x, y):
                return (255, 255, 255) if (x + y) % 2 == 0 else (0, 0, 0)
            matrix.draw_pattern(checker)
        """
        for i in range(self.num_pixels):
            x, y = self.get_coords(i)
            color = pattern_func(x, y)
            self._buffer[i] = color
            self.pixels[i] = color
        self.show()


# ============================================================================
# FONCTIONS D'EXEMPLE
# ============================================================================

def rainbow_pattern(x, y):
    """Crée un motif arc-en-ciel."""
    hue = (x + y) * 255 // 14  # 14 = (8+8-2) pour une matrice 8x8
    return hsv_to_rgb(hue / 255, 1.0, 1.0)


def checkerboard_pattern(x, y):
    """Crée un damier."""
    return (255, 255, 255) if (x + y) % 2 == 0 else (0, 0, 0)


def hsv_to_rgb(h, s, v):
    """
    Convertit HSV en RGB.
    
    Args:
        h: Teinte (0.0 à 1.0)
        s: Saturation (0.0 à 1.0)
        v: Valeur/Luminosité (0.0 à 1.0)
        
    Returns:
        Tuple RGB (0-255, 0-255, 0-255)
    """
    if s == 0.0:
        val = int(v * 255)
        return (val, val, val)
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    
    return (int(r * 255), int(g * 255), int(b * 255))


# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================

def main():
    """Fonction principale du programme."""
    # Initialisation de la matrice
    matrix = NeoPixelMatrix(LED_PIN, LED_WIDTH, LED_HEIGHT, BRIGHTNESS)
    
    try:
        # Affichage du dégradé original
        while True:
            matrix.draw_gradient()
            time.sleep(0.1)
            
            # Exemples d'autres motifs (décommenter pour tester)
            # matrix.draw_pattern(rainbow_pattern)
            # time.sleep(1)
            # matrix.draw_pattern(checkerboard_pattern)
            # time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nArrêt du programme...")
        matrix.clear()
        print("LEDs éteintes. Au revoir!")


if __name__ == "__main__":
    main()
