import wifi
import socketpool
import adafruit_ntp
import time
from config import Config
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    print("ERREUR: secrets.py manquant!")
    WIFI_SSID = ""
    WIFI_PASSWORD = ""

class NetworkManager:
    def __init__(self):
        self.connected = False
        self.ip_address = None
        self.pool = None
        self.ntp_client = None
    
    def connecter_wifi(self):
        try:
            wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD, timeout=Config.WIFI_TIMEOUT)
            self.ip_address = wifi.radio.ipv4_address
            self.connected = True
            if Config.DEBUG:
                print(f"WiFi OK! IP: {self.ip_address}")
            return True
        except Exception as e:
            if Config.DEBUG:
                print(f"WiFi erreur: {e}")
            self.connected = False
            return False
    
    def initialiser_ntp(self):
        if not self.connected:
            return False
        try:
            self.pool = socketpool.SocketPool(wifi.radio)
            self.ntp_client = adafruit_ntp.NTP(self.pool, server=Config.NTP_SERVER)
            return True
        except:
            return False
    
    def obtenir_temps_ntp(self):
        if not self.ntp_client:
            return None
        try:
            return self.ntp_client.datetime
        except:
            return None
    
    def resynchroniser(self):
        if not self.connected:
            self.connecter_wifi()
        if self.connected:
            self.initialiser_ntp()
            return self.obtenir_temps_ntp()
        return None