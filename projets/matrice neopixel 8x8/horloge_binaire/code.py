# Heures sur 2 premières lignes
# Minutes sur 2 suivantes
# 1 LED = 1 bit
# Ex: 10h30 = 1010 (h) 11110 (min)"""
# HORLOGE BINAIRE ÉLÉGANTE 8x8
#Affiche l'heure, minutes, secondes en binaire avec animations
#"""

import board
import time
from neopixel_matrix_optimized import NeoPixelMatrix, hsv_to_rgb
import math


# ============================================================================
# CONFIGURATION
# ============================================================================

LED_PIN = board.GP0
BRIGHTNESS = 0.2

# Couleurs pour chaque composante de temps
COLOR_HOURS = (255, 100, 0)      # Orange
COLOR_MINUTES = (0, 255, 100)    # Vert clair  
COLOR_SECONDS = (100, 150, 255)  # Bleu clair
COLOR_SEPARATOR = (150, 150, 150)  # Gris pour séparateurs

# Modes d'affichage
MODE_BINARY = 0      # Bits statiques
MODE_COUNTING = 1    # Animation de comptage
MODE_PULSE = 2       # Pulsation avec les secondes
MODE_RAINBOW = 3     # Couleurs arc-en-ciel

# Position des bits sur la matrice
# Chaque valeur (H, M, S) occupe 2 colonnes, 8 bits verticaux
BIT_POSITIONS = {
    'hours': {
        'col_start': 0,    # Colonnes 0-1 pour heures
        'col_end': 1,
        'bit_height': 8,   # 8 bits = 0-255 (mais heures max 23)
    },
    'minutes': {
        'col_start': 2,    # Colonnes 2-3 pour minutes
        'col_end': 3,
        'bit_height': 8,   # 8 bits = 0-255 (minutes max 59)
    },
    'seconds': {
        'col_start': 4,    # Colonnes 4-5 pour secondes
        'col_end': 5,
        'bit_height': 8,   # 8 bits = 0-255 (secondes max 59)
    }
}


# ============================================================================
# CLASSES UTILITAIRES
# ============================================================================

class BinaryClock:
    """Gère l'affichage binaire sur la matrice."""
    
    def __init__(self, matrix, mode=MODE_BINARY):
        self.matrix = matrix
        self.mode = mode
        self.animation_frame = 0
        self.last_second = -1
        
    def display_time(self, hours, minutes, seconds, animate=True):
        """
        Affiche l'heure en binaire.
        
        Args:
            hours: 0-23
            minutes: 0-59
            seconds: 0-59
            animate: True pour activer les animations
        """
        # Effacer l'écran
        self.matrix.fill((0, 0, 0))
        
        # Déterminer si on anime (changement de seconde)
        do_animation = animate and (seconds != self.last_second)
        self.last_second = seconds
        
        # Afficher chaque composante
        self._display_binary_value(hours, 'hours', do_animation)
        self._display_binary_value(minutes, 'minutes', do_animation)
        self._display_binary_value(seconds, 'seconds', do_animation)
        
        # Ajouter des séparateurs/décorations
        self._draw_separators()
        
        # Effets d'animation globaux
        if self.mode == MODE_PULSE and do_animation:
            self._pulse_effect()
        elif self.mode == MODE_RAINBOW:
            self._rainbow_effect()
            
        self.animation_frame += 1
        self.matrix.show()
    
    def _display_binary_value(self, value, value_type, animate=False):
        """Affiche une valeur en binaire à sa position."""
        config = BIT_POSITIONS[value_type]
        
        # Couleur selon le type
        if value_type == 'hours':
            base_color = COLOR_HOURS
        elif value_type == 'minutes':
            base_color = COLOR_MINUTES
        else:  # seconds
            base_color = COLOR_SECONDS
        
        # Convertir en binaire (8 bits)
        binary_str = format(value, '08b')
        
        # Pour chaque colonne (2 colonnes par valeur)
        for col_offset in range(2):
            col = config['col_start'] + col_offset
            
            # 4 bits par colonne (bits 7-4 pour col0, bits 3-0 pour col1)
            if col_offset == 0:
                bits = binary_str[:4]  # 4 bits de poids fort
            else:
                bits = binary_str[4:]  # 4 bits de poids faible
            
            # Afficher chaque bit
            for row_offset, bit in enumerate(bits):
                row = 7 - row_offset  # Inversé: bit 0 en haut, bit 7 en bas
                
                if bit == '1':
                    # LED allumée
                    color = self._get_animated_color(base_color, row_offset, col_offset, 
                                                    value_type, animate)
                    self.matrix.set_pixel(col, row, color)
                elif self.mode == MODE_COUNTING and animate:
                    # Animation de comptage (éclairer brièvement même les bits 0)
                    if self.animation_frame % 30 < 5:  # Clignotement rapide
                        faded_color = tuple(c // 8 for c in base_color)
                        self.matrix.set_pixel(col, row, faded_color)
    
    def _get_animated_color(self, base_color, bit_pos, col_offset, value_type, animate):
        """Calcule la couleur avec effets d'animation."""
        r, g, b = base_color
        
        if self.mode == MODE_RAINBOW:
            # Effet arc-en-ciel progressif
            hue = (self.animation_frame * 5 + bit_pos * 30 + col_offset * 60) % 360
            return hsv_to_rgb(hue / 360, 0.8, 1.0)
        
        elif self.mode == MODE_PULSE and animate and value_type == 'seconds':
            # Pulsation pour les secondes
            pulse = (math.sin(self.animation_frame * 0.5) * 0.3 + 0.7)
            return tuple(int(c * pulse) for c in base_color)
        
        elif self.mode == MODE_COUNTING and animate:
            # Effet de "comptage" - éclairer progressivement
            delay = bit_pos + col_offset * 4
            if self.animation_frame % 60 > delay * 3:
                return base_color
            else:
                return tuple(c // 4 for c in base_color)
        
        else:
            # Mode binaire simple
            return base_color
    
    def _draw_separators(self):
        """Dessine des séparateurs entre heures/minutes/seconds."""
        # Colonne 6: séparateurs verticaux
        for row in [1, 3, 5]:
            self.matrix.set_pixel(6, row, COLOR_SEPARATOR)
        
        # Colonne 7: animation décorative
        if self.mode == MODE_PULSE:
            # Barre qui monte et descend avec les secondes
            height = (self.animation_frame % 60) // 7.5  # 0-8
            for row in range(8):
                if row < height:
                    intensity = 100 + row * 20
                    self.matrix.set_pixel(7, 7 - row, (intensity, intensity, intensity))
        elif self.mode == MODE_RAINBOW:
            # Barre arc-en-ciel verticale
            for row in range(8):
                hue = (self.animation_frame * 10 + row * 45) % 360
                color = hsv_to_rgb(hue / 360, 0.7, 0.6)
                self.matrix.set_pixel(7, row, color)
        else:
            # Points décoratifs
            dot_pos = (self.animation_frame // 10) % 8
            self.matrix.set_pixel(7, dot_pos, COLOR_SEPARATOR)
    
    def _pulse_effect(self):
        """Effet de pulsation global."""
        pulse = (math.sin(self.animation_frame * 0.2) * 0.1 + 0.9)
        self.matrix.dim(pulse)
    
    def _rainbow_effect(self):
        """Applique un léger effet arc-en-ciel sur toute la matrice."""
        for x in range(8):
            for y in range(8):
                current_color = self.matrix.get_pixel(x, y)
                if sum(current_color) > 0:  # Si pixel allumé
                    hue_shift = (self.animation_frame * 2 + x * 10 + y * 5) % 360
                    # Convertir RGB -> HSV -> modifier teinte -> RGB
                    # (simplifié pour l'exemple)
                    r, g, b = current_color
                    hsv_factor = math.sin(hue_shift * math.pi / 180) * 0.2 + 0.8
                    new_color = (
                        min(255, int(r * hsv_factor)),
                        min(255, int(g * hsv_factor)),
                        min(255, int(b * hsv_factor))
                    )
                    self.matrix.set_pixel(x, y, new_color)
    
    def set_mode(self, mode):
        """Change le mode d'affichage."""
        self.mode = mode
        self.animation_frame = 0


# ============================================================================
# GESTION DU TEMPS
# ============================================================================

class TimeManager:
    """Gère l'heure et les fonctions temporelles."""
    
    def __init__(self, use_rtc=True):
        self.use_rtc = use_rtc
        self.start_time = time.monotonic()
        self.simulated_time = (12, 0, 0)  # Heure de départ si pas de RTC
        
        # Essayer d'initialiser l'RTC hardware si disponible
        self.rtc = None
        if use_rtc:
            try:
                import rtc
                self.rtc = rtc.RTC()
                print("RTC hardware initialisé")
            except:
                print("RTC hardware non disponible, utilisation du temps simulé")
    
    def get_time(self):
        """Retourne l'heure actuelle (heures, minutes, secondes)."""
        if self.rtc:
            # Lire depuis RTC hardware
            now = self.rtc.datetime
            return now.tm_hour, now.tm_min, now.tm_sec
        else:
            # Temps simulé (incrémenté à chaque appel)
            hours, minutes, seconds = self.simulated_time
            
            # Incrémenter le temps simulé
            elapsed = time.monotonic() - self.start_time
            total_seconds = int(elapsed)
            
            new_hours = (total_seconds // 3600 + hours) % 24
            new_minutes = (total_seconds // 60 + minutes) % 60
            new_seconds = (total_seconds + seconds) % 60
            
            self.simulated_time = (new_hours, new_minutes, new_seconds)
            return self.simulated_time
    
    def set_time(self, hours, minutes, seconds=0):
        """Règle l'heure manuellement."""
        if self.rtc:
            # Mettre à jour l'RTC hardware
            import rtc
            import adafruit_ntp
            # (Code simplifié - nécessite connexion internet pour NTP)
            print("Utilisez NTP ou un module RTC pour régler l'heure précise")
        else:
            # Mettre à jour le temps simulé
            self.simulated_time = (hours % 24, minutes % 60, seconds % 60)
            self.start_time = time.monotonic()
            print(f"Heure réglée à {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def get_binary_debug(self, hours, minutes, seconds):
        """Retourne une représentation texte du temps en binaire."""
        h_bin = format(hours, '08b')
        m_bin = format(minutes, '08b')
        s_bin = format(seconds, '08b')
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d} = " \
               f"H:{h_bin} M:{m_bin} S:{s_bin}"


# ============================================================================
# AFFICHAGE D'INFORMATIONS
# ============================================================================

class InfoDisplay:
    """Affiche des informations et menus."""
    
    def __init__(self, matrix):
        self.matrix = matrix
    
    def show_boot_animation(self):
        """Animation de démarrage."""
        print("=== HORLOGE BINAIRE 8x8 ===")
        print("Affichage binaire:")
        print("Colonnes 0-1: Heures (0-23)")
        print("Colonnes 2-3: Minutes (0-59)")
        print("Colonnes 4-5: Secondes (0-59)")
        print("1 pixel = 1 bit (0=éteint, 1=allumé)")
        
        # Animation de démarrage
        for i in range(8):
            for x in range(8):
                for y in range(8):
                    if x == i or y == i:
                        color = hsv_to_rgb(i * 45 / 360, 1.0, 1.0)
                        self.matrix.set_pixel(x, y, color)
            self.matrix.show()
            time.sleep(0.05)
        
        time.sleep(0.5)
        self.matrix.fill((0, 0, 0))
        self.matrix.show()
    
    def show_binary_example(self, value, color, label=""):
        """Affiche un exemple de conversion binaire."""
        print(f"\nExemple {label}: {value} décimal = {format(value, '08b')} binaire")
        
        self.matrix.fill((0, 0, 0))
        binary_str = format(value, '08b')
        
        # Afficher sur les colonnes du milieu
        for col_offset in range(2):
            col = 3 + col_offset
            bits = binary_str[col_offset*4:(col_offset+1)*4]
            
            for row_offset, bit in enumerate(bits):
                row = 7 - row_offset
                if bit == '1':
                    self.matrix.set_pixel(col, row, color)
        
        self.matrix.show()
        time.sleep(2)
        self.matrix.fill((0, 0, 0))
        self.matrix.show()
    
    def display_decimal_time(self, hours, minutes, seconds):
        """Affiche brièvement l'heure en décimal."""
        # Utiliser les chiffres si disponibles, sinon animation simple
        self.matrix.fill((0, 0, 0))
        
        # Afficher les chiffres simples
        digits = [
            hours // 10, hours % 10,
            minutes // 10, minutes % 10,
            seconds // 10, seconds % 10
        ]
        
        # Animation rapide
        for i, digit in enumerate(digits):
            col = i + 1
            for row in range(min(8, digit + 1)):
                color = hsv_to_rgb(i * 60 / 360, 1.0, 1.0)
                self.matrix.set_pixel(col, 7 - row, color)
        
        self.matrix.show()
        time.sleep(1)
        self.matrix.fill((0, 0, 0))
        self.matrix.show()


# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================

def main():
    """Fonction principale de l'horloge binaire."""
    print("\n" + "="*50)
    print("HORLOGE BINAIRE 8x8 - INITIALISATION")
    print("="*50)
    
    # Initialisation
    matrix = NeoPixelMatrix(LED_PIN, brightness=BRIGHTNESS)
    clock = BinaryClock(matrix, mode=MODE_BINARY)
    time_manager = TimeManager(use_rtc=False)  # Mettre True si RTC disponible
    info = InfoDisplay(matrix)
    
    # Animation de démarrage
    info.show_boot_animation()
    
    # Exemples d'affichage binaire
    print("\nDemonstration conversion binaire:")
    info.show_binary_example(23, COLOR_HOURS, "Heures max (23)")
    info.show_binary_example(59, COLOR_MINUTES, "Minutes max (59)")
    info.show_binary_example(42, COLOR_SECONDS, "Exemple (42)")
    
    # Régler l'heure de départ (12:00:00)
    time_manager.set_time(12, 0, 0)
    
    # Variables pour changement de mode
    mode_change_counter = 0
    current_mode = MODE_BINARY
    modes = [MODE_BINARY, MODE_COUNTING, MODE_PULSE, MODE_RAINBOW]
    mode_names = ["Binaire", "Comptage", "Pulsation", "Arc-en-ciel"]
    
    print("\n" + "="*50)
    print("Horloge binaire active!")
    print("Mode:", mode_names[current_mode])
    print("Format: HH:MM:SS en binaire")
    print("Colonnes 0-1: Heures | 2-3: Minutes | 4-5: Secondes")
    print("="*50 + "\n")
    
    last_debug_output = 0
    
    try:
        while True:
            # Obtenir l'heure actuelle
            hours, minutes, seconds = time_manager.get_time()
            
            # Afficher l'heure en binaire
            clock.display_time(hours, minutes, seconds, animate=True)
            
            # Changer de mode automatiquement toutes les 30 secondes
            mode_change_counter += 1
            if mode_change_counter >= 300:  # 30 secondes à 10 FPS
                mode_change_counter = 0
                current_mode = (current_mode + 1) % len(modes)
                clock.set_mode(modes[current_mode])
                print(f"Changement de mode: {mode_names[current_mode]}")
            
            # Afficher l'heure en décimal dans la console toutes les 10 secondes
            if time.monotonic() - last_debug_output > 10:
                binary_debug = time_manager.get_binary_debug(hours, minutes, seconds)
                print(f"{hours:02d}:{minutes:02d}:{seconds:02d} - {binary_debug}")
                last_debug_output = time.monotonic()
            
            # Attendre jusqu'à la prochaine seconde
            time.sleep(0.1)  # 10 FPS
    
    except KeyboardInterrupt:
        print("\n\nArret de l'horloge binaire...")
        matrix.clear()
        print("Matrice éteinte. Au revoir!")


# ============================================================================
# VERSION AVEC BOUTON POUR CHANGER DE MODE
# ============================================================================

def main_with_button():
    """Version avec bouton pour changer de mode manuellement."""
    import digitalio
    
    # Configuration du bouton
    BUTTON_PIN = board.GP1
    button = digitalio.DigitalInOut(BUTTON_PIN)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    
    # Initialisation
    matrix = NeoPixelMatrix(LED_PIN, brightness=BRIGHTNESS)
    clock = BinaryClock(matrix, mode=MODE_BINARY)
    time_manager = TimeManager(use_rtc=False)
    
    # Variables
    current_mode = 0
    modes = [MODE_BINARY, MODE_COUNTING, MODE_PULSE, MODE_RAINBOW]
    mode_names = ["Binaire", "Comptage", "Pulsation", "Arc-en-ciel"]
    last_button_state = button.value
    button_press_time = 0
    
    print("Horloge binaire avec bouton - Appuyez pour changer de mode")
    
    try:
        while True:
            # Détection du bouton
            current_button_state = button.value
            if current_button_state != last_button_state:
                if not current_button_state:  # Bouton appuyé (LOW avec pull-up)
                    button_press_time = time.monotonic()
                else:  # Bouton relâché
                    press_duration = time.monotonic() - button_press_time
                    if press_duration > 0.05: # Anti-rebond
                        # Changer de mode
                        current_mode = (current_mode + 1) % len(modes)
                        clock.set_mode(modes[current_mode])
                        print(f"Mode: {mode_names[current_mode]}")
                        
                        # Afficher brièvement le nom du mode
                        matrix.fill((0, 0, 0))
                        # Animation simple pour le nom du mode
                        for i in range(8):
                            color = hsv_to_rgb(current_mode * 90 / 360, 1.0, 1.0)
                            matrix.set_pixel(i, current_mode, color)
                        matrix.show()
                        time.sleep(0.5)
                
                last_button_state = current_button_state
            
            # Afficher l'heure
            hours, minutes, seconds = time_manager.get_time()
            clock.display_time(hours, minutes, seconds, animate=True)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        matrix.clear()
        print("Au revoir!")


# ============================================================================
# VERSION SIMPLIFIÉE (SANS ANIMATIONS)
# ============================================================================

def simple_binary_clock():
    """Version ultra-simple de l'horloge binaire."""
    matrix = NeoPixelMatrix(LED_PIN, brightness=0.1)
    
    # Heure de départ
    hours, minutes, seconds = 12, 0, 0
    start_time = time.monotonic()
    
    print("Horloge binaire simple - Ctrl+C pour quitter")
    
    try:
        while True:
            # Calculer le temps écoulé
            elapsed = time.monotonic() - start_time
            total_seconds = int(elapsed)
            
            # Mettre à jour l'heure
            seconds = total_seconds % 60
            minutes = (total_seconds // 60) % 60
            hours = (total_seconds // 3600 + 12) % 24
            
            # Effacer l'écran
            matrix.fill((0, 0, 0))
            
            # Afficher heures (colonnes 0-1)
            h_bin = format(hours, '08b')
            for col in range(2):
                bits = h_bin[col*4:(col+1)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, (255, 50, 0))
            
            # Afficher minutes (colonnes 2-3)
            m_bin = format(minutes, '08b')
            for col in range(2, 4):
                bits = m_bin[(col-2)*4:(col-1)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, (0, 255, 50))
            
            # Afficher secondes (colonnes 4-5)
            s_bin = format(seconds, '08b')
            for col in range(4, 6):
                bits = s_bin[(col-4)*4:(col-3)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, (50, 100, 255))
            
            # Séparateur (colonne 6)
            if seconds % 2 == 0:  # Clignotement
                for y in [2, 5]:
                    matrix.set_pixel(6, y, (100, 100, 100))
            
            matrix.show()
            
            # Afficher l'heure dans la console toutes les minutes
            if seconds == 0:
                print(f"{hours:02d}:{minutes:02d}:{seconds:02d} - "
                      f"H:{h_bin} M:{m_bin} S:{s_bin}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        matrix.clear()
        print("\nHorloge arrêtée")


# ============================================================================
# CHOIX DU MODE D'EXÉCUTION
# ============================================================================

if __name__ == "__main__":
    # Choisissez une des fonctions principales:
    
    # 1. Version complète avec animations
    main()
    
    # 2. Version avec bouton
    # main_with_button()
    
    # 3. Version ultra-simple
    # simple_binary_clock()