"""
Gestion des tests WiFi et Internet avec indicateurs visuels
"""

import time
import wifi
import socketpool
import adafruit_ntp
from config import Config
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    print("ERREUR: Fichier secrets.py manquant!")
    WIFI_SSID = ""
    WIFI_PASSWORD = ""

class NetworkTester:
    # États possibles
    ETAT_OK = 0
    ETAT_TEST = 1
    ETAT_KO = 2
    
    def __init__(self):
        """Initialise le testeur réseau"""
        self.wifi_state = self.ETAT_TEST  # Par défaut en test au démarrage
        self.internet_state = self.ETAT_TEST
        
        self.last_test_time = 0
        self.test_in_progress = False
        self.test_attempts = 0
        
        # Réseau
        self.connected = False
        self.ip_address = None
        self.pool = None
        self.ntp_client = None
        
        # Pour les tests
        self.wifi_test_started = False
        self.internet_test_started = False
        
        if Config.DEBUG:
            print("NetworkTester initialisé")
    
    def reset_states(self):
        """Réinitialise les états pour un nouveau démarrage"""
        self.wifi_state = self.ETAT_TEST
        self.internet_state = self.ETAT_TEST
        self.test_in_progress = False
        self.test_attempts = 0
        self.wifi_test_started = False
        self.internet_test_started = False
        
        # Réactiver le WiFi si désactivé
        try:
            wifi.radio.enabled = True
        except:
            pass
        
        if Config.DEBUG:
            print("États réseau réinitialisés")
    
    def get_wifi_state(self):
        """Retourne l'état actuel du WiFi"""
        return self.wifi_state
    
    def get_internet_state(self):
        """Retourne l'état actuel d'Internet"""
        return self.internet_state
    
    def get_wifi_color(self):
        """Retourne la couleur correspondant à l'état WiFi"""
        if self.wifi_state == self.ETAT_OK:
            return Config.COULEUR_WIFI_OK
        elif self.wifi_state == self.ETAT_TEST:
            return Config.COULEUR_WIFI_TEST
        else:  # ETAT_KO
            return Config.COULEUR_WIFI_KO
    
    def get_internet_color(self):
        """Retourne la couleur correspondant à l'état Internet"""
        if self.internet_state == self.ETAT_OK:
            return Config.COULEUR_INTERNET_OK
        elif self.internet_state == self.ETAT_TEST:
            return Config.COULEUR_INTERNET_TEST
        else:  # ETAT_KO
            return Config.COULEUR_INTERNET_KO
    
    def should_test(self):
        """Vérifie si un test périodique est nécessaire"""
        current_time = time.monotonic()
        
        # Si on est en train de tester, ne pas relancer
        if self.test_in_progress:
            return False
        
        # Si WiFi est KO, attendre l'intervalle complet
        if self.wifi_state == self.ETAT_KO:
            return current_time - self.last_test_time >= Config.TEST_WIFI_INTERVAL
        
        # Sinon, tester périodiquement
        return current_time - self.last_test_time >= Config.TEST_WIFI_INTERVAL
    
    def start_test(self):
        """Démarre un test réseau complet"""
        if self.test_in_progress:
            if Config.DEBUG:
                print("Test déjà en cours")
            return False
        
        self.test_in_progress = True
        self.test_attempts = 0
        self.wifi_test_started = False
        self.internet_test_started = False
        
        # Mettre les états en mode test (sauf si déjà OK)
        if self.wifi_state != self.ETAT_OK:
            self.wifi_state = self.ETAT_TEST
        if self.internet_state != self.ETAT_OK:
            self.internet_state = self.ETAT_TEST
        
        self.last_test_time = time.monotonic()
        
        if Config.DEBUG:
            print("Démarrage test réseau...")
        
        return True
    
    def run_test_step(self):
        """
        Exécute une étape de test (à appeler régulièrement)
        Retourne True si le test est terminé
        """
        if not self.test_in_progress:
            return True
        
        current_time = time.monotonic()
        
        # Test WiFi
        if not self.wifi_test_started:
            if Config.DEBUG:
                print("Test WiFi en cours...")
            
            self.wifi_test_started = True
            wifi_ok = self._test_wifi_connection()
            
            if wifi_ok:
                self.wifi_state = self.ETAT_OK
                self.test_attempts = 0
                
                if Config.DEBUG:
                    print("WiFi OK")
                
                # WiFi OK, on peut tester Internet
                return False  # Pas encore terminé
            else:
                # WiFi KO
                self.test_attempts += 1
                
                if self.test_attempts >= Config.TEST_WIFI_RETRIES:
                    # Échec définitif pour ce cycle
                    self.wifi_state = self.ETAT_KO
                    self.internet_state = self.ETAT_KO  # Pas d'internet sans WiFi
                    self.test_in_progress = False
                    
                    if Config.DEBUG:
                        print(f"WiFi KO après {self.test_attempts} tentatives")
                    
                    return True  # Test terminé
                else:
                    # Nouvelle tentative après l'intervalle
                    self.wifi_test_started = False
                    self.last_test_time = current_time + Config.TEST_WIFI_RETRY_INTERVAL
                    
                    if Config.DEBUG:
                        print(f"Tentative WiFi {self.test_attempts+1}/{Config.TEST_WIFI_RETRIES} dans {Config.TEST_WIFI_RETRY_INTERVAL}s")
                    
                    return False
        
        # Test Internet (uniquement si WiFi OK)
        if not self.internet_test_started and self.wifi_state == self.ETAT_OK:
            if Config.DEBUG:
                print("Test Internet en cours...")
            
            self.internet_test_started = True
            internet_ok = self._test_internet_connection()
            
            if internet_ok:
                self.internet_state = self.ETAT_OK
                self.test_attempts = 0
                
                if Config.DEBUG:
                    print("Internet OK")
            else:
                self.internet_state = self.ETAT_KO
                
                if Config.DEBUG:
                    print("Internet KO")
            
            # Test terminé
            self.test_in_progress = False
            return True
        
        return False  # En attente
    
    def _test_wifi_connection(self):
        """Teste la connexion WiFi"""
        try:
            # S'assurer que le WiFi est activé
            wifi.radio.enabled = True
            
            # Essayer de se connecter
            wifi.radio.connect(
                WIFI_SSID,
                WIFI_PASSWORD,
                timeout=Config.WIFI_TIMEOUT
            )
            
            self.connected = True
            self.ip_address = wifi.radio.ipv4_address
            
            # Initialiser le pool de sockets pour les tests suivants
            self.pool = socketpool.SocketPool(wifi.radio)
            
            return True
            
        except Exception as e:
            if Config.DEBUG:
                print(f"Échec connexion WiFi: {e}")
            
            self.connected = False
            self.ip_address = None
            return False
    
    def _test_internet_connection(self):
        """Teste la connexion Internet via NTP"""
        if not self.connected or not self.pool:
            return False
        
        try:
            # Créer un client NTP pour le test
            ntp_client = adafruit_ntp.NTP(
                self.pool,
                server=Config.NTP_SERVER
            )
            
            # Tenter de récupérer l'heure
            ntp_time = ntp_client.datetime
            if ntp_time:
                # Conserver le client pour une utilisation future
                self.ntp_client = ntp_client
                return True
            else:
                return False
                
        except Exception as e:
            if Config.DEBUG:
                print(f"Échec test Internet: {e}")
            return False
    
    def get_ntp_time(self):
        """Récupère l'heure NTP (si disponible)"""
        if not self.ntp_client:
            return None
        
        try:
            return self.ntp_client.datetime
        except Exception as e:
            if Config.DEBUG:
                print(f"Erreur récupération NTP: {e}")
            return None
    
    def disconnect(self):
        """Déconnecte du WiFi et réinitialise"""
        try:
            # Désactiver complètement le WiFi pour économiser l'énergie
            wifi.radio.enabled = False
        except Exception as e:
            if Config.DEBUG:
                print(f"Erreur lors de la déconnexion WiFi: {e}")
        
        self.connected = False
        self.ip_address = None
        self.pool = None
        self.ntp_client = None
        # Ne pas réinitialiser les états ici, ils seront réinitialisés au réveil
        self.test_in_progress = False
        
        if Config.DEBUG:
            print("WiFi déconnecté et désactivé")
    
    def is_connected(self):
        """Vérifie si connecté au WiFi"""
        return self.connected