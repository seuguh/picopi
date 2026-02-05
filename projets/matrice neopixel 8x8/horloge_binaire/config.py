"""
Configuration du projet Horloge BCD
Avec monitoring réseau et indicateur de connexion
"""

class Config:
    # WiFi (chargés depuis secrets.py)
    WIFI_SSID = ""  # Remplacé par secrets.py
    WIFI_PASSWORD = ""  # Remplacé par secrets.py
    WIFI_TIMEOUT = 30
    
    # Monitoring réseau
    MONITORING_ACTIF = True              # Activer le monitoring
    INTERVALLE_MONITORING = 30           # Test toutes les 30 secondes
    TENTATIVES_RECONNEXION = 2           # 2 tentatives supplémentaires
    DELAI_RECONNEXION = 10               # 10 secondes entre les tentatives
    SEUIL_ERREUR = 3                     # 3 échecs consécutifs = erreur
    
    # NTP
    NTP_SERVER = "pool.ntp.org"
    TIMEZONE_OFFSET = 1  # UTC+1 pour Paris (hiver)
    NTP_SYNC_INTERVAL = 3600  # Resync toutes les heures
    
    # Matrice NeoPixel
    MATRICE_PIN = 0
    MATRICE_LEDS = 64
    MATRICE_LUMINOSITE = 0.1  # 0.0 à 1.0
    
    # Bouton
    BOUTON_PIN = 1
    BOUTON_PULLDOWN = True
    BOUTON_APPUI_LONG = 1.5  # secondes
    
    # Affichage
    FORMAT_12H = True
    AFFICHER_SECONDES = True
    REFRESH_RATE = 0.05  # 50ms
    
    # Animation des secondes
    ANIMATION_SECONDES = True      # Activer l'animation
    DUREE_ANIM_SECONDE = 0.5       # Durée par étape d'animation (0.5s)
    ANIM_PAR_SECONDE = 2           # 2 animations par seconde (une toutes les 0.5s)
    
    # Couleurs
    COULEUR_NORMALE = (0, 0, 100)      # Bleu (jour)
    COULEUR_NUIT = (20, 0, 0)          # Rouge sombre (22h-6h)
    COULEUR_SECONDES = (0, 50, 50)     # Cyan
    COULEUR_SECONDES_ANIM = (0, 80, 80) # Cyan plus clair pour l'animation
    COULEUR_ERREUR = (100, 0, 0)       # Rouge erreur WiFi/NTP
    COULEUR_WIFI_OK = (0, 50, 0)       # Vert pour WiFi OK
    COULEUR_WIFI_WARNING = (50, 50, 0) # Jaune pour avertissement
    COULEUR_WIFI_ERREUR = (80, 0, 0)   # Rouge pour erreur WiFi
    
    # Transitions SIMULTANÉES (fade out + fade in en même temps)
    FADE_SECONDE = 0.3    # Plus long pour être visible
    FADE_MINUTE = 0.5
    FADE_HEURE = 0.8
    FADE_ETAT = 0.6
    
    # Type d'effet de transition
    EFFET_TRANSITION = "crossfade"  # "crossfade", "vague", "balayage"
    
    # Debug
    DEBUG = True
    DEBUG_RESEAU = True  # Messages spécifiques au réseau