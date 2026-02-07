import board
import neopixel
import digitalio
import time
import random
import sys

try:
    import toml
    HAS_TOML = True
except ImportError:
    print("Avertissement: module toml non trouvé, utilisation des valeurs par défaut")
    HAS_TOML = False

# ===== CHARGEMENT CONFIGURATION =====
CONFIG_DEFAUT = {
    "system": {"nom": "Minuteur BCD", "debug": True},
    "matrice": {"pin": 0, "nombre_leds": 64, "lignes": 8, "colonnes": 8, 
                "luminosite": 0.3, "auto_write": False},
    "bouton": {"pin": 1, "type": "pulldown", "appui_long_duree": 1.5},
    "timer": {"duree_initiale": 3600, "duree_explosion": 10, "rafraichissement": 0.05},
    "transitions": {"seconde": 0.15, "minute": 0.3, "heure": 0.5, 
                   "etat": 0.4, "etape": 0.02},
    "couleurs": {
        "normale": {"r": 0, "g": 0, "b": 100},
        "pause": {"r": 100, "g": 100, "b": 0},
        "secondes": {"r": 0, "g": 50, "b": 50},
        "explosion": {
            "phase1": {"r": 50, "g": 50, "b": 0},
            "phase2": {"r": 50, "g": 0, "b": 0},
            "phase3": {"r": 0, "g": 0, "b": 50}
        }
    },
    "affichage_bcd": {
        "heures": [0, 1, 0, 7],
        "dizaines_minutes": [3, 4, 0, 7],
        "unites_minutes": [6, 7, 0, 7],
        "dizaines_secondes": [2, 2, 0, 5],
        "unites_secondes": [5, 5, 0, 7]
    },
    "animation": {
        "clignotement_rapide": 0.1,
        "extinction_facteur": 0.95,
        "etapes_extinction": 20
    }
}

def charger_configuration():
    """Charge la configuration depuis config.toml ou utilise les valeurs par défaut"""
    if not HAS_TOML:
        return CONFIG_DEFAUT
    
    try:
        with open('/config.toml', 'r') as f:
            config = toml.load(f)
        
        # Fusionner avec les valeurs par défaut pour les champs manquants
        config_final = fusionner_configurations(CONFIG_DEFAUT, config)
        
        if config_final["system"]["debug"]:
            print("Configuration chargée avec succès")
            print(f"Timer: {config_final['timer']['duree_initiale']} secondes")
        
        return config_final
        
    except Exception as e:
        print(f"Erreur chargement config: {e}, utilisation valeurs par défaut")
        return CONFIG_DEFAUT

def fusionner_configurations(defaut, utilisateur):
    """Fusionne récursivement deux dictionnaires de configuration"""
    resultat = defaut.copy()
    for cle, valeur in utilisateur.items():
        if cle in resultat and isinstance(resultat[cle], dict) and isinstance(valeur, dict):
            resultat[cle] = fusionner_configurations(resultat[cle], valeur)
        else:
            resultat[cle] = valeur
    return resultat

# Charger la configuration
config = charger_configuration()

# ===== VARIABLES DE CONFIGURATION =====
DUREE_TIMER = config["timer"]["duree_initiale"]
DUREE_EXPLOSION = config["timer"]["duree_explosion"]
APPUI_LONG = config["bouton"]["appui_long_duree"]
DUREE_FADE_SECONDE = config["transitions"]["seconde"]
DUREE_FADE_MINUTE = config["transitions"]["minute"]
DUREE_FADE_HEURE = config["transitions"]["heure"]
DUREE_FADE_ETAT = config["transitions"]["etat"]
DUREE_ETAPE = config["transitions"]["etape"]

# Couleurs configurées
COULEUR_NORMALE_BASE = (
    config["couleurs"]["normale"]["r"],
    config["couleurs"]["normale"]["g"],
    config["couleurs"]["normale"]["b"]
)
COULEUR_PAUSE_BASE = (
    config["couleurs"]["pause"]["r"],
    config["couleurs"]["pause"]["g"],
    config["couleurs"]["pause"]["b"]
)
COULEUR_SECONDES = (
    config["couleurs"]["secondes"]["r"],
    config["couleurs"]["secondes"]["g"],
    config["couleurs"]["secondes"]["b"]
)
COULEURS_EXPLOSION = [
    (
        config["couleurs"]["explosion"]["phase1"]["r"],
        config["couleurs"]["explosion"]["phase1"]["g"],
        config["couleurs"]["explosion"]["phase1"]["b"]
    ),
    (
        config["couleurs"]["explosion"]["phase2"]["r"],
        config["couleurs"]["explosion"]["phase2"]["g"],
        config["couleurs"]["explosion"]["phase2"]["b"]
    ),
    (
        config["couleurs"]["explosion"]["phase3"]["r"],
        config["couleurs"]["explosion"]["phase3"]["g"],
        config["couleurs"]["explosion"]["phase3"]["b"]
    )
]

# Configuration BCD
BCD_CONFIG = config["affichage_bcd"]

# ===== INITIALISATION MATÉRIEL =====
# Matrice NeoPixel
pin_matrice = getattr(board, f"GP{config['matrice']['pin']}")
pixels = neopixel.NeoPixel(
    pin_matrice,
    config["matrice"]["nombre_leds"],
    brightness=config["matrice"]["luminosite"],
    auto_write=config["matrice"]["auto_write"]
)

# Bouton
pin_bouton = getattr(board, f"GP{config['bouton']['pin']}")
touch = digitalio.DigitalInOut(pin_bouton)
touch.direction = digitalio.Direction.INPUT

# Configuration du pull du bouton
type_bouton = config["bouton"]["type"]
if type_bouton == "pulldown":
    touch.pull = digitalio.Pull.DOWN
elif type_bouton == "pullup":
    touch.pull = digitalio.Pull.UP
# else: none, pas de pull

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
    return x * 8 + y

def clear_matrix():
    """Éteint toutes les LEDs"""
    pixels.fill((0, 0, 0))
    pixels.show()

def interpoler_couleur(couleur1, couleur2, facteur):
    """
    Interpole entre deux couleurs selon un facteur (0.0 à 1.0)
    facteur = 0.0 → couleur1
    facteur = 1.0 → couleur2
    """
    r1, g1, b1 = couleur1
    r2, g2, b2 = couleur2
    r = int(r1 + (r2 - r1) * facteur)
    g = int(g1 + (g2 - g1) * facteur)
    b = int(b1 + (b2 - b1) * facteur)
    return (r, g, b)

def afficher_zone(x_debut, x_fin, y_debut, y_fin, couleur, buffer):
    """Affiche une zone rectangulaire dans le buffer"""
    for x in range(x_debut, x_fin + 1):
        for y in range(y_debut, y_fin + 1):
            idx = coords_to_index(x, y)
            if idx is not None:
                buffer[idx] = couleur

def generer_affichage_bcd(secondes_totales, couleur_base):
    """
    Génère un buffer d'affichage pour le temps donné
    Retourne un tableau de 64 couleurs RGB
    """
    # Calcul des composantes temporelles
    heures = secondes_totales // 3600
    minutes = (secondes_totales % 3600) // 60
    secondes = secondes_totales % 60
    
    dizaines_min = minutes // 10
    unites_min = minutes % 10
    dizaines_sec = secondes // 10
    unites_sec = secondes % 10
    
    # Créer un buffer pour le nouvel affichage
    buffer = [(0, 0, 0)] * 64
    
    # ===== Affichage des heures =====
    heures_affichage = heures % 10
    for bit in range(4):
        if heures_affichage & (1 << bit):
            y_base = bit * 2
            x1, x2, y1, y2 = BCD_CONFIG["heures"]
            afficher_zone(x1, x2, y_base, y_base + 1, couleur_base, buffer)
    
    # ===== Affichage des dizaines de secondes =====
    for bit in range(3):
        if dizaines_sec & (1 << bit):
            y_base = bit * 2
            x1, x2, y1, y2 = BCD_CONFIG["dizaines_secondes"]
            afficher_zone(x1, x2, y_base, y_base + 1, COULEUR_SECONDES, buffer)
    
    # ===== Affichage des dizaines de minutes =====
    for bit in range(4):
        if dizaines_min & (1 << bit):
            y_base = bit * 2
            x1, x2, y1, y2 = BCD_CONFIG["dizaines_minutes"]
            afficher_zone(x1, x2, y_base, y_base + 1, couleur_base, buffer)
    
    # ===== Affichage des unités de secondes =====
    for bit in range(4):
        if unites_sec & (1 << bit):
            y_base = bit * 2
            x1, x2, y1, y2 = BCD_CONFIG["unites_secondes"]
            afficher_zone(x1, x2, y_base, y_base + 1, COULEUR_SECONDES, buffer)
    
    # ===== Affichage des unités de minutes =====
    for bit in range(4):
        if unites_min & (1 << bit):
            y_base = bit * 2
            x1, x2, y1, y2 = BCD_CONFIG["unites_minutes"]
            afficher_zone(x1, x2, y_base, y_base + 1, couleur_base, buffer)
    
    return buffer

def transition_fade(buffer_source, buffer_dest, duree):
    """
    Effectue une transition douce (fade) entre deux états d'affichage
    """
    etapes = int(duree / DUREE_ETAPE)
    if etapes < 1:
        etapes = 1
    
    for etape in range(etapes + 1):
        facteur = etape / etapes
        for i in range(64):
            couleur = interpoler_couleur(buffer_source[i], buffer_dest[i], facteur)
            pixels[i] = couleur
        pixels.show()
        time.sleep(DUREE_ETAPE)

def detecter_type_changement(ancien_temps, nouveau_temps):
    """
    Détecte quel type de changement s'est produit (seconde, minute, heure)
    Retourne la durée de fade appropriée
    """
    if ancien_temps is None:
        return DUREE_FADE_ETAT
    
    ancien_heures = ancien_temps // 3600
    nouveau_heures = nouveau_temps // 3600
    ancien_minutes = (ancien_temps % 3600) // 60
    nouveau_minutes = (nouveau_temps % 3600) // 60
    
    if ancien_heures != nouveau_heures:
        return DUREE_FADE_HEURE
    
    if ancien_minutes != nouveau_minutes:
        return DUREE_FADE_MINUTE
    
    return DUREE_FADE_SECONDE

def afficher_bcd(secondes_totales, couleur_base, avec_transition=False, ancien_temps=None):
    """
    Affiche le temps en BCD avec option de transition fade adaptative
    """
    global buffer_affichage_actuel
    
    # Générer le nouvel affichage
    nouveau_buffer = generer_affichage_bcd(secondes_totales, couleur_base)
    
    if avec_transition and buffer_affichage_actuel is not None:
        duree = detecter_type_changement(ancien_temps, secondes_totales)
        transition_fade(buffer_affichage_actuel, nouveau_buffer, duree)
    else:
        for i in range(64):
            pixels[i] = nouveau_buffer[i]
        pixels.show()
    
    buffer_affichage_actuel = nouveau_buffer

def effet_explosion():
    """Effet d'explosion de pixels colorés à la fin du timer"""
    debut = time.monotonic()
    duree_phase = DUREE_EXPLOSION / 3
    
    # Phase 1: Remplissage progressif aléatoire
    positions = list(range(64))
    for i in range(len(positions)-1, 0, -1):
        j = random.randint(0, i)
        positions[i], positions[j] = positions[j], positions[i]
    
    delai_phase1 = duree_phase / 64
    for i in range(64):
        couleur = COULEURS_EXPLOSION[random.randint(0, len(COULEURS_EXPLOSION)-1)]
        pixels[positions[i]] = couleur
        pixels.show()
        time.sleep(delai_phase1)
    
    # Phase 2: Clignotements
    nb_clignotements = int(duree_phase / (config["animation"]["clignotement_rapide"] * 2))
    for _ in range(nb_clignotements):
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(config["animation"]["clignotement_rapide"])
        for i in range(64):
            couleur = COULEURS_EXPLOSION[random.randint(0, len(COULEURS_EXPLOSION)-1)]
            pixels[i] = couleur
        pixels.show()
        time.sleep(config["animation"]["clignotement_rapide"])
    
    # Phase 3: Extinction progressive
    nb_etapes = config["animation"]["etapes_extinction"]
    facteur = config["animation"]["extinction_facteur"]
    delai_extinction = duree_phase / nb_etapes
    
    for _ in range(nb_etapes):
        for i in range(64):
            r, g, b = pixels[i]
            pixels[i] = (int(r*facteur), int(g*facteur), int(b*facteur))
        pixels.show()
        time.sleep(delai_extinction)
    
    clear_matrix()
    
    if config["system"]["debug"]:
        duree_totale = time.monotonic() - debut
        print(f"Explosion terminée en {duree_totale:.1f}s")

def detecter_appui():
    """
    Détecte un appui sur le bouton et retourne:
    - None si pas d'appui
    - "court" si appui court
    - "long" si appui long
    """
    if type_bouton == "pullup":
        # Pour pullup, le bouton est actif bas
        if touch.value:  # Bouton relâché
            return None
    else:
        # Pour pulldown, le bouton est actif haut
        if not touch.value:  # Bouton relâché
            return None
    
    # Bouton pressé, mesurer la durée
    debut = time.monotonic()
    while True:
        time.sleep(0.01)
        if type_bouton == "pullup":
            if touch.value:  # Bouton relâché
                break
        else:
            if not touch.value:  # Bouton relâché
                break
        
        if time.monotonic() - debut > APPUI_LONG:
            # Attendre le relâchement
            while (type_bouton == "pullup" and not touch.value) or \
                  (type_bouton != "pullup" and touch.value):
                time.sleep(0.01)
            return "long"
    
    duree = time.monotonic() - debut
    return "long" if duree >= APPUI_LONG else "court"

# ===== PROGRAMME PRINCIPAL =====
ETAT_ARRET = 0
ETAT_EN_COURS = 1
ETAT_PAUSE = 2
ETAT_TERMINE = 3

etat = ETAT_ARRET
temps_restant = DUREE_TIMER
temps_precedent = None
dernier_update = 0
dernier_affichage = -1
buffer_affichage_actuel = None

if config["system"]["debug"]:
    print("Minuteur BCD démarré")
    print(f"Durée configurée: {DUREE_TIMER} secondes")
    print(f"Bouton sur GP{config['bouton']['pin']} (type: {type_bouton})")
    print(f"Matrice sur GP{config['matrice']['pin']} ({config['matrice']['lignes']}x{config['matrice']['colonnes']})")

clear_matrix()

while True:
    appui = detecter_appui()
    temps_actuel = time.monotonic()
    
    # Gestion des appuis
    if appui:
        if etat == ETAT_ARRET:
            if appui == "court":
                etat = ETAT_EN_COURS
                temps_restant = DUREE_TIMER
                temps_precedent = None
                dernier_update = temps_actuel
                afficher_bcd(temps_restant, COULEUR_NORMALE_BASE, avec_transition=True, ancien_temps=None)
                temps_precedent = temps_restant
                dernier_affichage = temps_restant
                if config["system"]["debug"]:
                    print("Timer démarré")
            elif appui == "long":
                if buffer_affichage_actuel:
                    buffer_noir = [(0, 0, 0)] * 64
                    transition_fade(buffer_affichage_actuel, buffer_noir, DUREE_FADE_ETAT)
                else:
                    clear_matrix()
                buffer_affichage_actuel = None
                temps_precedent = None
                if config["system"]["debug"]:
                    print("Affichage éteint")
        
        elif etat == ETAT_EN_COURS:
            if appui == "court":
                etat = ETAT_PAUSE
                afficher_bcd(temps_restant, COULEUR_PAUSE_BASE, avec_transition=True, ancien_temps=temps_precedent)
                temps_precedent = temps_restant
                dernier_affichage = temps_restant
                if config["system"]["debug"]:
                    print(f"Pause - Temps restant: {temps_restant}s")
        
        elif etat == ETAT_PAUSE:
            if appui == "court":
                etat = ETAT_EN_COURS
                dernier_update = temps_actuel
                afficher_bcd(temps_restant, COULEUR_NORMALE_BASE, avec_transition=True, ancien_temps=temps_precedent)
                temps_precedent = temps_restant
                dernier_affichage = temps_restant
                if config["system"]["debug"]:
                    print("Reprise du timer")
            elif appui == "long":
                buffer_noir = [(0, 0, 0)] * 64
                if buffer_affichage_actuel:
                    transition_fade(buffer_affichage_actuel, buffer_noir, duree=DUREE_FADE_ETAT/2)
                etat = ETAT_ARRET
                temps_restant = DUREE_TIMER
                temps_precedent = None
                time.sleep(0.1)
                afficher_bcd(temps_restant, COULEUR_NORMALE_BASE, avec_transition=True, ancien_temps=None)
                temps_precedent = temps_restant
                dernier_affichage = temps_restant
                if config["system"]["debug"]:
                    print("Reset du timer")
        
        elif etat == ETAT_TERMINE:
            if appui == "long":
                buffer_noir = [(0, 0, 0)] * 64
                if buffer_affichage_actuel:
                    transition_fade(buffer_affichage_actuel, buffer_noir, DUREE_FADE_ETAT)
                else:
                    clear_matrix()
                etat = ETAT_ARRET
                temps_restant = DUREE_TIMER
                buffer_affichage_actuel = None
                temps_precedent = None
                dernier_affichage = -1
                if config["system"]["debug"]:
                    print("Extinction - Timer réinitialisé")
    
    # Mise à jour du décompte
    if etat == ETAT_EN_COURS:
        if temps_actuel - dernier_update >= 1.0:
            ancien_temps = temps_restant
            temps_restant -= 1
            dernier_update = temps_actuel
            
            if temps_restant <= 0:
                temps_restant = 0
                etat = ETAT_TERMINE
                buffer_affichage_actuel = None
                temps_precedent = None
                if config["system"]["debug"]:
                    print("Timer terminé!")
                effet_explosion()
            else:
                if temps_restant != dernier_affichage:
                    afficher_bcd(temps_restant, COULEUR_NORMALE_BASE, avec_transition=True, ancien_temps=ancien_temps)
                    temps_precedent = temps_restant
                    dernier_affichage = temps_restant
    
    time.sleep(config["timer"]["rafraichissement"])
