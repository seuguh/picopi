"""
Exemples d'utilisation du contrôleur NeoPixel Matrix
Différents motifs et animations pour votre matrice LED 8x8
"""

import board
import time
from neopixel_matrix_optimized import NeoPixelMatrix, rainbow_pattern, checkerboard_pattern, hsv_to_rgb


# ============================================================================
# EXEMPLE 1 : DÉGRADÉ ANIMÉ
# ============================================================================

def exemple_degrade_anime():
    """Animation d'un dégradé qui change progressivement."""
    print("Démarrage : Dégradé animé")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    try:
        scale = 0
        while True:
            matrix.draw_gradient(x_scale=scale, y_scale=scale, z_value=100)
            scale = (scale + 2) % 256
            time.sleep(0.03)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Dégradé animé")


# ============================================================================
# EXEMPLE 2 : ARC-EN-CIEL ROTATIF
# ============================================================================

def exemple_arc_en_ciel():
    """Affiche un arc-en-ciel qui tourne."""
    print("Démarrage : Arc-en-ciel rotatif")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.2)
    
    def rainbow_rotated(x, y, offset):
        hue = ((x + y + offset) * 255 // 14) % 256
        return hsv_to_rgb(hue / 255, 1.0, 1.0)
    
    try:
        offset = 0
        while True:
            matrix.draw_pattern(lambda x, y: rainbow_rotated(x, y, offset))
            offset = (offset + 1) % 256
            time.sleep(0.05)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Arc-en-ciel rotatif")


# ============================================================================
# EXEMPLE 3 : DAMIER CLIGNOTANT
# ============================================================================

def exemple_damier_clignotant():
    """Damier qui alterne entre deux couleurs."""
    print("Démarrage : Damier clignotant")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    colors = [
        ((255, 0, 0), (0, 0, 255)),    # Rouge/Bleu
        ((0, 255, 0), (255, 255, 0)),  # Vert/Jaune
    ]
    
    def animated_checker(x, y, offset, color_pair):
        if (x + y + offset) % 2 == 0:
            return color_pair[0]
        return color_pair[1]
    
    try:
        offset = 0
        color_index = 0
        iterations = 0
        
        while True:
            matrix.draw_pattern(
                lambda x, y: animated_checker(x, y, offset, colors[color_index])
            )
            offset = (offset + 1) % 2
            iterations += 1
            
            # Changer de palette toutes les 20 itérations
            if iterations % 20 == 0:
                color_index = (color_index + 1) % len(colors)
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Damier clignotant")


# ============================================================================
# EXEMPLE 4 : VAGUE
# ============================================================================

def exemple_vague():
    """Effet de vague qui traverse la matrice."""
    print("Démarrage : Vague")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    import math
    
    def wave_pattern(x, y, t):
        # Calcul de l'intensité basée sur une onde sinusoïdale
        wave = math.sin((x + t) * 0.5) * 0.5 + 0.5
        intensity = int(wave * 255)
        return (0, intensity, 255 - intensity)
    
    try:
        t = 0
        while True:
            matrix.draw_pattern(lambda x, y: wave_pattern(x, y, t))
            t += 0.3
            time.sleep(0.05)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Vague")


# ============================================================================
# EXEMPLE 5 : SPIRALE
# ============================================================================

def exemple_spirale():
    """Spirale colorée qui tourne."""
    print("Démarrage : Spirale")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    import math
    
    def spiral_pattern(x, y, offset):
        # Centrer la spirale
        cx, cy = 3.5, 3.5
        dx, dy = x - cx, y - cy
        
        # Calculer l'angle et la distance
        angle = math.atan2(dy, dx)
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Créer l'effet de spirale
        hue = (angle + distance + offset) % (2 * math.pi)
        hue_normalized = hue / (2 * math.pi)
        
        return hsv_to_rgb(hue_normalized, 1.0, 1.0)
    
    try:
        offset = 0
        while True:
            matrix.draw_pattern(lambda x, y: spiral_pattern(x, y, offset))
            offset += 0.1
            time.sleep(0.03)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Spirale")


# ============================================================================
# EXEMPLE 6 : EFFET FEU
# ============================================================================

def exemple_feu():
    """Simulation d'un feu avec des couleurs chaudes."""
    print("Démarrage : Effet feu")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    import random
    
    # Buffer pour l'effet feu
    heat = [[0 for _ in range(matrix.width)] for _ in range(matrix.height)]
    
    def fire_pattern():
        # Refroidissement
        for y in range(matrix.height):
            for x in range(matrix.width):
                cooldown = random.randint(0, 10)
                heat[y][x] = max(0, heat[y][x] - cooldown)
        
        # Propagation de la chaleur vers le haut
        for y in range(matrix.height - 1, 0, -1):
            for x in range(matrix.width):
                heat[y][x] = (heat[y-1][x] + 
                             heat[y-1][(x-1) % matrix.width] + 
                             heat[y-1][(x+1) % matrix.width]) // 3
        
        # Source de chaleur en bas
        for x in range(matrix.width):
            heat[0][x] = random.randint(200, 255)
        
        # Convertir la chaleur en couleur
        for y in range(matrix.height):
            for x in range(matrix.width):
                t = heat[y][x]
                if t < 85:
                    r, g, b = t * 3, 0, 0
                elif t < 170:
                    r, g, b = 255, (t - 85) * 3, 0
                else:
                    r, g, b = 255, 255, (t - 170) * 3
                
                matrix.set_pixel(x, y, (r, g, b))
        
        matrix.show()
    
    try:
        while True:
            fire_pattern()
            time.sleep(0.05)
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Effet feu")


# ============================================================================
# EXEMPLE 7 : PLUIE
# ============================================================================

def exemple_pluie():
    """Effet de gouttes de pluie qui tombent."""
    print("Démarrage : Pluie")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    import random
    
    # Liste des gouttes [x, y, intensité]
    drops = []
    
    try:
        while True:
            # Ajouter de nouvelles gouttes aléatoirement
            if random.random() < 0.3:
                drops.append([random.randint(0, 7), 0, 255])
            
            # Effacer la matrice
            matrix.fill((0, 0, 20))  # Fond bleu foncé
            
            # Mettre à jour et dessiner les gouttes
            new_drops = []
            for drop in drops:
                x, y, intensity = drop
                
                # Dessiner la goutte
                if 0 <= y < matrix.height:
                    matrix.set_pixel(x, y, (0, 0, intensity))
                
                # Déplacer la goutte vers le bas
                drop[1] += 1
                drop[2] = max(0, drop[2] - 20)  # Diminuer l'intensité
                
                # Garder la goutte si elle est encore visible
                if drop[1] < matrix.height and drop[2] > 0:
                    new_drops.append(drop)
            
            drops = new_drops
            matrix.show()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Pluie")


# ============================================================================
# EXEMPLE 8 : CŒUR BATTANT
# ============================================================================

def exemple_coeur_battant():
    """Cœur qui bat en changeant d'intensité."""
    print("Démarrage : Cœur battant")
    matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
    
    import math
    
    # Forme du cœur (coordonnées)
    heart_pixels = [
        (1, 1), (2, 1), (4, 1), (5, 1),
        (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        (2, 5), (3, 5), (4, 5),
        (3, 6),
    ]
    
    try:
        t = 0
        while True:
            # Calculer l'intensité du battement
            intensity = (math.sin(t) * 0.5 + 0.5) * 255
            intensity = int(intensity)
            
            # Effacer et redessiner
            matrix.fill((0, 0, 0))
            for x, y in heart_pixels:
                matrix.set_pixel(x, y, (intensity, 0, 0))
            
            matrix.show()
            t += 0.2
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        matrix.clear()
        print("Arrêt : Cœur battant")


# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def menu():
    """Affiche le menu et lance l'exemple choisi."""
    exemples = {
        '1': ('Dégradé animé', exemple_degrade_anime),
        '2': ('Arc-en-ciel rotatif', exemple_arc_en_ciel),
        '3': ('Damier clignotant', exemple_damier_clignotant),
        '4': ('Vague', exemple_vague),
        '5': ('Spirale', exemple_spirale),
        '6': ('Effet feu', exemple_feu),
        '7': ('Pluie', exemple_pluie),
        '8': ('Cœur battant', exemple_coeur_battant),
    }
    
    print("\n" + "="*50)
    print("  EXEMPLES NEOPIXEL MATRIX")
    print("="*50)
    for key, (name, _) in exemples.items():
        print(f"  {key}. {name}")
    print("  q. Quitter")
    print("="*50)
    
    choix = input("\nChoisissez un exemple (1-8, q pour quitter) : ").strip()
    
    if choix.lower() == 'q':
        print("Au revoir !")
        return
    
    if choix in exemples:
        name, fonction = exemples[choix]
        print(f"\nLancement de : {name}")
        print("Appuyez sur Ctrl+C pour arrêter\n")
        fonction()
    else:
        print("Choix invalide !")
        menu()


if __name__ == "__main__":
    # Note : Sur un microcontrôleur, décommentez l'exemple souhaité
    # au lieu d'utiliser le menu interactif
    
    # Exemples à décommenter pour utilisation sur microcontrôleur :
    # exemple_degrade_anime()
    # exemple_arc_en_ciel()
    # exemple_damier_clignotant()
    # exemple_vague()
    # exemple_spirale()
    # exemple_feu()
    # exemple_pluie()
    # exemple_coeur_battant()
    
    # Menu interactif (pour ordinateur uniquement)
    try:
        menu()
    except Exception as e:
        print(f"Erreur : {e}")
        print("\nSur microcontrôleur, décommentez l'exemple souhaité.")
