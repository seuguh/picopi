"""
Gestion de l'affichage BCD sur la matrice NeoPixel
Nouvelle organisation des colonnes:
  0-1: Heures (2 colonnes, 4 bits)
  6:   Dizaines secondes (1 colonne, 3 bits)
  2-3: Dizaines minutes (2 colonnes, 3 bits) + Indicateurs réseau
  7:   Unités secondes (1 colonne, 4 bits)
  4-5: Unités minutes (2 colonnes, 4 bits)
Plus d'indicateur PM
Indicateurs réseau:
  WiFi: (2,6) et (3,6) - Rangée 6
  Internet: (2,7) et (3,7) - Rangée 7
"""

import time
from config import Config

class DisplayManager:
    def __init__(self, hardware):
        self.hardware = hardware
        self.last_display = None
        self.current_buffer = [(0, 0, 0)] * 64
        self.network_tester = None  # Sera connecté plus tard
    
    def set_network_tester(self, network_tester):
        """Connecte le testeur réseau pour les indicateurs"""
        self.network_tester = network_tester
    
    def coords_to_index(self, x, y):
        """
        Convertit (x, y) en index LED
        x = 0-7 (colonnes, de gauche à droite)
        y = 0-7 (rangées, de bas en haut)
        """
        if 0 <= x <= 7 and 0 <= y <= 7:
            return x * 8 + y
        return None
    
    def choisir_couleur_base(self, heure_24h):
        """Retourne la couleur selon l'heure (22h-6h = mode nuit)"""
        if heure_24h >= 22 or heure_24h < 6:
            return Config.COULEUR_NUIT
        return Config.COULEUR_NORMALE
    
    def ajouter_indicateurs_reseau(self, buffer):
        """
        Ajoute les indicateurs WiFi et Internet au buffer
        Les indicateurs remplacent les LEDs correspondantes
        """
        if not self.network_tester:
            return buffer
        
        # WiFi - Rangée 6, Colonnes 2 et 3
        wifi_color = self.network_tester.get_wifi_color()
        idx_wifi1 = self.coords_to_index(Config.WIFI_LED_1[0], Config.WIFI_LED_1[1])
        idx_wifi2 = self.coords_to_index(Config.WIFI_LED_2[0], Config.WIFI_LED_2[1])
        
        if idx_wifi1 is not None:
            buffer[idx_wifi1] = wifi_color
        if idx_wifi2 is not None:
            buffer[idx_wifi2] = wifi_color
        
        # Internet - Rangée 7, Colonnes 2 et 3
        internet_color = self.network_tester.get_internet_color()
        idx_internet1 = self.coords_to_index(Config.INTERNET_LED_1[0], Config.INTERNET_LED_1[1])
        idx_internet2 = self.coords_to_index(Config.INTERNET_LED_2[0], Config.INTERNET_LED_2[1])
        
        if idx_internet1 is not None:
            buffer[idx_internet1] = internet_color
        if idx_internet2 is not None:
            buffer[idx_internet2] = internet_color
        
        return buffer
    
    def generer_buffer_bcd(self, heures, minutes, secondes, est_pm, timestamp):
        """
        Génère un buffer de 64 LEDs pour l'heure donnée
        NOUVELLE ORGANISATION:
          0-1: Heures (2 colonnes, 4 bits)
          6:   Dizaines secondes (1 colonne, 3 bits)
          2-3: Dizaines minutes (2 colonnes, 3 bits) + Indicateurs réseau
          7:   Unités secondes (1 colonne, 4 bits)
          4-5: Unités minutes (2 colonnes, 4 bits)
        Indicateurs réseau sur rangées 6-7, colonnes 2-3
        """
        buffer = [(0, 0, 0)] * 64
        
        # Déterminer les couleurs
        heure_24h = (timestamp % 86400) // 3600
        couleur_base = self.choisir_couleur_base(heure_24h)
        
        # Fonctions spécialisées pour chaque type de colonne
        def ajouter_chiffre_large(chiffre, bits, colonne_debut, couleur):
            """
            Ajoute un chiffre BCD sur 2 colonnes (heures, minutes)
            Chaque bit allume 2x2 LEDs (carré de 4 LEDs)
            """
            for bit in range(bits):
                if (chiffre >> bit) & 1:  # Vérifier si le bit est à 1
                    # Allumer un carré de 2x2 LEDs pour ce bit
                    # SAUF sur les positions des indicateurs réseau
                    for row in range(bit * 2, bit * 2 + 2):
                        # Vérifier si cette rangée est occupée par un indicateur
                        is_indicator_row = (row == 6 or row == 7)
                        
                        for col_offset in range(2):
                            col = colonne_debut + col_offset
                            
                            # Vérifier si cette position est un indicateur réseau
                            is_indicator = False
                            if is_indicator_row and col in [2, 3]:
                                # Cette LED est réservée pour un indicateur
                                is_indicator = True
                            
                            # N'allumer que si ce n'est pas un indicateur
                            if not is_indicator:
                                idx = self.coords_to_index(col, row)
                                if idx is not None:
                                    buffer[idx] = couleur
        
        def ajouter_chiffre_etroit(chiffre, bits, colonne, couleur):
            """
            Ajoute un chiffre BCD sur 1 colonne (secondes)
            Chaque bit allume 2 LEDs superposées
            """
            for bit in range(bits):
                if (chiffre >> bit) & 1:  # Vérifier si le bit est à 1
                    # Allumer 2 LEDs superposées pour ce bit
                    for row in range(bit * 2, bit * 2 + 2):
                        idx = self.coords_to_index(colonne, row)
                        if idx is not None:
                            buffer[idx] = couleur
        
        # 1. Heures (colonnes 0-1, 4 bits) - colonnes larges
        ajouter_chiffre_large(heures, 4, 0, couleur_base)
        
        # 2. Dizaines de minutes (colonnes 2-3, 3 bits) - colonnes larges
        dizaines_minutes = minutes // 10
        ajouter_chiffre_large(dizaines_minutes, 3, 2, couleur_base)
        
        # 3. Unités de minutes (colonnes 4-5, 4 bits) - colonnes larges
        unites_minutes = minutes % 10
        ajouter_chiffre_large(unites_minutes, 4, 4, couleur_base)
        
        # 4. Secondes (1 colonne chacune) - colonnes étroites
        if Config.AFFICHER_SECONDES:
            # Dizaines de secondes (colonne 6, 3 bits)
            dizaines_secondes = secondes // 10
            ajouter_chiffre_etroit(dizaines_secondes, 3, 6, Config.COULEUR_SECONDES)
            
            # Unités de secondes (colonne 7, 4 bits)
            unites_secondes = secondes % 10
            ajouter_chiffre_etroit(unites_secondes, 4, 7, Config.COULEUR_SECONDES)
        
        # 5. Ajouter les indicateurs réseau (écrasent certaines LEDs si nécessaire)
        buffer = self.ajouter_indicateurs_reseau(buffer)
        
        return buffer
    
    def transition_fade(self, buffer_nouveau, duree):
        """
        Transition douce entre l'affichage actuel et le nouveau
        
        Args:
            buffer_nouveau: liste de 64 tuples (r,g,b)
            duree: durée en secondes
        """
        if duree <= 0:
            self.current_buffer = buffer_nouveau
            self._appliquer_buffer()
            return
        
        buffer_ancien = self.current_buffer
        ETAPE = 0.02  # 20ms par étape
        nb_etapes = max(1, int(duree / ETAPE))
        
        for etape in range(nb_etapes + 1):
            facteur = etape / nb_etapes
            
            for i in range(64):
                r1, g1, b1 = buffer_ancien[i]
                r2, g2, b2 = buffer_nouveau[i]
                
                r = int(r1 + (r2 - r1) * facteur)
                g = int(g1 + (g2 - g1) * facteur)
                b = int(b1 + (b2 - b1) * facteur)
                
                self.hardware.pixels[i] = (r, g, b)
            
            self.hardware.pixels.show()
            time.sleep(ETAPE)
        
        self.current_buffer = buffer_nouveau
    
    def afficher_heure(self, time_manager, avec_transition=True):
        """
        Affiche l'heure actuelle avec indicateurs réseau
        """
        heures, minutes, secondes, est_pm = time_manager.obtenir_heure_actuelle()
        timestamp = time_manager.obtenir_timestamp_actuel()
        
        nouveau_buffer = self.generer_buffer_bcd(
            heures, minutes, secondes, est_pm, timestamp
        )
        
        # Déterminer la durée de transition
        if not avec_transition:
            duree = 0
        else:
            # Dernière heure affichée
            if self.last_display:
                h_old, m_old, s_old, pm_old = self.last_display
                
                if heures != h_old:
                    duree = Config.FADE_HEURE
                elif minutes != m_old:
                    duree = Config.FADE_MINUTE
                elif secondes != s_old:
                    duree = Config.FADE_SECONDE
                else:
                    duree = 0
            else:
                duree = Config.FADE_ETAT
        
        self.transition_fade(nouveau_buffer, duree)
        self.last_display = (heures, minutes, secondes, est_pm)
    
    def afficher_erreur(self):
        """Affiche une croix rouge en cas d'erreur (démarrage seulement)"""
        self.hardware.pixels.fill((0, 0, 0))
        
        # Diagonale principale
        for i in range(8):
            idx = self.coords_to_index(i, i)
            if idx is not None:
                self.hardware.pixels[idx] = Config.COULEUR_ERREUR
        
        # Diagonale secondaire
        for i in range(8):
            idx = self.coords_to_index(i, 7 - i)
            if idx is not None:
                self.hardware.pixels[idx] = Config.COULEUR_ERREUR
        
        self.hardware.pixels.show()
        self.current_buffer = [(0, 0, 0)] * 64
    
    def eteindre(self, avec_transition=True):
        """Éteint l'affichage (indicateurs inclus)"""
        buffer_eteint = [(0, 0, 0)] * 64
        if avec_transition:
            self.transition_fade(buffer_eteint, Config.FADE_ETAT)
        else:
            self.current_buffer = buffer_eteint
            self._appliquer_buffer()
    
    def _appliquer_buffer(self):
        """Applique le buffer actuel à la matrice"""
        for i in range(64):
            self.hardware.pixels[i] = self.current_buffer[i]
        self.hardware.pixels.show()
    
    def mettre_a_jour_indicateurs(self):
        """Met à jour uniquement les indicateurs réseau"""
        if not self.network_tester or not self.current_buffer:
            return
        
        # Mettre à jour les couleurs des indicateurs dans le buffer actuel
        wifi_color = self.network_tester.get_wifi_color()
        internet_color = self.network_tester.get_internet_color()
        
        # WiFi
        idx_wifi1 = self.coords_to_index(Config.WIFI_LED_1[0], Config.WIFI_LED_1[1])
        idx_wifi2 = self.coords_to_index(Config.WIFI_LED_2[0], Config.WIFI_LED_2[1])
        
        if idx_wifi1 is not None:
            self.current_buffer[idx_wifi1] = wifi_color
            self.hardware.pixels[idx_wifi1] = wifi_color
        
        if idx_wifi2 is not None:
            self.current_buffer[idx_wifi2] = wifi_color
            self.hardware.pixels[idx_wifi2] = wifi_color
        
        # Internet
        idx_internet1 = self.coords_to_index(Config.INTERNET_LED_1[0], Config.INTERNET_LED_1[1])
        idx_internet2 = self.coords_to_index(Config.INTERNET_LED_2[0], Config.INTERNET_LED_2[1])
        
        if idx_internet1 is not None:
            self.current_buffer[idx_internet1] = internet_color
            self.hardware.pixels[idx_internet1] = internet_color
        
        if idx_internet2 is not None:
            self.current_buffer[idx_internet2] = internet_color
            self.hardware.pixels[idx_internet2] = internet_color
        
        self.hardware.pixels.show()