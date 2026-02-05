"""
Configuration du projet Horloge BCD
"""

class Config:
    # WiFi (chargés depuis secrets.py)
    WIFI_TIMEOUT = 30
    
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
    
    # Couleurs
    COULEUR_NORMALE = (0, 0, 100)      # Bleu (jour)
    COULEUR_NUIT = (20, 0, 0)          # Rouge sombre (22h-6h)
    COULEUR_SECONDES = (0, 50, 50)     # Cyan
    COULEUR_PM = (100, 50, 0)          # Orange
    COULEUR_ERREUR = (100, 0, 0)       # Rouge
    
    # Transitions
    FADE_SECONDE = 0.15
    FADE_MINUTE = 0.3
    FADE_HEURE = 0.5
    FADE_ETAT = 0.4
    
    # Debug
    DEBUG = True