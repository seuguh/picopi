import board
import neopixel
import digitalio
import time
import random

# ===== CONFIGURATION =====
DUREE_TIMER = 3600  # Durée du timer en secondes (modifiable)
DUREE_EXPLOSION = 10  # Durée de l'effet d'explosion en secondes
APPUI_LONG = 1.5  # Durée en secondes pour considérer un appui comme "long"

# Couleurs de base
COULEUR_NORMALE_BASE = (0, 0, 100)      # Bleu (valeur max)
COULEUR_PAUSE_BASE = (100, 100, 0)       # Jaune (valeur max)
COULEUR_SECONDES = (0, 50, 50)           # Cyan pour les secondes
COULEURS_EXPLOSION = [
    (50, 50, 0),   # Jaune
    (50, 0, 0),    # Rouge
    (0, 0, 50)     # Bleu
]

# ===== INITIALISATION MATÉRIEL =====
# Matrice 8x8 = 64 LEDs sur GP0
pixels = neopixel.NeoPixel(board.GP0, 64, brightness=0.3, auto_write=False)

# Bouton touch sur GP1
touch = digitalio.DigitalInOut(board.GP1)
touch.direction = digitalio.Direction.INPUT
touch.pull = digitalio.Pull.DOWN

# ===== FONCTIONS UTILITAIRES =====

def coords_to_index(x, y):
    """
    Convertit coordonnées (x,y) en index LED
    x=0, y=0 = bas gauche
    x=7, y=7 = haut droite
    Matrice organisée en colonnes
    """
    if x < 0 or x > 7 or y < 0 or y > 7:
        return None
    # Chaque colonne monte de bas en haut
    return x * 8 + y

def clear_matrix():
    """Éteint toutes les LEDs"""
    pixels.fill((0, 0, 0))
    pixels.show()

def afficher_bloc_2x2(x_base, y_base, couleur):
    """
    Affiche un bloc de 2×2 LEDs à partir de la position (x_base, y_base)
    """
    for dx in range(2):
        for dy in range(2):
            idx = coords_to_index(x_base + dx, y_base + dy)
            if idx is not None:
                pixels[idx] = couleur

def afficher_bloc_1x2(x, y_base, couleur):
    """
    Affiche un bloc de 1×2 LEDs (vertical) à partir de la position (x, y_base)
    """
    for dy in range(2):
        idx = coords_to_index(x, y_base + dy)
        if idx is not None:
            pixels[idx] = couleur

def afficher_bcd(secondes_totales, couleur_base):
    """
    Affiche le temps en BCD avec des blocs de 2×2 LEDs
    Format: HH:MM:SS avec les secondes en binaire sur les colonnes de séparation
    
    Layout sur la matrice 8x8:
    - Colonnes 0-1: Heures (0-9) en BCD (blocs 2×2)
    - Colonne 2: Dizaines de secondes (0-5) en binaire sur 3 bits (blocs 1×2)
    - Colonnes 3-4: Dizaines de minutes (0-5) en BCD (blocs 2×2)
    - Colonne 5: Unités de secondes (0-9) en binaire sur 4 bits (blocs 1×2)
    - Colonnes 6-7: Unités de minutes (0-9) en BCD (blocs 2×2)
    """
    # NE PAS effacer la matrice pour éviter le scintillement
    # On va mettre à jour pixel par pixel
    
    # Calcul des composantes temporelles
    heures = secondes_totales // 3600
    minutes = (secondes_totales % 3600) // 60
    secondes = secondes_totales % 60
    
    dizaines_min = minutes // 10
    unites_min = minutes % 10
    dizaines_sec = secondes // 10
    unites_sec = secondes % 10
    
    # Créer un buffer temporaire pour le nouvel affichage
    nouveau_affichage = [(0, 0, 0)] * 64
    
    # ===== Affichage des heures (colonnes 0-1) =====
    heures_affichage = heures % 10
    for bit in range(4):
        if heures_affichage & (1 << bit):
            y_base = bit * 2
            for dx in range(2):
                for dy in range(2):
                    idx = coords_to_index(0 + dx, y_base + dy)
                    if idx is not None:
                        nouveau_affichage[idx] = couleur_base
    
    # ===== Affichage des dizaines de secondes (colonne 2) =====
    # 3 bits suffisent (0-5), affichés en blocs 1×2 verticaux
    for bit in range(3):
        if dizaines_sec & (1 << bit):
            y_base = bit * 2
            for dy in range(2):
                idx = coords_to_index(2, y_base + dy)
                if idx is not None:
                    nouveau_affichage[idx] = COULEUR_SECONDES
    
    # ===== Affichage des dizaines de minutes (colonnes 3-4) =====
    for bit in range(4):
        if dizaines_min & (1 << bit):
            y_base = bit * 2
            for dx in range(2):
                for dy in range(2):
                    idx = coords_to_index(3 + dx, y_base + dy)
                    if idx is not None:
                        nouveau_affichage[idx] = couleur_base
    
    # ===== Affichage des unités de secondes (colonne 5) =====
    # 4 bits (0-9), affichés en blocs 1×2 verticaux
    for bit in range(4):
        if unites_sec & (1 << bit):
            y_base = bit * 2
            for dy in range(2):
                idx = coords_to_index(5, y_base + dy)
                if idx is not None:
                    nouveau_affichage[idx] = COULEUR_SECONDES
    
    # ===== Affichage des unités de minutes (colonnes 6-7) =====
    for bit in range(4):
        if unites_min & (1 << bit):
            y_base = bit * 2
            for dx in range(2):
                for dy in range(2):
                    idx = coords_to_index(6 + dx, y_base + dy)
                    if idx is not None:
                        nouveau_affichage[idx] = couleur_base
    
    # Mettre à jour uniquement les pixels qui ont changé
    for i in range(64):
        if pixels[i] != nouveau_affichage[i]:
            pixels[i] = nouveau_affichage[i]
    
    pixels.show()

def effet_explosion():
    """Effet d'explosion de pixels colorés à la fin du timer"""
    debut = time.monotonic()
    duree_phase = DUREE_EXPLOSION / 3  # Diviser en 3 phases égales
    
    # Phase 1: Remplissage progressif aléatoire
    positions = list(range(64))
    # Shuffle manuel car random.shuffle n'existe pas en CircuitPython
    for i in range(len(positions)-1, 0, -1):
        j = random.randint(0, i)
        positions[i], positions[j] = positions[j], positions[i]
    
    delai_phase1 = duree_phase / 64  # Temps par pixel
    for i in range(64):
        couleur = COULEURS_EXPLOSION[random.randint(0, len(COULEURS_EXPLOSION)-1)]
        pixels[positions[i]] = couleur
        pixels.show()
        time.sleep(delai_phase1)
    
    # Phase 2: Clignotements
    nb_clignotements = int(duree_phase / 0.2)  # Un clignotement toutes les 0.2s
    for _ in range(nb_clignotements):
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.1)
        for i in range(64):
            couleur = COULEURS_EXPLOSION[random.randint(0, len(COULEURS_EXPLOSION)-1)]
            pixels[i] = couleur
        pixels.show()
        time.sleep(0.1)
    
    # Phase 3: Extinction progressive
    nb_etapes = int(duree_phase / 0.05)
    facteur = 0.95 ** (1.0 / nb_etapes)  # Calculer le facteur pour atteindre ~0 à la fin
    for _ in range(nb_etapes):
        for i in range(64):
            r, g, b = pixels[i]
            pixels[i] = (int(r*facteur), int(g*facteur), int(b*facteur))
        pixels.show()
        time.sleep(0.05)
    
    clear_matrix()
    
    duree_totale = time.monotonic() - debut
    print(f"Explosion terminée en {duree_totale:.1f}s")

def detecter_appui():
    """
    Détecte un appui sur le bouton et retourne:
    - None si pas d'appui
    - "court" si appui court
    - "long" si appui long
    """
    if not touch.value:
        return None
    
    # Bouton pressé, mesurer la durée
    debut = time.monotonic()
    while touch.value:  # Tant que le bouton est pressé
        time.sleep(0.01)
        if time.monotonic() - debut > APPUI_LONG:
            # Attendre le relâchement
            while touch.value:
                time.sleep(0.01)
            return "long"
    
    duree = time.monotonic() - debut
    return "long" if duree >= APPUI_LONG else "court"

# ===== PROGRAMME PRINCIPAL =====

# États possibles
ETAT_ARRET = 0      # Timer à zéro, en attente
ETAT_EN_COURS = 1   # Décompte en cours
ETAT_PAUSE = 2      # En pause
ETAT_TERMINE = 3    # Timer terminé

etat = ETAT_ARRET
temps_restant = DUREE_TIMER
dernier_update = 0
dernier_affichage = -1  # Pour éviter les rafraîchissements inutiles

print("Minuteur BCD démarré - Format HH:MM:SS")
print(f"Durée configurée: {DUREE_TIMER} secondes ({DUREE_TIMER//3600}h {(DUREE_TIMER%3600)//60}m {DUREE_TIMER%60}s)")
print(f"Durée explosion: {DUREE_EXPLOSION} secondes")
print("Les secondes s'affichent sur les colonnes de séparation")
print("Appui court: démarrer/pause/reprendre")
print(f"Appui long ({APPUI_LONG}s): reset ou extinction")

clear_matrix()

while True:
    appui = detecter_appui()
    temps_actuel = time.monotonic()
    
    # ===== GESTION DES APPUIS =====
    if appui:
        if etat == ETAT_ARRET:
            if appui == "court":
                # Démarrer le timer
                etat = ETAT_EN_COURS
                temps_restant = DUREE_TIMER
                dernier_update = temps_actuel
                dernier_affichage = -1
                print("Timer démarré")
            elif appui == "long":
                # Éteindre l'affichage
                clear_matrix()
                dernier_affichage = -1
                print("Affichage éteint")
        
        elif etat == ETAT_EN_COURS:
            if appui == "court":
                # Mettre en pause
                etat = ETAT_PAUSE
                print(f"Pause - Temps restant: {temps_restant}s")
        
        elif etat == ETAT_PAUSE:
            if appui == "court":
                # Reprendre
                etat = ETAT_EN_COURS
                dernier_update = temps_actuel
                print("Reprise du timer")
            elif appui == "long":
                # Reset
                etat = ETAT_ARRET
                temps_restant = DUREE_TIMER
                clear_matrix()
                dernier_affichage = -1
                print("Reset du timer")
        
        elif etat == ETAT_TERMINE:
            if appui == "long":
                # Éteindre et retourner à l'état d'arrêt
                clear_matrix()
                etat = ETAT_ARRET
                temps_restant = DUREE_TIMER
                dernier_affichage = -1
                print("Extinction - Timer réinitialisé")
    
    # ===== MISE À JOUR DU DÉCOMPTE =====
    if etat == ETAT_EN_COURS:
        if temps_actuel - dernier_update >= 1.0:
            temps_restant -= 1
            dernier_update = temps_actuel
            
            if temps_restant <= 0:
                temps_restant = 0
                etat = ETAT_TERMINE
                dernier_affichage = -1
                print("Timer terminé!")
                effet_explosion()
            else:
                # Afficher seulement si le temps a changé
                if temps_restant != dernier_affichage:
                    afficher_bcd(temps_restant, COULEUR_NORMALE_BASE)
                    dernier_affichage = temps_restant
    
    # ===== MISE À JOUR DE L'AFFICHAGE =====
    if etat == ETAT_PAUSE:
        if temps_restant != dernier_affichage:
            afficher_bcd(temps_restant, COULEUR_PAUSE_BASE)
            dernier_affichage = temps_restant
    elif etat == ETAT_ARRET and temps_restant == DUREE_TIMER:
        if dernier_affichage != temps_restant:
            afficher_bcd(temps_restant, COULEUR_NORMALE_BASE)
            dernier_affichage = temps_restant
    
    time.sleep(0.05)  # Petit délai pour ne pas surcharger le CPU