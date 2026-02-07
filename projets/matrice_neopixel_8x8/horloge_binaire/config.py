class Config:
    # WiFi
    WIFI_TIMEOUT = 30
    
    # NTP
    NTP_SERVER = "pool.ntp.org"
    TIMEZONE_OFFSET = 1
    NTP_SYNC_INTERVAL = 3600
    
    # Matrice
    MATRICE_PIN = 0
    MATRICE_LEDS = 64
    MATRICE_LUMINOSITE = 0.1
    
    # Bouton
    BOUTON_PIN = 1
    BOUTON_PULLDOWN = True
    BOUTON_APPUI_LONG = 1.5
    
    # Affichage
    FORMAT_12H = True
    AFFICHER_SECONDES = True
    REFRESH_RATE = 0.05
    
    # Couleurs
    COULEUR_NORMALE = (0, 0, 100)
    COULEUR_NUIT = (20, 0, 0)
    COULEUR_SECONDES = (0, 50, 50)
    COULEUR_ERREUR = (100, 0, 0)
    
    # Transitions
    FADE_SECONDE = 0.15
    FADE_MINUTE = 0.3
    FADE_HEURE = 0.5
    FADE_ETAT = 0.4
    
    # Debug
    DEBUG = True