"""
Gestion réseau, WiFi et NTP
"""

import wifi
import socketpool
import adafruit_ntp
import time
from config import Config
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    print("ERREUR: Fichier secrets.py manquant!")
    WIFI_SSID = ""
    WIFI_PASSWORD = ""

class NetworkManager:
    def __init__(self):
        self.connected = False
        self.ip_address = None
        self.pool = None
        self.ntp_client = None
    
    def connecter_wifi(self):
        """Établit la connexion WiFi"""
        if Config.DEBUG:
            print(f"Connexion au WiFi: {WIFI_SSID}")
        
        try:
            wifi.radio.connect(
                WIFI_SSID,
                WIFI_PASSWORD,
                timeout=Config.WIFI_TIMEOUT
            )
            
            self.ip_address = wifi.radio.ipv4_address
            self.connected = True
            
            if Config.DEBUG:
                print(f"Connecté! IP: {self.ip_address}")
            
            return True
        
        except Exception as e:
            if Config.DEBUG:
                print(f"Échec connexion WiFi: {e}")
            self.connected = False
            return False
    
    def initialiser_ntp(self):
        """Initialise le client NTP"""
        if not self.connected:
            if Config.DEBUG:
                print("NTP: Non connecté au WiFi")
            return False
        
        try:
            self.pool = socketpool.SocketPool(wifi.radio)
            self.ntp_client = adafruit_ntp.NTP(
                self.pool,
                server=Config.NTP_SERVER
            )
            
            if Config.DEBUG:
                print("Client NTP initialisé")
            
            return True
        
        except Exception as e:
            if Config.DEBUG:
                print(f"Échec initialisation NTP: {e}")
            return False
    
    def obtenir_temps_ntp(self):
        """Récupère l'heure depuis le serveur NTP"""
        if not self.ntp_client:
            if Config.DEBUG:
                print("NTP: Client non initialisé")
            return None
        
        try:
            ntp_time = self.ntp_client.datetime
            if Config.DEBUG:
                print(f"Heure NTP récupérée: {ntp_time}")
            return ntp_time
        
        except Exception as e:
            if Config.DEBUG:
                print(f"Échec récupération NTP: {e}")
            return None
    
    def resynchroniser(self):
        """Tente une resynchronisation complète"""
        if Config.DEBUG:
            print("Tentative de resynchronisation...")
        
        # Reconnexion WiFi si nécessaire
        if not self.connected:
            self.connecter_wifi()
        
        # Réinitialisation NTP
        if self.connected:
            self.initialiser_ntp()
            
            # Récupération du temps
            ntp_time = self.obtenir_temps_ntp()
            return ntp_time
        
        return None