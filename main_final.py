"""
Programme principal avec sélection d'effets par bouton
Appuyez sur le bouton GP1 pour changer d'effet
"""

import board
import digitalio
import time
from neopixel_matrix_optimized import NeoPixelMatrix, rainbow_pattern, hsv_to_rgb
import random
import math


# ============================================================================
# CONFIGURATION
# ============================================================================

LED_PIN = board.GP0
BUTTON_PIN = board.GP1
BRIGHTNESS = 0.3
EFFECT_DISPLAY_TIME = 1.5  # Temps d'affichage du numéro d'effet (secondes)


# ============================================================================
# INITIALISATION DU BOUTON
# ============================================================================
class Button:
    """Classe pour gérer le bouton avec anti-rebond."""
    
    def __init__(self, pin):
        """
        Initialise le bouton.
        
        Args:
            pin: Pin GPIO du bouton
        """
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP  # Pull-up = True au repos
        
        self.last_state = self.button.value
        self.last_press_time = 0
        self.debounce_time = 0.05  # Réduit à 50ms pour une meilleure réactivité
    
    def is_pressed(self):
        """
        Détecte un appui sur le bouton avec anti-rebond.
        
        Returns:
            True si le bouton vient d'être appuyé, False sinon
        """
        current_state = self.button.value
        current_time = time.monotonic()
        
        # Détection d'un appui (passage de True à False avec pull-up)
        # IMPORTANT: avec pull-up, le bouton est True (HIGH) au repos
        # et False (LOW) quand appuyé
        if current_state != self.last_state:
            self.last_state = current_state
            self.last_press_time = current_time
            return not current_state  # Retourne True quand bouton appuyé (False)
        
        return False

# ============================================================================
# AFFICHAGE DES CHIFFRES 8x8
# ============================================================================

# Définition des chiffres en 8x8 pixels (1 = allumé, 0 = éteint)
DIGITS = {
    0: [
        "  ████  ",
        " ██  ██ ",
        "██    ██",
        "██    ██",
        "██    ██",
        "██    ██",
        " ██  ██ ",
        "  ████  "
    ],
    1: [
        "   ██   ",
        "  ███   ",
        " ████   ",
        "   ██   ",
        "   ██   ",
        "   ██   ",
        "   ██   ",
        " ██████ "
    ],
    2: [
        "  ████  ",
        " ██  ██ ",
        "     ██ ",
        "    ██  ",
        "   ██   ",
        "  ██    ",
        " ██     ",
        " ██████ "
    ],
    3: [
        "  ████  ",
        " ██  ██ ",
        "     ██ ",
        "   ███  ",
        "     ██ ",
        "     ██ ",
        " ██  ██ ",
        "  ████  "
    ],
    4: [
        "    ██  ",
        "   ███  ",
        "  ████  ",
        " ██ ██  ",
        "██  ██  ",
        "████████",
        "    ██  ",
        "    ██  "
    ],
    5: [
        " ██████ ",
        " ██     ",
        " ██     ",
        " █████  ",
        "     ██ ",
        "     ██ ",
        " ██  ██ ",
        "  ████  "
    ],
    6: [
        "  ████  ",
        " ██  ██ ",
        " ██     ",
        " █████  ",
        " ██  ██ ",
        " ██  ██ ",
        " ██  ██ ",
        "  ████  "
    ],
    7: [
        " ██████ ",
        "     ██ ",
        "    ██  ",
        "   ██   ",
        "  ██    ",
        "  ██    ",
        "  ██    ",
        "  ██    "
    ],
    8: [
        "  ████  ",
        " ██  ██ ",
        " ██  ██ ",
        "  ████  ",
        " ██  ██ ",
        " ██  ██ ",
        " ██  ██ ",
        "  ████  "
    ],
    9: [
        "  ████  ",
        " ██  ██ ",
        " ██  ██ ",
        " ██  ██ ",
        "  █████ ",
        "     ██ ",
        " ██  ██ ",
        "  ████  "
    ]
}


def display_number(matrix, number, color=(0, 255, 255), scroll=True):
    """
    Affiche un numéro sur la matrice avec effet de défilement.
    
    Args:
        matrix: Instance de NeoPixelMatrix
        number: Numéro à afficher (0-9)
        color: Couleur RGB du chiffre
        scroll: Si True, fait défiler le chiffre de droite à gauche
    """
    if number not in DIGITS:
        return
    
    digit = DIGITS[number]
    
    if scroll:
        # Défilement de droite à gauche
        for offset in range(8, -8, -1):
            matrix.fill((0, 0, 0))
            
            for y in range(8):
                for x in range(8):
                    display_x = x + offset
                    if 0 <= display_x < 8:
                        if digit[y][x] == '█':
                            matrix.set_pixel(display_x, y, color)
            
            matrix.show()
            time.sleep(0.05)
    else:
        # Affichage statique
        matrix.fill((0, 0, 0))
        for y in range(8):
            for x in range(8):
                if digit[y][x] == '█':
                    matrix.set_pixel(x, y, color)
        matrix.show()


# ============================================================================
# EFFETS VISUELS
# ============================================================================

class Effect:
    """Classe de base pour les effets."""
    
    def __init__(self, matrix):
        self.matrix = matrix
        self.running = True
    
    def stop(self):
        """Arrête l'effet."""
        self.running = False
    
    def run(self):
        """Méthode à surcharger pour chaque effet."""
        pass


class Effect1_Gradient(Effect):
    """Effet 1 : Dégradé animé"""
    
    def run(self):
        scale = 0
        while self.running:
            self.matrix.draw_gradient(x_scale=scale, y_scale=scale, z_value=100)
            scale = (scale + 2) % 256
            time.sleep(0.03)


class Effect2_Rainbow(Effect):
    """Effet 2 : Arc-en-ciel rotatif"""
    
    def run(self):
        offset = 0
        while self.running:
            def rainbow_rotated(x, y):
                hue = ((x + y + offset) * 255 // 14) % 256
                return hsv_to_rgb(hue / 255, 1.0, 1.0)
            
            self.matrix.draw_pattern(rainbow_rotated)
            offset = (offset + 1) % 256
            time.sleep(0.05)


class Effect3_Wave(Effect):
    """Effet 3 : Vague"""
    
    def run(self):
        t = 0
        while self.running:
            def wave_pattern(x, y):
                wave = math.sin((x + t) * 0.5) * 0.5 + 0.5
                intensity = int(wave * 255)
                return (0, intensity, 255 - intensity)
            
            self.matrix.draw_pattern(wave_pattern)
            t += 0.3
            time.sleep(0.05)


class Effect4_Spiral(Effect):
    """Effet 4 : Spirale"""
    
    def run(self):
        offset = 0
        while self.running:
            def spiral_pattern(x, y):
                cx, cy = 3.5, 3.5
                dx, dy = x - cx, y - cy
                angle = math.atan2(dy, dx)
                distance = math.sqrt(dx*dx + dy*dy)
                hue = (angle + distance + offset) % (2 * math.pi)
                hue_normalized = hue / (2 * math.pi)
                return hsv_to_rgb(hue_normalized, 1.0, 1.0)
            
            self.matrix.draw_pattern(spiral_pattern)
            offset += 0.1
            time.sleep(0.03)


class Effect5_Fire(Effect):
    """Effet 5 : Feu"""
    
    def run(self):
        heat = [[0 for _ in range(8)] for _ in range(8)]
        
        while self.running:
            # Refroidissement
            for y in range(8):
                for x in range(8):
                    cooldown = random.randint(0, 10)
                    heat[y][x] = max(0, heat[y][x] - cooldown)
            
            # Propagation vers le haut
            for y in range(7, 0, -1):
                for x in range(8):
                    heat[y][x] = (heat[y-1][x] + 
                                 heat[y-1][(x-1) % 8] + 
                                 heat[y-1][(x+1) % 8]) // 3
            
            # Source de chaleur en bas
            for x in range(8):
                heat[0][x] = random.randint(200, 255)
            
            # Affichage
            for y in range(8):
                for x in range(8):
                    t = heat[y][x]
                    if t < 85:
                        r, g, b = t * 3, 0, 0
                    elif t < 170:
                        r, g, b = 255, (t - 85) * 3, 0
                    else:
                        r, g, b = 255, 255, (t - 170) * 3
                    
                    self.matrix.set_pixel(x, y, (r, g, b))
            
            self.matrix.show()
            time.sleep(0.05)


class Effect6_Rain(Effect):
    """Effet 6 : Pluie"""
    
    def run(self):
        drops = []
        
        while self.running:
            # Nouvelles gouttes
            if random.random() < 0.3:
                drops.append([random.randint(0, 7), 0, 255])
            
            # Fond bleu foncé
            self.matrix.fill((0, 0, 20))
            
            # Mise à jour des gouttes
            new_drops = []
            for drop in drops:
                x, y, intensity = drop
                
                if 0 <= y < 8:
                    self.matrix.set_pixel(x, y, (0, 0, intensity))
                
                drop[1] += 1
                drop[2] = max(0, drop[2] - 20)
                
                if drop[1] < 8 and drop[2] > 0:
                    new_drops.append(drop)
            
            drops = new_drops
            self.matrix.show()
            time.sleep(0.1)


class Effect7_Heart(Effect):
    """Effet 7 : Cœur battant"""
    
    def run(self):
        heart_pixels = [
            (1, 1), (2, 1), (4, 1), (5, 1),
            (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
            (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
            (2, 5), (3, 5), (4, 5),
            (3, 6),
        ]
        
        t = 0
        while self.running:
            intensity = int((math.sin(t) * 0.5 + 0.5) * 255)
            
            self.matrix.fill((0, 0, 0))
            for x, y in heart_pixels:
                self.matrix.set_pixel(x, y, (intensity, 0, 0))
            
            self.matrix.show()
            t += 0.2
            time.sleep(0.05)


class Effect8_Checkerboard(Effect):
    """Effet 8 : Damier clignotant"""
    
    def run(self):
        colors = [
            ((255, 0, 0), (0, 0, 255)),
            ((0, 255, 0), (255, 255, 0)),
        ]
        offset = 0
        color_index = 0
        iterations = 0
        
        while self.running:
            def animated_checker(x, y):
                if (x + y + offset) % 2 == 0:
                    return colors[color_index][0]
                return colors[color_index][1]
            
            self.matrix.draw_pattern(animated_checker)
            offset = (offset + 1) % 2
            iterations += 1
            
            if iterations % 20 == 0:
                color_index = (color_index + 1) % len(colors)
            
            time.sleep(0.5)


class Effect9_Stars(Effect):
    """Effet 9 : Étoiles scintillantes"""
    
    def run(self):
        stars = []
        
        while self.running:
            # Ajouter de nouvelles étoiles
            if random.random() < 0.2:
                stars.append({
                    'x': random.randint(0, 7),
                    'y': random.randint(0, 7),
                    'brightness': 0,
                    'direction': 1
                })
            
            # Fond noir
            self.matrix.fill((0, 0, 0))
            
            # Mise à jour des étoiles
            new_stars = []
            for star in stars:
                # Scintillement
                star['brightness'] += star['direction'] * 20
                
                if star['brightness'] >= 255:
                    star['brightness'] = 255
                    star['direction'] = -1
                elif star['brightness'] <= 0:
                    star['brightness'] = 0
                    continue
                
                # Afficher l'étoile
                self.matrix.set_pixel(
                    star['x'], 
                    star['y'], 
                    (star['brightness'], star['brightness'], star['brightness'])
                )
                
                new_stars.append(star)
            
            stars = new_stars
            self.matrix.show()
            time.sleep(0.05)


# ============================================================================
# GESTIONNAIRE D'EFFETS
# ============================================================================

class EffectManager:
    """Gère la sélection et l'exécution des effets."""
    
    def __init__(self, matrix, button):
        self.matrix = matrix
        self.button = button
        self.effects = [
            Effect1_Gradient,
            Effect2_Rainbow,
            Effect3_Wave,
            Effect4_Spiral,
            Effect5_Fire,
            Effect6_Rain,
            Effect7_Heart,
            Effect8_Checkerboard,
            Effect9_Stars
        ]
        self.current_effect_index = 0
        self.current_effect = None
    
    def next_effect(self):
        """Passe à l'effet suivant."""
        # Arrêter l'effet actuel
        if self.current_effect:
            self.current_effect.stop()
        
        # Passer à l'effet suivant
        self.current_effect_index = (self.current_effect_index + 1) % len(self.effects)
        
        # Afficher le numéro de l'effet avec défilement
        effect_number = self.current_effect_index + 1
        print(f"Effet {effect_number} selectionne")
        
        # Couleur arc-en-ciel pour le numéro
        hue = (effect_number - 1) / len(self.effects)
        color = hsv_to_rgb(hue, 1.0, 1.0)
        
        display_number(self.matrix, effect_number % 10, color=color, scroll=True)
        time.sleep(EFFECT_DISPLAY_TIME)
        
        # Lancer le nouvel effet
        EffectClass = self.effects[self.current_effect_index]
        self.current_effect = EffectClass(self.matrix)
    
    def run_current_effect(self):
        """Exécute l'effet actuel."""
        if self.current_effect:
            self.current_effect.run()
    
    def check_button(self):
        """Vérifie si le bouton a été appuyé."""
        return self.button.is_pressed()


# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================

def main():
    """Fonction principale du programme."""
    print("=" * 50)
    print("  SELECTEUR D'EFFETS NEOPIXEL - BOUTON")
    print("=" * 50)
    print("Appuyez sur le bouton GP1 pour changer d'effet")
    print("Ctrl+C pour quitter")
    print("=" * 50)
    
    # Initialisation
    matrix = NeoPixelMatrix(LED_PIN, brightness=BRIGHTNESS)
    button = Button(BUTTON_PIN)
    
    manager = EffectManager(matrix, button)
    
    # Démarrer avec le premier effet
    manager.next_effect()
    
    try:
        while True:
            # Vérifier le bouton
            if manager.check_button():
                print("Bouton appuye!")
                manager.next_effect()
            
            # Exécuter l'effet actuel
            try:
                manager.run_current_effect()
            except:
                # Si l'effet plante, passer au suivant
                print("Erreur dans l'effet, passage au suivant...")
                manager.next_effect()
    
    except KeyboardInterrupt:
        print("\n\nArret du programme...")
        if manager.current_effect:
            manager.current_effect.stop()
        matrix.clear()
        print("LEDs eteintes. Au revoir!")


if __name__ == "__main__":
    main()
