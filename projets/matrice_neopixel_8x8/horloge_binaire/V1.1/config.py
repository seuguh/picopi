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
    # COULEUR_PM retirée (plus d'indicateur PM)
    COULEUR_ERREUR = (100, 0, 0)       # Rouge
    
    # Transitions
    FADE_SECONDE = 0.15
    FADE_MINUTE = 0.3
    FADE_HEURE = 0.5
    FADE_ETAT = 0.4
    
    # Tests réseau
    TEST_WIFI_INTERVAL = 30          # Test toutes les 30 secondes
    TEST_WIFI_RETRIES = 2            # 2 tentatives après échec
    TEST_WIFI_RETRY_INTERVAL = 5     # 5 secondes entre tentatives
    
    # Couleurs indicateurs réseau
    COULEUR_WIFI_OK = (0, 100, 0)        # Vert
    COULEUR_WIFI_TEST = (100, 100, 0)    # Jaune
    COULEUR_WIFI_KO = (100, 0, 0)        # Rouge
    
    COULEUR_INTERNET_OK = (0, 100, 0)     # Vert
    COULEUR_INTERNET_TEST = (100, 100, 0) # Jaune
    COULEUR_INTERNET_KO = (100, 0, 0)     # Rouge
    
    # Positions des indicateurs (colonne, rangée)
    WIFI_LED_1 = (2, 6)  # Colonne 2, Rangée 6
    WIFI_LED_2 = (3, 6)  # Colonne 3, Rangée 6
    INTERNET_LED_1 = (2, 7)  # Colonne 2, Rangée 7
    INTERNET_LED_2 = (3, 7)  # Colonne 3, Rangée 7
    
    # Debug
    DEBUG = True