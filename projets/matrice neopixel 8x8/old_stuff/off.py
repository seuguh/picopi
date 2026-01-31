import board
import neopixel

# Configuration de la matrice
LED_WIDTH = 8
LED_HEIGHT = 8
NUM_PIXELS = LED_WIDTH * LED_HEIGHT

# Création de l'objet neopixel
pixels = neopixel.NeoPixel(board.GP0, NUM_PIXELS, auto_write=False)

# Éteindre toutes les LEDs
for i in range(NUM_PIXELS):
    pixels[i] = (0, 0, 0)

# Mise à jour de la matrice
pixels.show()
