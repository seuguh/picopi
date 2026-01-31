"""
Programme principal avec sélection d'effets par bouton
Appuyez sur le bouton GP1 pour changer d'effet
VERSION CORRIGÉE - Bouton fonctionnel
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
# INITIALISATION DU BOUTON (CORRIGÉE)
# ============================================================================

class Button:
    """Classe pour gérer le bouton avec anti-rebond."""
    
    def __init__(self, pin):
        """
        Initialise le bouton.
        
        Args:
            pin: Pin GPIO du bouton
        """
        # Configuration du bouton
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP  # Pull-up = True au repos, False quand appuyé
        
        self.last_state = self.button.value
        self.last_press_time = 0
        self.debounce_time = 0.05  # 50ms anti-rebond (réduit pour meilleure réactivité)
    
    def is_pressed(self):
        """
        Détecte un appui sur le bouton avec anti-rebond.
        
        Returns:
            True si le bouton vient d'être appuyé, False sinon
        """
        current_state = self.button.value
        current_time = time.monotonic()
        
        # Vérifier si l'état a changé
        if current_state != self.last_state:
            # Vérifier le temps d'anti-rebond
            if (current_time - self.last_press_time) > self.debounce_time:
                self.last_press_time = current_time
                self.last_state = current_state
                # Avec pull-up, le bouton est False quand appuyé
                if not current_state:
                    return True
        
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
# EFFETS VISUELS (MODIFIÉS POUR ÊTRE NON-BLOQUANTS)
# ============================================================================

class Effect:
    """Classe de base pour les effets."""
    
    def __init__(self, matrix):
        self.matrix = matrix
        self.running = True
        self.frame_count = 0
    
    def stop(self):
        """Arrête l'effet."""
        self.running = False
    
    def update(self):
        """Méthode à appeler à chaque frame."""
        self.frame_count += 1


class Effect1_Gradient(Effect):
    """Effet 1 : Dégradé animé"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.scale = 0
    
    def update(self):
        super().update()
        self.matrix.draw_gradient(x_scale=self.scale, y_scale=self.scale, z_value=100)
        self.scale = (self.scale + 2) % 256


class Effect2_Rainbow(Effect):
    """Effet 2 : Arc-en-ciel rotatif"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.offset = 0
    
    def update(self):
        super().update()
        
        def rainbow_rotated(x, y):
            hue = ((x + y + self.offset) * 255 // 14) % 256
            return hsv_to_rgb(hue / 255, 1.0, 1.0)
        
        self.matrix.draw_pattern(rainbow_rotated)
        self.offset = (self.offset + 1) % 256


class Effect3_Wave(Effect):
    """Effet 3 : Vague"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.t = 0
    
    def update(self):
        super().update()
        
        def wave_pattern(x, y):
            wave = math.sin((x + self.t) * 0.5) * 0.5 + 0.5
            intensity = int(wave * 255)
            return (0, intensity, 255 - intensity)
        
        self.matrix.draw_pattern(wave_pattern)
        self.t += 0.3


class Effect4_Spiral(Effect):
    """Effet 4 : Spirale"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.offset = 0
    
    def update(self):
        super().update()
        
        def spiral_pattern(x, y):
            cx, cy = 3.5, 3.5
            dx, dy = x - cx, y - cy
            angle = math.atan2(dy, dx)
            distance = math.sqrt(dx*dx + dy*dy)
            hue = (angle + distance + self.offset) % (2 * math.pi)
            hue_normalized = hue / (2 * math.pi)
            return hsv_to_rgb(hue_normalized, 1.0, 1.0)
        
        self.matrix.draw_pattern(spiral_pattern)
        self.offset += 0.1


class Effect5_Fire(Effect):
    """Effet 5 : Feu"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.heat = [[0 for _ in range(8)] for _ in range(8)]
    
    def update(self):
        super().update()
        
        # Refroidissement
        for y in range(8):
            for x in range(8):
                cooldown = random.randint(0, 10)
                self.heat[y][x] = max(0, self.heat[y][x] - cooldown)
        
        # Propagation vers le haut
        for y in range(7, 0, -1):
            for x in range(8):
                self.heat[y][x] = (self.heat[y-1][x] + 
                                 self.heat[y-1][(x-1) % 8] + 
                                 self.heat[y-1][(x+1) % 8]) // 3
        
        # Source de chaleur en bas
        for x in range(8):
            self.heat[0][x] = random.randint(200, 255)
        
        # Affichage
        for y in range(8):
            for x in range(8):
                t = self.heat[y][x]
                if t < 85:
                    r, g, b = t * 3, 0, 0
                elif t < 170:
                    r, g, b = 255, (t - 85) * 3, 0
                else:
                    r, g, b = 255, 255, (t - 170) * 3
                
                self.matrix.set_pixel(x, y, (r, g, b))
        
        self.matrix.show()


class Effect6_Rain(Effect):
    """Effet 6 : Pluie"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.drops = []
    
    def update(self):
        super().update()
        
        # Nouvelles gouttes
        if random.random() < 0.3:
            self.drops.append([random.randint(0, 7), 0, 255])
        
        # Fond bleu foncé
        self.matrix.fill((0, 0, 20))
        
        # Mise à jour des gouttes
        new_drops = []
        for drop in self.drops:
            x, y, intensity = drop
            
            if 0 <= y < 8:
                self.matrix.set_pixel(x, y, (0, 0, intensity))
            
            drop[1] += 1
            drop[2] = max(0, drop[2] - 20)
            
            if drop[1] < 8 and drop[2] > 0:
                new_drops.append(drop)
        
        self.drops = new_drops
        self.matrix.show()


class Effect7_Heart(Effect):
    """Effet 7 : Cœur battant"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.t = 0
        self.heart_pixels = [
            (1, 1), (2, 1), (4, 1), (5, 1),
            (0, 2), (1, 2), (2, 2), (4, 2), (5, 2), (6, 2),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
            (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
            (2, 5), (3, 5), (4, 5),
            (3, 6),
        ]
    
    def update(self):
        super().update()
        
        intensity = int((math.sin(self.t) * 0.5 + 0.5) * 255)
        
        self.matrix.fill((0, 0, 0))
        for x, y in self.heart_pixels:
            self.matrix.set_pixel(x, y, (intensity, 0, 0))
        
        self.matrix.show()
        self.t += 0.2


class Effect8_Checkerboard(Effect):
    """Effet 8 : Damier clignotant"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.colors = [
            ((255, 0, 0), (0, 0, 255)),
            ((0, 255, 0), (255, 255, 0)),
        ]
        self.offset = 0
        self.color_index = 0
    
    def update(self):
        super().update()
        
        def animated_checker(x, y):
            if (x + y + self.offset) % 2 == 0:
                return self.colors[self.color_index][0]
            return self.colors[self.color_index][1]
        
        self.matrix.draw_pattern(animated_checker)
        self.offset = (self.offset + 1) % 2
        
        if self.frame_count % 20 == 0:
            self.color_index = (self.color_index + 1) % len(self.colors)


class Effect9_Stars(Effect):
    """Effet 9 : Étoiles scintillantes"""
    
    def __init__(self, matrix):
        super().__init__(matrix)
        self.stars = []
    
    def update(self):
        super().update()
        
        # Ajouter de nouvelles étoiles
        if random.random() < 0.2:
            self.stars.append({
                'x': random.randint(0, 7),
                'y': random.randint(0, 7),
                'brightness': 0,
                'direction': 1
            })
        
        # Fond noir
        self.matrix.fill((0, 0, 0))
        
        # Mise à jour des étoiles
        new_stars = []
        for star in self.stars:
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
        
        self.stars = new_stars
        self.matrix.show()


# ============================================================================
# GESTIONNAIRE D'EFFETS (CORRIGÉ)
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
        self.last_frame_time = 0
        self.frame_delay = 0.05  # 20 FPS
    
    def next_effect(self):
        """Passe à l'effet suivant."""
        # Arrêter l'effet actuel
        if self.current_effect:
            self.current_effect.stop()
        
        # Passer à l'effet suivant
        self.current_effect_index = (self.current_effect_index + 1) % len(self.effects)
        
        # Afficher le numéro de l'effet avec défilement
        effect_number = self.current_effect_index + 1
        print(f"\n=== Effet {effect_number} selectionne ===")
        
        # Couleur arc-en-ciel pour le numéro
        hue = (effect_number - 1) / len(self.effects)
        color = hsv_to_rgb(hue, 1.0, 1.0)
        
        display_number(self.matrix, effect_number % 10, color=color, scroll=True)
        time.sleep(EFFECT_DISPLAY_TIME)
        
        # Lancer le nouvel effet
        EffectClass = self.effects[self.current_effect_index]
        self.current_effect = EffectClass(self.matrix)
        self.last_frame_time = time.monotonic()
    
    def update(self):
        """Met à jour l'effet actuel."""
        current_time = time.monotonic()
        
        # Vérifier si c'est le temps de mettre à jour l'affichage
        if current_time - self.last_frame_time >= self.frame_delay:
            if self.current_effect:
                try:
                    self.current_effect.update()
                except Exception as e:
                    print(f"Erreur dans l'effet: {e}")
                    self.next_effect()
            
            self.last_frame_time = current_time
    
    def check_button(self):
        """Vérifie si le bouton a été appuyé."""
        return self.button.is_pressed()


# ============================================================================
# PROGRAMME PRINCIPAL (CORRIGÉ)
# ============================================================================

def main():
    """Fonction principale du programme."""
    print("=" * 50)
    print("  SELECTEUR D'EFFETS NEOPIXEL - BOUTON")
    print("=" * 50)
    print("Appuyez sur le bouton GP1 pour changer d'effet")
    print("Ctrl+C pour quitter")
    print("=" * 50)
    print("Initialisation...")
    
    # Initialisation
    try:
        matrix = NeoPixelMatrix(LED_PIN, brightness=BRIGHTNESS)
        print("Matrice NeoPixel initialisee")
    except Exception as e:
        print(f"Erreur initialisation matrice: {e}")
        return
    
    try:
        button = Button(BUTTON_PIN)
        print("Bouton initialise sur GP1")
        print("Bouton au repos:", button.button.value)
    except Exception as e:
        print(f"Erreur initialisation bouton: {e}")
        return
    
    manager = EffectManager(matrix, button)
    
    # Démarrer avec le premier effet
    print("\nDebut du programme!")
    manager.next_effect()
    
    # Compteur pour afficher l'état du bouton (debug)
    debug_counter = 0
    
    try:
        while True:
            # Vérifier le bouton
            if manager.check_button():
                print("Bouton appuye!")
                manager.next_effect()
                # Petite pause après changement d'effet
                time.sleep(0.2)
            
            # Mettre à jour l'effet actuel
            manager.update()
            
            # Debug: afficher l'état du bouton toutes les 100 frames
            debug_counter += 1
            if debug_counter % 100 == 0:
                # Afficher l'état du bouton dans la console
                print(f"Etat bouton: {button.button.value} (1=relache, 0=appuye)", end='\r')
            
            # Petite pause pour éviter de saturer le CPU
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\n\nArret du programme...")
        if manager.current_effect:
            manager.current_effect.stop()
        matrix.clear()
        print("LEDs eteintes. Au revoir!")


if __name__ == "__main__":
    main()