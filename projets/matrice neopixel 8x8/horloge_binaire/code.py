"""
HORLOGE BINAIRE ÉLÉGANTE 8x8 - CIRCUITPYTHON 10.0.3
Affiche l'heure, minutes, secondes en binaire avec animations
Version optimisée pour CircuitPython 10.0.3
"""

import board
import time
import math
import sys
import os

# ============================================================================
# CONFIGURATION AVANCÉE
# ============================================================================

LED_PIN = board.GP0
BRIGHTNESS = 0.25
USE_HW_RTC = False  # Mettre à True si vous avez un module RTC
USE_NTP = False     # Mettre à True pour synchronisation WiFi
BUTTON_PIN = board.GP1  # Bouton pour changement de mode

# Couleurs avec saturation améliorée
COLOR_HOURS = (255, 80, 0)        # Orange vif
COLOR_MINUTES = (0, 255, 80)      # Vert émeraude
COLOR_SECONDS = (80, 180, 255)    # Bleu ciel
COLOR_SEPARATOR = (180, 180, 180) # Gris clair
COLOR_BACKGROUND = (5, 5, 10)     # Bleu nuit très sombre

# Modes d'affichage
MODE_BINARY = 0      # Bits statiques
MODE_COUNTING = 1    # Animation de comptage
MODE_PULSE = 2       # Pulsation avec les secondes
MODE_RAINBOW = 3     # Couleurs arc-en-ciel
MODE_MATRIX = 4      # Effet "Matrix digital rain"
MODE_FIRE = 5        # Effet feu
MODE_COUNT = 6       # Nombre total de modes

# Configuration d'affichage
BIT_POSITIONS = {
    'hours': {'col_start': 0, 'col_end': 1, 'bits': 5},   # 0-23 = 5 bits max
    'minutes': {'col_start': 2, 'col_end': 3, 'bits': 6}, # 0-59 = 6 bits max
    'seconds': {'col_start': 4, 'col_end': 5, 'bits': 6}, # 0-59 = 6 bits max
}

# ============================================================================
# IMPORTS CONDITIONNELS
# ============================================================================

print(f"\n{'='*60}")
print(f"HORLOGE BINAIRE 8x8 - CircuitPython {sys.version.split()[0]}")
print(f"{'='*60}")

# Tester les fonctionnalités de la version 10
print("\n📊 Tests de fonctionnalités:")
print(f"  • F-strings: {'✓' if sys.version_info >= (3,6) else '✗'}")
print(f"  • math.tau: {'✓' if hasattr(math, 'tau') else '✗'}")
print(f"  • time.monotonic_ns: {'✓' if hasattr(time, 'monotonic_ns') else '✗'}")

try:
    import neopixel
    from neopixel_matrix_optimized import NeoPixelMatrix, hsv_to_rgb
    print("  • NeoPixelMatrix: ✓")
except ImportError as e:
    print(f"  • NeoPixelMatrix: ✗ ({e})")
    # Création d'une classe de secours améliorée
    class NeoPixelMatrix:
        def __init__(self, pin, brightness=0.3, width=8, height=8, auto_write=False):
            self.width = width
            self.height = height
            self.brightness = brightness
            self.auto_write = auto_write
            self.pixels = [[(0,0,0) for _ in range(width)] for _ in range(height)]
            print(f"  Matrice virtuelle {width}x{height} créée")
        
        def __getitem__(self, index):
            return self.pixels[index]
        
        def set_pixel(self, x, y, color):
            if 0 <= x < self.width and 0 <= y < self.height:
                r, g, b = color
                # Application de la luminosité
                r = int(r * self.brightness)
                g = int(g * self.brightness)
                b = int(b * self.brightness)
                self.pixels[y][x] = (r, g, b)
                if self.auto_write:
                    self.show()
        
        def get_pixel(self, x, y):
            if 0 <= x < self.width and 0 <= y < self.height:
                return self.pixels[y][x]
            return (0,0,0)
        
        def fill(self, color):
            r, g, b = color
            r = int(r * self.brightness)
            g = int(g * self.brightness)
            b = int(b * self.brightness)
            for y in range(self.height):
                for x in range(self.width):
                    self.pixels[y][x] = (r, g, b)
        
        def show(self):
            # Pour debug: afficher un aperçu ASCII
            if os.getenv('DEBUG_MATRIX'):
                print("\n" + "-"*25)
                for y in range(self.height):
                    row = ""
                    for x in range(self.width):
                        r, g, b = self.pixels[y][x]
                        if sum((r, g, b)) > 50:
                            row += "██"
                        else:
                            row += "  "
                    print(row)
        
        def clear(self):
            self.fill((0,0,0))
            self.show()
        
        def dim(self, factor):
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b = self.pixels[y][x]
                    self.pixels[y][x] = (
                        int(r * factor),
                        int(g * factor),
                        int(b * factor)
                    )
    
    def hsv_to_rgb(hue, saturation=1.0, value=1.0):
        """Conversion HSV vers RGB optimisée."""
        hue = hue % 1.0
        i = int(hue * 6.0)
        f = hue * 6.0 - i
        p = value * (1.0 - saturation)
        q = value * (1.0 - f * saturation)
        t = value * (1.0 - (1.0 - f) * saturation)
        
        i %= 6
        if i == 0:
            return (int(value * 255), int(t * 255), int(p * 255))
        elif i == 1:
            return (int(q * 255), int(value * 255), int(p * 255))
        elif i == 2:
            return (int(p * 255), int(value * 255), int(t * 255))
        elif i == 3:
            return (int(p * 255), int(q * 255), int(value * 255))
        elif i == 4:
            return (int(t * 255), int(p * 255), int(value * 255))
        else:
            return (int(value * 255), int(p * 255), int(q * 255))

# ============================================================================
# GESTION DU TEMPS AVANCÉE
# ============================================================================

class AdvancedTimeManager:
    """Gestion avancée du temps avec multiples sources."""
    
    def __init__(self):
        self.start_time = time.monotonic_ns() if hasattr(time, 'monotonic_ns') else time.monotonic()
        self.rtc = None
        self.ntp_synced = False
        self.time_offset = 0
        
        # Initialiser RTC hardware si disponible
        if USE_HW_RTC:
            self._init_hw_rtc()
        
        # Configuration par défaut
        self.current_time = (12, 0, 0)  # MIDI par défaut
        print(f"⏰ Gestionnaire temps initialisé (RTC: {self.rtc is not None})")
    
    def _init_hw_rtc(self):
        """Initialise le RTC hardware."""
        try:
            import rtc
            self.rtc = rtc.RTC()
            
            # Essayer de synchroniser avec NTP si demandé
            if USE_NTP:
                self._sync_with_ntp()
                
        except ImportError:
            print("⚠️ Module rtc non disponible")
        except Exception as e:
            print(f"⚠️ Erreur RTC: {e}")
    
    def _sync_with_ntp(self):
        """Synchronise avec un serveur NTP."""
        try:
            import socketpool
            import wifi
            import adafruit_ntp
            
            # Connexion WiFi (à configurer)
            wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
            
            pool = socketpool.SocketPool(wifi.radio)
            ntp = adafruit_ntp.NTP(pool, tz_offset=1)  # UTC+1 pour France
            
            # Mettre à jour le RTC
            self.rtc.datetime = ntp.datetime
            self.ntp_synced = True
            
            print("✅ Synchronisation NTP réussie")
            
        except Exception as e:
            print(f"⚠️ Erreur NTP: {e}")
    
    def get_time(self):
        """Récupère l'heure actuelle depuis la source appropriée."""
        if self.rtc:
            # Heure depuis RTC hardware
            now = self.rtc.datetime
            return now.tm_hour, now.tm_min, now.tm_sec
        else:
            # Heure simulée basée sur le temps écoulé
            if hasattr(time, 'monotonic_ns'):
                elapsed_ns = time.monotonic_ns() - self.start_time
                elapsed = elapsed_ns / 1_000_000_000  # Conversion en secondes
            else:
                elapsed = time.monotonic() - self.start_time
            
            # Ajouter à l'heure de départ
            total_seconds = int(elapsed) + self.time_offset
            seconds = total_seconds % 60
            minutes = (total_seconds // 60) % 60
            hours = (total_seconds // 3600) % 24
            
            return hours, minutes, seconds
    
    def set_time(self, hours, minutes, seconds=0):
        """Règle l'heure manuellement."""
        self.current_time = (hours % 24, minutes % 60, seconds % 60)
        
        if hasattr(time, 'monotonic_ns'):
            self.start_time = time.monotonic_ns()
        else:
            self.start_time = time.monotonic()
        
        self.time_offset = hours * 3600 + minutes * 60 + seconds
        print(f"🕐 Heure réglée: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def get_binary_debug(self, hours, minutes, seconds):
        """Retourne une représentation texte debug."""
        h_bin = f"{hours:08b}"
        m_bin = f"{minutes:08b}"
        s_bin = f"{seconds:08b}"
        
        # Version détaillée avec bits marqués
        h_marked = self._mark_active_bits(h_bin, 5)  # 5 bits pour heures
        m_marked = self._mark_active_bits(m_bin, 6)  # 6 bits pour minutes
        s_marked = self._mark_active_bits(s_bin, 6)  # 6 bits pour secondes
        
        return (f"{hours:02d}:{minutes:02d}:{seconds:02d}\n"
                f"H:{h_marked} ({hours:2d})\n"
                f"M:{m_marked} ({minutes:2d})\n"
                f"S:{s_marked} ({seconds:2d})")
    
    def _mark_active_bits(self, binary_str, significant_bits):
        """Marque les bits significatifs."""
        result = []
        for i, bit in enumerate(binary_str):
            if i >= (8 - significant_bits):
                # Bit significatif
                if bit == '1':
                    result.append(f"¹")  # Exposant pour bit actif
                else:
                    result.append(f"⁰")  # Exposant pour bit inactif
            else:
                # Bit non significatif (toujours 0 pour nos plages)
                result.append("·")
        return "".join(result)
    
    def get_time_fraction(self):
        """Retourne la fraction de la journée écoulée (0.0 à 1.0)."""
        h, m, s = self.get_time()
        total_seconds = h * 3600 + m * 60 + s
        return total_seconds / 86400.0

# ============================================================================
# HORLOGE BINAIRE AVANCÉE
# ============================================================================

class AdvancedBinaryClock:
    """Horloge binaire avec effets avancés."""
    
    def __init__(self, matrix):
        self.matrix = matrix
        self.mode = MODE_BINARY
        self.animation_time = 0
        self.last_update = time.monotonic()
        self.transition_progress = 0.0
        self.target_mode = MODE_BINARY
        
        # État pour les effets spéciaux
        self.matrix_drops = []  # Pour l'effet Matrix
        self.fire_heat = [[0.0 for _ in range(8)] for _ in range(8)]  # Pour l'effet feu
    
    def update(self, hours, minutes, seconds):
        """Met à jour l'affichage."""
        current_time = time.monotonic()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        self.animation_time += delta_time
        
        # Gestion des transitions de mode
        if self.mode != self.target_mode:
            self.transition_progress = min(1.0, self.transition_progress + delta_time * 2)
            if self.transition_progress >= 1.0:
                self.mode = self.target_mode
        
        # Effacer avec fond optionnel
        if self.mode in [MODE_MATRIX, MODE_FIRE]:
            self.matrix.fill(COLOR_BACKGROUND)
        else:
            self.matrix.fill((0, 0, 0))
        
        # Appliquer le mode courant
        if self.mode == MODE_BINARY:
            self._draw_binary(hours, minutes, seconds)
        elif self.mode == MODE_COUNTING:
            self._draw_counting(hours, minutes, seconds)
        elif self.mode == MODE_PULSE:
            self._draw_pulse(hours, minutes, seconds)
        elif self.mode == MODE_RAINBOW:
            self._draw_rainbow(hours, minutes, seconds)
        elif self.mode == MODE_MATRIX:
            self._draw_matrix_effect(hours, minutes, seconds)
        elif self.mode == MODE_FIRE:
            self._draw_fire_effect(hours, minutes, seconds)
        
        # Appliquer la transition si en cours
        if self.transition_progress < 1.0:
            self._apply_transition()
        
        self.matrix.show()
    
    def _draw_binary(self, hours, minutes, seconds):
        """Mode binaire classique."""
        self._draw_binary_value(hours, BIT_POSITIONS['hours'], COLOR_HOURS)
        self._draw_binary_value(minutes, BIT_POSITIONS['minutes'], COLOR_MINUTES)
        self._draw_binary_value(seconds, BIT_POSITIONS['seconds'], COLOR_SECONDS)
        self._draw_separators()
    
    def _draw_binary_value(self, value, config, base_color):
        """Dessine une valeur binaire."""
        binary_str = f"{value:08b}"
        
        for col_offset in range(2):
            col = config['col_start'] + col_offset
            bits = binary_str[col_offset*4:(col_offset+1)*4]
            
            for row_offset, bit in enumerate(bits):
                if bit == '1':
                    # Animation subtile sur les bits actifs
                    pulse = 0.9 + 0.1 * math.sin(self.animation_time * 3 + row_offset)
                    color = tuple(int(c * pulse) for c in base_color)
                    self.matrix.set_pixel(col, 7 - row_offset, color)
    
    def _draw_counting(self, hours, minutes, seconds):
        """Mode avec animation de comptage."""
        # Utiliser les secondes pour animer le "comptage"
        count_progress = (seconds % 10) / 10.0
        
        for value, config, color in [
            (hours, BIT_POSITIONS['hours'], COLOR_HOURS),
            (minutes, BIT_POSITIONS['minutes'], COLOR_MINUTES),
            (seconds, BIT_POSITIONS['seconds'], COLOR_SECONDS)
        ]:
            binary_str = f"{value:08b}"
            
            for col_offset in range(2):
                col = config['col_start'] + col_offset
                bits = binary_str[col_offset*4:(col_offset+1)*4]
                
                for row_offset, bit in enumerate(bits):
                    row = 7 - row_offset
                    intensity = 1.0
                    
                    if bit == '1':
                        # Bits actifs pleins
                        self.matrix.set_pixel(col, row, color)
                    else:
                        # Bits inactifs avec animation
                        phase = (row_offset + col_offset * 4) / 8.0
                        if (count_progress * 1.2) > phase:
                            faded = tuple(c // 4 for c in color)
                            self.matrix.set_pixel(col, row, faded)
        
        self._draw_separators()
    
    def _draw_pulse(self, hours, minutes, seconds):
        """Mode avec pulsation."""
        # Pulsation basée sur les secondes
        pulse_base = 0.7 + 0.3 * math.sin(self.animation_time * math.tau)
        pulse_sec = 0.8 + 0.2 * math.sin(self.animation_time * math.tau * 2)
        
        # Heures et minutes avec pulsation douce
        self._draw_binary_value(hours, BIT_POSITIONS['hours'], 
                               tuple(int(c * pulse_base) for c in COLOR_HOURS))
        self._draw_binary_value(minutes, BIT_POSITIONS['minutes'], 
                               tuple(int(c * pulse_base) for c in COLOR_MINUTES))
        
        # Secondes avec pulsation accentuée
        self._draw_binary_value(seconds, BIT_POSITIONS['seconds'], 
                               tuple(int(c * pulse_sec) for c in COLOR_SECONDS))
        
        # Barre de progression des secondes
        sec_progress = seconds / 59.0
        bar_height = int(sec_progress * 8)
        for i in range(bar_height):
            hue = (self.animation_time * 20 + i * 30) % 360
            color = hsv_to_rgb(hue / 360, 0.7, pulse_sec)
            self.matrix.set_pixel(7, 7 - i, color)
    
    def _draw_rainbow(self, hours, minutes, seconds):
        """Mode arc-en-ciel."""
        time_fraction = hours / 24.0 + minutes / 1440.0 + seconds / 86400.0
        
        for value, config, _ in [
            (hours, BIT_POSITIONS['hours'], COLOR_HOURS),
            (minutes, BIT_POSITIONS['minutes'], COLOR_MINUTES),
            (seconds, BIT_POSITIONS['seconds'], COLOR_SECONDS)
        ]:
            binary_str = f"{value:08b}"
            
            for col_offset in range(2):
                col = config['col_start'] + col_offset
                bits = binary_str[col_offset*4:(col_offset+1)*4]
                
                for row_offset, bit in enumerate(bits):
                    if bit == '1':
                        # Couleur basée sur position et temps
                        hue = (time_fraction * 360 + col * 45 + row_offset * 15) % 360
                        saturation = 0.8 + 0.2 * math.sin(self.animation_time + col)
                        color = hsv_to_rgb(hue / 360, saturation, 1.0)
                        self.matrix.set_pixel(col, 7 - row_offset, color)
        
        # Colonne séparatrice arc-en-ciel
        for y in range(8):
            hue = (self.animation_time * 30 + y * 45) % 360
            color = hsv_to_rgb(hue / 360, 0.6, 0.7)
            self.matrix.set_pixel(6, y, color)
    
    def _draw_matrix_effect(self, hours, minutes, seconds):
        """Effet Matrix digital rain avec heure intégrée."""
        # Ajouter de nouvelles gouttes
        if len(self.matrix_drops) < 15 and (seconds % 3 == 0):
            self.matrix_drops.append({
                'x': (hours + minutes + seconds) % 8,
                'y': 0,
                'speed': 0.5 + (seconds % 10) / 20,
                'brightness': 1.0,
                'length': 3 + (minutes % 5)
            })
        
        # Mettre à jour les gouttes existantes
        for drop in self.matrix_drops[:]:
            drop['y'] += drop['speed']
            drop['brightness'] *= 0.95
            
            if drop['y'] >= 8 or drop['brightness'] < 0.1:
                self.matrix_drops.remove(drop)
        
        # Dessiner les gouttes
        for drop in self.matrix_drops:
            for i in range(drop['length']):
                y_pos = int(drop['y'] - i)
                if 0 <= y_pos < 8:
                    intensity = drop['brightness'] * (1.0 - i/drop['length'])
                    color = (0, int(255 * intensity), 0)
                    self.matrix.set_pixel(drop['x'], y_pos, color)
        
        # Superposer l'heure en filigrane
        alpha = 0.3  # Transparence
        self._draw_binary_value(hours, BIT_POSITIONS['hours'], 
                               tuple(int(c * alpha) for c in COLOR_HOURS))
        self._draw_binary_value(minutes, BIT_POSITIONS['minutes'], 
                               tuple(int(c * alpha) for c in COLOR_MINUTES))
    
    def _draw_fire_effect(self, hours, minutes, seconds):
        """Effet de feu avec heure intégrée."""
        # Génération de chaleur à la base
        for x in range(8):
            self.fire_heat[0][x] = min(1.0, self.fire_heat[0][x] + 
                                      (0.1 if (x + seconds) % 3 == 0 else 0))
        
        # Propagation vers le haut
        for y in range(7, 0, -1):
            for x in range(8):
                # Moyenne des cellules voisines
                left = self.fire_heat[y][(x-1) % 8]
                right = self.fire_heat[y][(x+1) % 8]
                below = self.fire_heat[y-1][x]
                
                self.fire_heat[y][x] = (left + right + below) / 3.5
                self.fire_heat[y][x] *= 0.95  # Refroidissement
        
        # Affichage du feu
        for y in range(8):
            for x in range(8):
                heat = self.fire_heat[y][x]
                if heat > 0.1:
                    # Gradient feu: jaune -> orange -> rouge
                    if heat > 0.7:
                        color = (255, 255, int(200 * heat))
                    elif heat > 0.4:
                        color = (255, int(180 * heat), 0)
                    else:
                        color = (int(200 * heat), int(80 * heat), 0)
                    
                    self.matrix.set_pixel(x, y, color)
        
        # Superposer l'heure en filigrane
        alpha = 0.4
        self._draw_binary_value(hours % 12, BIT_POSITIONS['hours'], 
                               tuple(int(c * alpha) for c in (0, 200, 255)))
    
    def _draw_separators(self):
        """Dessine les séparateurs."""
        # Points aux intersections
        for y in [1, 3, 5]:
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * 2 + y)
            color = tuple(int(c * pulse) for c in COLOR_SEPARATOR)
            self.matrix.set_pixel(6, y, color)
    
    def _apply_transition(self):
        """Applique un effet de transition entre modes."""
        progress = self.transition_progress
        fade = math.sin(progress * math.pi)  # Fonction d'easing
        
        if progress < 0.5:
            # Fade out
            self.matrix.dim(1.0 - fade)
        else:
            # Fade in
            self.matrix.dim(fade)
    
    def set_mode(self, mode):
        """Change le mode avec transition."""
        if 0 <= mode < MODE_COUNT:
            self.target_mode = mode
            self.transition_progress = 0.0
            print(f"🔄 Changement vers mode: {self._mode_name(mode)}")
    
    def next_mode(self):
        """Passe au mode suivant."""
        self.set_mode((self.mode + 1) % MODE_COUNT)
    
    def _mode_name(self, mode):
        """Nom du mode."""
        names = [
            "Binaire Classique",
            "Animation Comptage",
            "Pulsation Temporelle",
            "Arc-en-Ciel Dynamique",
            "Matrix Digital Rain",
            "Effet Feu"
        ]
        return names[mode] if mode < len(names) else f"Mode {mode}"

# ============================================================================
# INTERFACE UTILISATEUR
# ============================================================================

class ClockInterface:
    """Interface utilisateur avec animations et menus."""
    
    def __init__(self, matrix, clock, time_manager):
        self.matrix = matrix
        self.clock = clock
        self.time_manager = time_manager
        self.showing_info = False
        self.info_timeout = 0
    
    def show_startup_animation(self):
        """Animation de démarrage spectaculaire."""
        print("\n" + "🌟" * 30)
        print("        HORLOGE BINAIRE 8x8 - CIRCUITPYTHON 10")
        print("🌟" * 30)
        
        # Animation de spirale
        for frame in range(30):
            self.matrix.fill((0, 0, 0))
            for i in range(64):
                angle = i * 0.1 + frame * 0.3
                radius = (frame / 30) * 4
                x = int(3.5 + radius * math.cos(angle))
                y = int(3.5 + radius * math.sin(angle))
                
                if 0 <= x < 8 and 0 <= y < 8:
                    hue = (frame * 12 + i * 5) % 360
                    color = hsv_to_rgb(hue / 360, 1.0, 1.0)
                    self.matrix.set_pixel(x, y, color)
            
            self.matrix.show()
            time.sleep(0.03)
        
        # Explosion finale
        self.matrix.fill((255, 255, 255))
        self.matrix.show()
        time.sleep(0.1)
        
        # Révélation du texte "BINARY"
        text = "BINARY"
        for i, char in enumerate(text):
            x = i + 1
            ascii_val = ord(char)
            binary = f"{ascii_val:08b}"
            
            for bit_pos in range(4):
                if binary[bit_pos] == '1':
                    self.matrix.set_pixel(x, 3 + bit_pos, (255, 100, 0))
            
            self.matrix.show()
            time.sleep(0.2)
        
        time.sleep(1)
        self.matrix.clear()
    
    def show_current_mode(self):
        """Affiche brièvement le mode courant."""
        self.matrix.fill((0, 0, 0))
        
        # Afficher le numéro du mode
        mode_num = self.clock.mode + 1
        binary_mode = f"{mode_num:04b}"
        
        for i, bit in enumerate(binary_mode):
            if bit == '1':
                hue = (self.clock.mode * 60) % 360
                color = hsv_to_rgb(hue / 360, 1.0, 1.0)
                self.matrix.set_pixel(2 + i, 4, color)
        
        self.matrix.show()
        time.sleep(0.8)
        self.matrix.clear()
    
    def show_time_debug(self, hours, minutes, seconds):
        """Affiche un debug visuel."""
        if self.showing_info:
            # Mode texte alternatif
            self._show_text_display(hours, minutes, seconds)
            
            self.info_timeout -= 1
            if self.info_timeout <= 0:
                self.showing_info = False
        else:
            # Mode horloge normal
            self.clock.update(hours, minutes, seconds)
    
    def _show_text_display(self, hours, minutes, seconds):
        """Affiche l'heure en format texte."""
        self.matrix.fill((0, 0, 20))
        
        # Afficher les chiffres de l'heure
        digits = [hours // 10, hours % 10, minutes // 10, minutes % 10]
        
        for i, digit in enumerate(digits):
            if digit > 0:
                for j in range(min(digit, 8)):
                    color = hsv_to_rgb(i * 90 / 360, 1.0, 1.0)
                    self.matrix.set_pixel(i * 2, 7 - j, color)
        
        self.matrix.show()

# ============================================================================
# GESTION DES BOUTONS
# ============================================================================

class ButtonHandler:
    """Gestion des entrées boutons."""
    
    def __init__(self, pin):
        import digitalio
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        
        self.last_state = self.button.value
        self.last_press_time = 0
        self.long_press_threshold = 1.0
        
        self.click_count = 0
        self.last_click_time = 0
        self.double_click_threshold = 0.5
        
        print(f"🔄 Bouton initialisé sur {pin}")
    
    def update(self):
        """Met à jour l'état du bouton."""
        current_state = self.button.value
        current_time = time.monotonic()
        
        # Détection d'appui (front descendant)
        if not current_state and self.last_state:
            self.last_press_time = current_time
            self.click_count += 1
            
            # Vérifier double-clic
            if current_time - self.last_click_time < self.double_click_threshold:
                self.click_count = 2
            self.last_click_time = current_time
        
        self.last_state = current_state
        
        # Retourner le type d'événement
        if self.click_count > 0:
            if current_state:  # Bouton relâché
                press_duration = current_time - self.last_press_time
                
                if press_duration >= self.long_press_threshold:
                    event = 'long'
                elif self.click_count >= 2:
                    event = 'double'
                else:
                    event = 'click'
                
                self.click_count = 0
                return event
        
        return None

# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================

def main():
    """Programme principal optimisé."""
    print("\n🚀 Initialisation en cours...")
    
    # Initialisation des composants
    matrix = NeoPixelMatrix(LED_PIN, brightness=BRIGHTNESS, auto_write=False)
    time_manager = AdvancedTimeManager()
    clock = AdvancedBinaryClock(matrix)
    interface = ClockInterface(matrix, clock, time_manager)
    button = ButtonHandler(BUTTON_PIN)
    
    # Réglage de l'heure
    time_manager.set_time(12, 0, 0)
    
    # Animation de démarrage
    interface.show_startup_animation()
    interface.show_current_mode()
    
    print("\n✅ Prêt !")
    print("Contrôles:")
    print("  • Clic: Changement de mode")
    print("  • Double-clic: Affichage debug")
    print("  • Appui long: Réglage heure")
    print("\n" + "─" * 60)
    
    # Variables de performance
    frame_count = 0
    last_fps_time = time.monotonic()
    fps = 0
    
    try:
        while True:
            # Gestion du bouton
            button_event = button.update()
            if button_event:
                print(f"Bouton: {button_event}")
                
                if button_event == 'click':
                    clock.next_mode()
                    interface.show_current_mode()
                elif button_event == 'double':
                    interface.showing_info = True
                    interface.info_timeout = 100  # ~5 secondes
                elif button_event == 'long':
                    # Mode réglage heure (simplifié)
                    h, m, s = time_manager.get_time()
                    time_manager.set_time((h + 1) % 24, m, s)
            
            # Récupération de l'heure
            hours, minutes, seconds = time_manager.get_time()
            
            # Mise à jour de l'affichage
            interface.show_time_debug(hours, minutes, seconds)
            
            # Calcul FPS (toutes les 100 frames)
            frame_count += 1
            if frame_count >= 100:
                current_time = time.monotonic()
                elapsed = current_time - last_fps_time
                fps = frame_count / elapsed
                
                print(f"📊 FPS: {fps:.1f} | Heure: {hours:02d}:{minutes:02d}:{seconds:02d}")
                
                frame_count = 0
                last_fps_time = current_time
            
            # Contrôle de la vitesse de boucle
            time.sleep(0.02)  # ~50 FPS max
    
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé...")
    except Exception as e:
        print(f"\n⚠️ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        matrix.clear()
        print("\n✨ Au revoir !")
        print("=" * 60)

def simple_mode():
    """Mode simple sans animations."""
    matrix = NeoPixelMatrix(LED_PIN, brightness=0.15)
    time_manager = AdvancedTimeManager()
    
    print("⏱️ Mode simple - Horloge binaire basique")
    
    try:
        while True:
            h, m, s = time_manager.get_time()
            
            # Affichage minimaliste
            matrix.fill((0, 0, 0))
            
            # Heures
            h_bin = f"{h:08b}"
            for col in range(2):
                bits = h_bin[col*4:(col+1)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, COLOR_HOURS)
            
            # Minutes
            m_bin = f"{m:08b}"
            for col in range(2, 4):
                bits = m_bin[(col-2)*4:(col-1)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, COLOR_MINUTES)
            
            # Secondes
            s_bin = f"{s:08b}"
            for col in range(4, 6):
                bits = s_bin[(col-4)*4:(col-3)*4]
                for i, bit in enumerate(bits):
                    if bit == '1':
                        matrix.set_pixel(col, 7-i, COLOR_SECONDS)
            
            # Séparateur clignotant
            if s % 2 == 0:
                matrix.set_pixel(6, 3, COLOR_SEPARATOR)
                matrix.set_pixel(6, 4, COLOR_SEPARATOR)
            
            matrix.show()
            
            # Afficher toutes les minutes
            if s == 0 and m == 0:
                print(f"{h:02d}:{m:02d}:{s:02d}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        matrix.clear()

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    # Configuration du mode d'exécution
    MODE = "advanced"  # "advanced" ou "simple"
    
    if MODE == "advanced":
        main()
    else:
        simple_mode()