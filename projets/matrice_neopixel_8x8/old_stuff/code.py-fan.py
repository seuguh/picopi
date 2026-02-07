import board
import neopixel
import time
import math

# Configuration de la matrice
LED_WIDTH = 8
LED_HEIGHT = 8
NUM_PIXELS = LED_WIDTH * LED_HEIGHT

# Création de l'objet neopixel
pixels = neopixel.NeoPixel(board.GP0, NUM_PIXELS, auto_write=False)

def fan_blade(x, y, t):
    # Calcul de l'angle par rapport au centre de la matrice
    dx = x - (LED_WIDTH - 1) / 2.0
    dy = y - (LED_HEIGHT - 1) / 2.0
    angle = math.atan2(dy, dx)
    # Calcul de la distance par rapport au centre
    dist = math.sqrt(dx * dx + dy * dy)
    # Calcul de la luminosité en fonction de l'angle, du temps et de la distance
    brightness = math.sin(4.0 * (angle - t)) * (1.0 - dist / (math.sqrt(2) * LED_WIDTH / 2.0))
    if brightness > 0:  # Si la luminosité est positive, allumer la LED
        r = 0  # Pas de composante rouge
        g = int(brightness * 255)  # Composante verte
        b = 0  # Pas de composante bleue
    else:  # Sinon, éteindre la LED
        r = 0
        g = 0
        b = 0
    return (r, g, b)

def draw_matrix(t):
    for i in range(NUM_PIXELS):
        # Calcul des coordonnées x et y dans la matrice
        x = i % LED_WIDTH
        y = i // LED_WIDTH
        # Calcul de la couleur du pixel
        color = fan_blade(x, y, t)
        # Définition de la couleur du pixel
        pixels[i] = color
    # Mise à jour de la matrice
    pixels.show()

t = 0.0
while True:
    draw_matrix(t)
    time.sleep(0.1)
    t += 0.1
