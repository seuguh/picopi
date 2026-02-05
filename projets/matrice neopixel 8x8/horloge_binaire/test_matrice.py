"""
Test de la matrice NeoPixel 8x8
Ce script teste chaque LED individuellement pour vérifier les connexions

UTILISATION:
1. Renommer code.py en code_backup.py
2. Renommer ce fichier en code.py
3. Observer le test sur la matrice
4. Restaurer code.py après le test
"""

import board
import neopixel
import time

# Configuration
NEOPIXEL_PIN = board.GP0
NUM_PIXELS = 64
BRIGHTNESS = 0.3

# Initialisation
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

def coords_to_index(x, y):
    """Convertit (x,y) en index LED"""
    if x < 0 or x > 7 or y < 0 or y > 7:
        return None
    return x * 8 + y

print("=== TEST MATRICE NEOPIXEL 8x8 ===")
print("Test en cours...")

# Test 1: Toutes les LEDs en rouge
print("\nTest 1: Toutes les LEDs en ROUGE")
pixels.fill((100, 0, 0))
pixels.show()
time.sleep(2)

# Test 2: Toutes les LEDs en vert
print("Test 2: Toutes les LEDs en VERT")
pixels.fill((0, 100, 0))
pixels.show()
time.sleep(2)

# Test 3: Toutes les LEDs en bleu
print("Test 3: Toutes les LEDs en BLEU")
pixels.fill((0, 0, 100))
pixels.show()
time.sleep(2)

# Test 4: Toutes les LEDs en blanc
print("Test 4: Toutes les LEDs en BLANC")
pixels.fill((100, 100, 100))
pixels.show()
time.sleep(2)

# Test 5: Test individuel de chaque LED
print("Test 5: Chaque LED individuellement")
pixels.fill((0, 0, 0))

for i in range(NUM_PIXELS):
    # Allumer la LED actuelle en blanc
    pixels[i] = (50, 50, 50)
    pixels.show()
    
    # Afficher la position
    x = i // 8
    y = i % 8
    print(f"LED {i}: position (x={x}, y={y})")
    
    time.sleep(0.1)
    
    # Éteindre
    pixels[i] = (0, 0, 0)

# Test 6: Test par colonnes
print("\nTest 6: Colonnes (gauche à droite)")
pixels.fill((0, 0, 0))

for col in range(8):
    # Allumer la colonne
    for row in range(8):
        idx = coords_to_index(col, row)
        if idx is not None:
            pixels[idx] = (0, 0, 100)
    
    pixels.show()
    print(f"Colonne {col}")
    time.sleep(0.5)
    
    # Éteindre
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.2)

# Test 7: Test par rangées
print("\nTest 7: Rangées (bas vers haut)")
pixels.fill((0, 0, 0))

for row in range(8):
    # Allumer la rangée
    for col in range(8):
        idx = coords_to_index(col, row)
        if idx is not None:
            pixels[idx] = (100, 0, 0)
    
    pixels.show()
    print(f"Rangée {row}")
    time.sleep(0.5)
    
    # Éteindre
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.2)

# Test 8: Diagonales
print("\nTest 8: Diagonale principale")
pixels.fill((0, 0, 0))

for i in range(8):
    idx = coords_to_index(i, i)
    if idx is not None:
        pixels[idx] = (100, 100, 0)

pixels.show()
time.sleep(2)

print("Test 8: Diagonale secondaire")
pixels.fill((0, 0, 0))

for i in range(8):
    idx = coords_to_index(i, 7-i)
    if idx is not None:
        pixels[idx] = (0, 100, 100)

pixels.show()
time.sleep(2)

# Test 9: Bordure
print("\nTest 9: Bordure")
pixels.fill((0, 0, 0))

# Bordure extérieure
for i in range(8):
    # Bas et haut
    pixels[coords_to_index(i, 0)] = (100, 0, 100)
    pixels[coords_to_index(i, 7)] = (100, 0, 100)
    # Gauche et droite
    pixels[coords_to_index(0, i)] = (100, 0, 100)
    pixels[coords_to_index(7, i)] = (100, 0, 100)

pixels.show()
time.sleep(2)

# Test 10: Animation arc-en-ciel
print("\nTest 10: Arc-en-ciel rotatif (10 secondes)")

def wheel(pos):
    """Génère une couleur arc-en-ciel (0-255)"""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

for j in range(256):
    for i in range(NUM_PIXELS):
        pixel_index = (i * 256 // NUM_PIXELS) + j
        r, g, b = wheel(pixel_index & 255)
        pixels[i] = (r//3, g//3, b//3)  # Diviser par 3 pour réduire la luminosité
    
    pixels.show()
    time.sleep(0.02)
    
    # Arrêt après 5 secondes
    if j >= 125:
        break

# Test terminé
print("\n=== TESTS TERMINÉS ===")
print("Toutes les LEDs devraient avoir été testées.")
print("\nSi certaines LEDs n'ont pas fonctionné:")
print("1. Vérifiez les connexions DIN, VCC, GND")
print("2. Vérifiez que GP0 est bien connecté à DIN")
print("3. Vérifiez l'alimentation 5V")
print("\nÉteignez et rallumez le Pico W.")
print("Puis restaurez code.py pour l'horloge normale.")

# Motif final: damier
pixels.fill((0, 0, 0))
for x in range(8):
    for y in range(8):
        if (x + y) % 2 == 0:
            idx = coords_to_index(x, y)
            if idx is not None:
                pixels[idx] = (20, 20, 20)

pixels.show()

# Boucle infinie pour maintenir l'affichage
while True:
    time.sleep(1)
