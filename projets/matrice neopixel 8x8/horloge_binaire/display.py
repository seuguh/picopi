"""
Gestion de l'affichage BCD sur la matrice NeoPixel
Avec animation des secondes par déplacement de LED
"""

import time
import math
from config import Config

class DisplayManager:
    def __init__(self, hardware):
        self.hardware = hardware
        self.last_display = None
        self.current_buffer = [(0, 0, 0)] * 64
        self.en_transition = False
        
        # Animation des secondes
        self.animation_seconde_active = False
        self.phase_animation = 0  # 0 ou 1 (2 phases par seconde)
        self.last_animation_time = 0
    
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
    
    def generer_buffer_bcd(self, heures, minutes, secondes, est_pm, timestamp, animation_phase=0):
        """
        Génère un buffer de 64 LEDs pour l'heure donnée
        Avec animation des secondes par déplacement de LED
        
        animation_phase: 0 = début de seconde, 1 = milieu de seconde
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
                    for row in range(bit * 2, bit * 2 + 2):
                        for col_offset in range(2):
                            col = colonne_debut + col_offset
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
        
        def ajouter_chiffre_etroit_anime(chiffre, bits, colonne, couleur, couleur_anim, phase):
            """
            Ajoute un chiffre BCD sur 1 colonne (secondes) avec animation
            phase: 0 = LED du bas, 1 = LED du haut pour l'animation
            """
            for bit in range(bits):
                if (chiffre >> bit) & 1:  # Vérifier si le bit est à 1
                    # Allumer 2 LEDs superposées pour ce bit
                    for row in range(bit * 2, bit * 2 + 2):
                        idx = self.coords_to_index(colonne, row)
                        if idx is not None:
                            # Animation: alterner entre couleur normale et couleur animée
                            if Config.ANIMATION_SECONDES and phase == 0:
                                # Phase 0: LED du bas en couleur animée
                                if row == bit * 2:  # LED du bas
                                    buffer[idx] = couleur_anim
                                else:  # LED du haut
                                    buffer[idx] = couleur
                            elif Config.ANIMATION_SECONDES and phase == 1:
                                # Phase 1: LED du haut en couleur animée
                                if row == bit * 2 + 1:  # LED du haut
                                    buffer[idx] = couleur_anim
                                else:  # LED du bas
                                    buffer[idx] = couleur
                            else:
                                # Pas d'animation
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
            
            if Config.ANIMATION_SECONDES:
                ajouter_chiffre_etroit_anime(dizaines_secondes, 3, 6, 
                                           Config.COULEUR_SECONDES,
                                           Config.COULEUR_SECONDES_ANIM,
                                           animation_phase)
            else:
                ajouter_chiffre_etroit(dizaines_secondes, 3, 6, Config.COULEUR_SECONDES)
            
            # Unités de secondes (colonne 7, 4 bits)
            unites_secondes = secondes % 10
            
            if Config.ANIMATION_SECONDES:
                ajouter_chiffre_etroit_anime(unites_secondes, 4, 7,
                                           Config.COULEUR_SECONDES,
                                           Config.COULEUR_SECONDES_ANIM,
                                           animation_phase)
            else:
                ajouter_chiffre_etroit(unites_secondes, 4, 7, Config.COULEUR_SECONDES)
        
        return buffer
    
    def animation_seconde_update(self):
        """
        Met à jour l'animation des secondes
        Retourne True si l'animation a changé de phase
        """
        if not Config.ANIMATION_SECONDES:
            return False
        
        temps_actuel = time.monotonic()
        temps_ecoule = temps_actuel - self.last_animation_time
        
        if temps_ecoule >= Config.DUREE_ANIM_SECONDE:
            # Changer de phase
            self.phase_animation = (self.phase_animation + 1) % Config.ANIM_PAR_SECONDE
            self.last_animation_time = temps_actuel
            return True
        
        return False
    
    def afficher_heure_animee(self, time_manager):
        """
        Affiche l'heure actuelle avec animation des secondes
        """
        if self.en_transition:
            return
        
        # Mettre à jour l'animation des secondes
        animation_changed = self.animation_seconde_update()
        
        heures, minutes, secondes, est_pm = time_manager.obtenir_heure_actuelle()
        timestamp = time_manager.obtenir_timestamp_actuel()
        
        # Générer le buffer avec la phase d'animation actuelle
        nouveau_buffer = self.generer_buffer_bcd(
            heures, minutes, secondes, est_pm, timestamp, self.phase_animation
        )
        
        # Vérifier si l'heure a changé (nouvelle seconde)
        heure_actuelle = (heures, minutes, secondes, est_pm)
        
        if heure_actuelle != self.last_display:
            # Nouvelle seconde: transition normale
            self.transition_crossfade(nouveau_buffer, Config.FADE_SECONDE)
            self.last_display = heure_actuelle
            
            if Config.DEBUG:
                am_pm = "PM" if est_pm else "AM"
                print(f"Nouvelle seconde: {heures:02d}:{minutes:02d}:{secondes:02d} {am_pm}")
        
        elif animation_changed:
            # Seulement l'animation a changé: mise à jour directe
            self.current_buffer = nouveau_buffer
            self._appliquer_buffer()
            
            if Config.DEBUG and secondes % 10 == 0:
                print(f"Animation seconde phase: {self.phase_animation}")
    
    def transition_crossfade(self, buffer_nouveau, duree):
        """
        Transition CROSSFADE simultanée
        L'ancien fade out pendant que le nouveau fade IN
        """
        if self.en_transition or duree <= 0:
            self.current_buffer = buffer_nouveau
            self._appliquer_buffer()
            return
        
        self.en_transition = True
        buffer_ancien = self.current_buffer.copy()
        
        ETAPE = 0.02  # 20ms par étape
        nb_etapes = max(1, int(duree / ETAPE))
        
        for etape in range(nb_etapes + 1):
            facteur = etape / nb_etapes
            
            # Pour chaque LED, mélanger ancien et nouveau
            for i in range(64):
                r1, g1, b1 = buffer_ancien[i]
                r2, g2, b2 = buffer_nouveau[i]
                
                # Ancien: fade OUT (1 -> 0)
                r_out = int(r1 * (1 - facteur))
                g_out = int(g1 * (1 - facteur))
                b_out = int(b1 * (1 - facteur))
                
                # Nouveau: fade IN (0 -> 1)
                r_in = int(r2 * facteur)
                g_in = int(g2 * facteur)
                b_in = int(b2 * facteur)
                
                # Combiner les deux
                self.hardware.pixels[i] = (
                    min(255, r_out + r_in),
                    min(255, g_out + g_in),
                    min(255, b_out + b_in)
                )
            
            self.hardware.pixels.show()
            time.sleep(ETAPE)
        
        self.current_buffer = buffer_nouveau
        self.en_transition = False
    
    def afficher_heure(self, time_manager, avec_transition=True):
        """
        Affiche l'heure actuelle (version compatible)
        """
        if Config.ANIMATION_SECONDES:
            # Utiliser la version animée
            self.afficher_heure_animee(time_manager)
            return
        
        # Version sans animation (pour compatibilité)
        heures, minutes, secondes, est_pm = time_manager.obtenir_heure_actuelle()
        timestamp = time_manager.obtenir_timestamp_actuel()
        
        nouveau_buffer = self.generer_buffer_bcd(
            heures, minutes, secondes, est_pm, timestamp
        )
        
        # Déterminer la durée et le type de transition
        if not avec_transition:
            self.current_buffer = nouveau_buffer
            self._appliquer_buffer()
        
        else:
            # Dernière heure affichée
            if self.last_display:
                h_old, m_old, s_old, pm_old = self.last_display
                
                # Choisir durée selon le changement
                if heures != h_old:
                    duree = Config.FADE_HEURE
                elif minutes != m_old:
                    duree = Config.FADE_MINUTE
                elif secondes != s_old:
                    duree = Config.FADE_SECONDE
                else:
                    duree = 0
            else:
                # Premier affichage
                duree = Config.FADE_ETAT
            
            # Appliquer la transition
            if duree > 0:
                self.transition_crossfade(nouveau_buffer, duree)
            else:
                self.current_buffer = nouveau_buffer
                self._appliquer_buffer()
        
        self.last_display = (heures, minutes, secondes, est_pm)
    
    def afficher_erreur(self):
        """Affiche une croix rouge en cas d'erreur avec effet"""
        if self.en_transition:
            return
        
        self.en_transition = True
        
        # Effet de clignotement
        for i in range(3):
            # Croix rouge
            self.hardware.pixels.fill((0, 0, 0))
            for j in range(8):
                idx1 = self.coords_to_index(j, j)
                idx2 = self.coords_to_index(j, 7 - j)
                if idx1 is not None:
                    self.hardware.pixels[idx1] = Config.COULEUR_ERREUR
                if idx2 is not None:
                    self.hardware.pixels[idx2] = Config.COULEUR_ERREUR
            self.hardware.pixels.show()
            time.sleep(0.3)
            
            # Noir
            self.hardware.pixels.fill((0, 0, 0))
            self.hardware.pixels.show()
            time.sleep(0.2)
        
        # Croix fixe
        for j in range(8):
            idx1 = self.coords_to_index(j, j)
            idx2 = self.coords_to_index(j, 7 - j)
            if idx1 is not None:
                self.hardware.pixels[idx1] = Config.COULEUR_ERREUR
            if idx2 is not None:
                self.hardware.pixels[idx2] = Config.COULEUR_ERREUR
        
        self.hardware.pixels.show()
        self.current_buffer = [(0, 0, 0)] * 64
        self.en_transition = False
    
    def eteindre(self, avec_transition=True):
        """Éteint l'affichage avec transition"""
        if self.en_transition:
            return
        
        buffer_eteint = [(0, 0, 0)] * 64
        
        if avec_transition:
            self.transition_crossfade(buffer_eteint, Config.FADE_ETAT)
        else:
            self.current_buffer = buffer_eteint
            self._appliquer_buffer()
    
    def allumer(self, time_manager, avec_transition=True):
        """Allume l'affichage depuis l'état éteint"""
        if self.en_transition:
            return
        
        # Réinitialiser l'animation
        self.last_animation_time = time.monotonic()
        self.phase_animation = 0
        
        heures, minutes, secondes, est_pm = time_manager.obtenir_heure_actuelle()
        timestamp = time_manager.obtenir_timestamp_actuel()
        
        nouveau_buffer = self.generer_buffer_bcd(
            heures, minutes, secondes, est_pm, timestamp, self.phase_animation
        )
        
        if avec_transition:
            self.transition_crossfade(nouveau_buffer, Config.FADE_ETAT)
        else:
            self.current_buffer = nouveau_buffer
            self._appliquer_buffer()
        
        self.last_display = (heures, minutes, secondes, est_pm)
    
    def _appliquer_buffer(self):
        """Applique le buffer actuel à la matrice"""
        for i in range(64):
            self.hardware.pixels[i] = self.current_buffer[i]
        self.hardware.pixels.show()