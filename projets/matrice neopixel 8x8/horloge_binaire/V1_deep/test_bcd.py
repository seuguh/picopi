"""
Test de l'affichage BCD
Ce script affiche tous les chiffres de 0 à 9 en format BCD
pour vérifier la logique d'encodage

UTILISATION:
1. Renommer code.py en code_backup.py
2. Renommer ce fichier en code.py
3. Observer les chiffres affichés sur la matrice
4. Restaurer code.py après le test
"""

import board
import neopixel
import time

# Configuration
NEOPIXEL_PIN = board.GP0
NUM_PIXELS = 64
BRIGHTNESS = 0.3

# Couleur pour l'affichage
COULEUR_TEST = (0, 100, 200)  # Bleu cyan

# Initialisation
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

def coords_to_index(x, y):
    """Convertit (x,y) en index LED"""
    if x < 0 or x > 7 or y < 0 or y > 7:
        return None
    return x * 8 + y

def afficher_chiffre_bcd(chiffre, colonnes, nb_bits=4):
    """
    Affiche un chiffre en BCD sur les colonnes spécifiées
    
    Args:
        chiffre: Valeur à afficher (0-15 pour 4 bits, 0-7 pour 3 bits)
        colonnes: Liste des colonnes à utiliser (ex: [0, 1])
        nb_bits: Nombre de bits à utiliser (3 ou 4)
    """
    pixels.fill((0, 0, 0))
    
    for bit in range(nb_bits):
        if chiffre & (1 << bit):
            # Chaque bit occupe 2 rangées
            y_start = bit * 2
            for col in colonnes:
                for y in [y_start, y_start + 1]:
                    idx = coords_to_index(col, y)
                    if idx is not None:
                        pixels[idx] = COULEUR_TEST
    
    pixels.show()

def afficher_binaire_texte(chiffre, nb_bits=4):
    """Affiche la représentation binaire en texte"""
    binaire = bin(chiffre)[2:].zfill(nb_bits)
    return binaire

print("=== TEST AFFICHAGE BCD ===\n")
print("Chaque chiffre sera affiché pendant 3 secondes")
print("Organisation verticale (de bas en haut):")
print("  Rangées 0-1: Bit 0 (valeur 1)")
print("  Rangées 2-3: Bit 1 (valeur 2)")
print("  Rangées 4-5: Bit 2 (valeur 4)")
print("  Rangées 6-7: Bit 3 (valeur 8)")
print("\n" + "="*50)

# Test 1: Chiffres 0-9 avec 4 bits (colonnes 0-1)
print("\nTest 1: Chiffres 0-9 (4 bits sur colonnes 0-1)")
print("="*50)

for chiffre in range(10):
    binaire = afficher_binaire_texte(chiffre, 4)
    print(f"\nChiffre {chiffre}:")
    print(f"  Binaire: {binaire}")
    print(f"  Bit 3 (8): {'●' if chiffre & 8 else '○'}")
    print(f"  Bit 2 (4): {'●' if chiffre & 4 else '○'}")
    print(f"  Bit 1 (2): {'●' if chiffre & 2 else '○'}")
    print(f"  Bit 0 (1): {'●' if chiffre & 1 else '○'}")
    
    afficher_chiffre_bcd(chiffre, [0, 1], 4)
    time.sleep(3)

# Test 2: Dizaines de minutes/secondes 0-5 (3 bits sur colonne 2)
print("\n" + "="*50)
print("\nTest 2: Dizaines 0-5 (3 bits sur colonne 2)")
print("="*50)

for chiffre in range(6):
    binaire = afficher_binaire_texte(chiffre, 3)
    print(f"\nDizaine {chiffre}:")
    print(f"  Binaire: {binaire}")
    print(f"  Bit 2 (4): {'●' if chiffre & 4 else '○'}")
    print(f"  Bit 1 (2): {'●' if chiffre & 2 else '○'}")
    print(f"  Bit 0 (1): {'●' if chiffre & 1 else '○'}")
    
    afficher_chiffre_bcd(chiffre, [2], 3)
    time.sleep(3)

# Test 3: Heures 1-12 (format 12h sur colonnes 0-1)
print("\n" + "="*50)
print("\nTest 3: Heures 1-12 format 12h (4 bits sur colonnes 0-1)")
print("="*50)

for heure in range(1, 13):
    binaire = afficher_binaire_texte(heure, 4)
    print(f"\nHeure {heure:02d}:00:")
    print(f"  Binaire: {binaire}")
    print(f"  Bit 3 (8): {'●' if heure & 8 else '○'}")
    print(f"  Bit 2 (4): {'●' if heure & 4 else '○'}")
    print(f"  Bit 1 (2): {'●' if heure & 2 else '○'}")
    print(f"  Bit 0 (1): {'●' if heure & 1 else '○'}")
    
    afficher_chiffre_bcd(heure, [0, 1], 4)
    time.sleep(2)

# Test 4: Affichage complet d'une heure
print("\n" + "="*50)
print("\nTest 4: Affichage complet d'une heure complète")
print("="*50)

def afficher_heure_complete(heures, minutes, secondes):
    """Affiche une heure complète en BCD"""
    pixels.fill((0, 0, 0))
    
    # Calculs
    dizaines_minutes = minutes // 10
    unites_minutes = minutes % 10
    dizaines_secondes = secondes // 10
    unites_secondes = secondes % 10
    
    def allumer_bits(valeur, colonnes, nb_bits, couleur):
        """Allume les bits d'une valeur"""
        for bit in range(nb_bits):
            if valeur & (1 << bit):
                y_start = bit * 2
                for col in colonnes:
                    for y in [y_start, y_start + 1]:
                        idx = coords_to_index(col, y)
                        if idx is not None:
                            pixels[idx] = couleur
    
    # Heures (colonnes 0-1) en bleu
    allumer_bits(heures, [0, 1], 4, (0, 0, 150))
    
    # Dizaines minutes (colonnes 3-4) en cyan
    allumer_bits(dizaines_minutes, [3, 4], 3, (0, 150, 150))
    
    # Unités minutes (colonnes 6-7) en cyan
    allumer_bits(unites_minutes, [6, 7], 4, (0, 150, 150))
    
    # Dizaines secondes (colonne 2) en vert
    allumer_bits(dizaines_secondes, [2], 3, (0, 150, 0))
    
    # Unités secondes (colonne 5) en vert
    allumer_bits(unites_secondes, [5], 4, (0, 150, 0))
    
    pixels.show()

exemples = [
    (3, 45, 27),
    (12, 0, 0),
    (1, 30, 15),
    (9, 59, 59),
    (6, 15, 42)
]

for h, m, s in exemples:
    print(f"\n{h:02d}:{m:02d}:{s:02d}")
    print(f"  Heures: {h} = {bin(h)[2:].zfill(4)}")
    print(f"  Minutes: {m//10}{m%10} = {bin(m//10)[2:].zfill(3)} {bin(m%10)[2:].zfill(4)}")
    print(f"  Secondes: {s//10}{s%10} = {bin(s//10)[2:].zfill(3)} {bin(s%10)[2:].zfill(4)}")
    
    afficher_heure_complete(h, m, s)
    time.sleep(4)

# Test 5: Tableau de référence visuel
print("\n" + "="*50)
print("\nTest 5: Tableau de référence (affichage continu)")
print("="*50)
print("\nTableau binaire → décimal:")
print("┌─────────┬─────────┬─────────┐")
print("│ Binaire │ Décimal │ Pattern │")
print("├─────────┼─────────┼─────────┤")

patterns = {
    0: "○○○○ (éteint)",
    1: "●●○○ (bas)",
    2: "○○●●○○",
    3: "●●●●○○",
    4: "○○○○●●",
    5: "●●○○●●",
    6: "○○●●●●",
    7: "●●●●●●",
    8: "○○○○○○●● (haut)",
    9: "●●○○○○●●"
}

for i in range(10):
    binaire = bin(i)[2:].zfill(4)
    pattern = patterns[i]
    print(f"│  {binaire}  │    {i}    │ {pattern:15} │")
    if i < 9:
        print("├─────────┼─────────┼─────────┤")
    else:
        print("└─────────┴─────────┴─────────┘")

# Affichage séquentiel continu
print("\nAffichage séquentiel de 0 à 9 en boucle...")
print("(Ctrl+C pour arrêter)\n")

try:
    compteur = 0
    while True:
        chiffre = compteur % 10
        print(f"\rChiffre: {chiffre} ({bin(chiffre)[2:].zfill(4)})", end="")
        afficher_chiffre_bcd(chiffre, [0, 1], 4)
        time.sleep(1.5)
        compteur += 1
        
except KeyboardInterrupt:
    print("\n\nTest interrompu par l'utilisateur.")

# Affichage final
pixels.fill((0, 0, 0))
pixels.show()

print("\n=== TESTS BCD TERMINÉS ===")
print("\nVérifications effectuées:")
print("✓ Chiffres 0-9 (4 bits)")
print("✓ Dizaines 0-5 (3 bits)")
print("✓ Heures 1-12 (format 12h)")
print("✓ Affichages complets")
print("✓ Tableau de référence")
print("\nSi l'affichage est correct, le système BCD fonctionne!")
print("Restaurez code.py et utilisez l'horloge normalement.")
