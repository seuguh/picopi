import board
import neopixel
import time

# Configuration de la matrice
LED_WIDTH = 8
LED_HEIGHT = 8
NUM_PIXELS = LED_WIDTH * LED_HEIGHT

# Création de l'objet neopixel
pixels = neopixel.NeoPixel(board.GP0, NUM_PIXELS, auto_write=False)

def draw_matrix():
    for i in range(NUM_PIXELS):
        # Calcul des coordonnées x et y dans la matrice
        x = i % LED_WIDTH
        y = i // LED_WIDTH

        # Définition de la couleur en fonction de la position
        color = (x * 32, y * 32, 50)

        # Définition de la couleur du pixel
        pixels[i] = color

    # Mise à jour de la matrice
    pixels.show()

while True:
    draw_matrix()
    time.sleep(0.1)