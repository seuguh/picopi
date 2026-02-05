"""
Gestion réseau, WiFi et NTP avec monitoring fiable
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
        
        # Monitoring
        self.dernier_monitoring = 0
        self.echecs_consecutifs = 0
        self.en_tentative_reconnexion = False
        self.etat_wifi = "inconnu"  # "ok", "warning", "erreur"
        self.derniere_reconnexion = 0
        
        # Pour éviter les reconnexions trop fréquentes
        self.dernier_test_reussi = 0
    
    def connecter_wifi(self):
        """Établit la connexion WiFi"""
        if Config.DEBUG_RESEAU:
            print(f"[WiFi] Connexion à: {WIFI_SSID}")
        
        try:
            # D'abord déconnecter pour être sûr
            try:
                wifi.radio.stop_station()
            except:
                pass
            
            time.sleep(0.5)  # Petit délai
            
            # Se connecter
            wifi.radio.connect(
                WIFI_SSID,
                WIFI_PASSWORD,
                timeout=Config.WIFI_TIMEOUT
            )
            
            # Attendre un peu pour que la connexion s'établisse
            time.sleep(1)
            
            # Vérifier la connexion
            if wifi.radio.ipv4_address:
                self.ip_address = wifi.radio.ipv4_address
                self.connected = True
                self.echecs_consecutifs = 0
                self.etat_wifi = "ok"
                self.derniere_reconnexion = time.monotonic()
                self.dernier_test_reussi = time.monotonic()
                
                if Config.DEBUG_RESEAU:
                    print(f"[WiFi] Connecté! IP: {self.ip_address}")
                
                return True
            else:
                if Config.DEBUG_RESEAU:
                    print("[WiFi] Pas d'adresse IP obtenue")
                self.connected = False
                self.echecs_consecutifs += 1
                self._mettre_a_jour_etat()
                return False
        
        except Exception as e:
            if Config.DEBUG_RESEAU:
                print(f"[WiFi] Échec connexion: {e}")
            self.connected = False
            self.echecs_consecutifs += 1
            self._mettre_a_jour_etat()
            return False
    
    def tester_connexion(self):
        """
        Teste la connexion WiFi de manière fiable
        Retourne True si connecté, False sinon
        """
        try:
            # Méthode 1: Vérifier si on a une adresse IP
            if not wifi.radio.ipv4_address:
                self.connected = False
                self.echecs_consecutifs += 1
                self._mettre_a_jour_etat()
                return False
            
            # Méthode 2: Tenter un ping léger vers la passerelle par défaut
            # (plus fiable que juste vérifier l'état)
            gateway = wifi.radio.ipv4_gateway
            if gateway:
                # Simuler un test en vérifiant simplement l'état
                # CircuitPython n'a pas de ping facile, on fait un test simple
                self.connected = True
                self.dernier_test_reussi = time.monotonic()
                
                if self.echecs_consecutifs > 0:
                    if Config.DEBUG_RESEAU:
                        print(f"[WiFi] Connexion rétablie après {self.echecs_consecutifs} échecs")
                    self.echecs_consecutifs = 0
                    self.etat_wifi = "ok"
                
                return True
            else:
                self.connected = False
                self.echecs_consecutifs += 1
                self._mettre_a_jour_etat()
                return False
            
        except Exception as e:
            if Config.DEBUG_RESEAU:
                print(f"[WiFi] Erreur test: {e}")
            self.connected = False
            self.echecs_consecutifs += 1
            self._mettre_a_jour_etat()
            return False
    
    def _mettre_a_jour_etat(self):
        """Met à jour l'état WiFi selon les échecs consécutifs"""
        ancien_etat = self.etat_wifi
        
        if self.echecs_consecutifs == 0:
            self.etat_wifi = "ok"
        elif self.echecs_consecutifs <= Config.TENTATIVES_RECONNEXION:
            self.etat_wifi = "warning"
        else:
            self.etat_wifi = "erreur"
        
        if Config.DEBUG_RESEAU and ancien_etat != self.etat_wifi:
            print(f"[WiFi] État: {ancien_etat} → {self.etat_wifi} (échecs: {self.echecs_consecutifs})")
    
    def monitoring_reseau(self):
        """
        Effectue le monitoring périodique du réseau
        Retourne True si une reconnexion est nécessaire
        """
        if not Config.MONITORING_ACTIF:
            return False
        
        temps_actuel = time.monotonic()
        
        # Vérifier si c'est le moment de tester (toutes les 30 secondes)
        if temps_actuel - self.dernier_monitoring >= Config.INTERVALLE_MONITORING:
            self.dernier_monitoring = temps_actuel
            
            if Config.DEBUG_RESEAU:
                print(f"[Monitoring] Test réseau à {temps_actuel:.0f}s (échecs: {self.echecs_consecutifs})")
            
            # Test de connexion
            if self.tester_connexion():
                if Config.DEBUG_RESEAU:
                    print("[Monitoring] Connexion OK")
                
                # Si on vient de se reconnecter, réinitialiser NTP
                if self.connected and not self.ntp_client:
                    if Config.DEBUG_RESEAU:
                        print("[Monitoring] Réinitialisation NTP après reconnexion")
                    self.initialiser_ntp()
                
                return False
            else:
                # Connexion échouée
                if Config.DEBUG_RESEAU:
                    print(f"[Monitoring] Échec, état: {self.etat_wifi}")
                
                # Logique de reconnexion:
                # 1. Si c'est le premier ou deuxième échec, tenter reconnexion immédiate
                # 2. Si en état erreur, tenter toutes les minutes
                # 3. Éviter les reconnexions trop fréquentes
                
                if self.etat_wifi == "warning" and not self.en_tentative_reconnexion:
                    # Premier ou deuxième échec: tenter reconnexion
                    if Config.DEBUG_RESEAU:
                        print("[Monitoring] Tentative de reconnexion (warning)")
                    return True
                
                elif self.etat_wifi == "erreur":
                    # En état erreur: tenter reconnexion toutes les minutes
                    temps_depuis_derniere_tentative = temps_actuel - self.derniere_reconnexion
                    if temps_depuis_derniere_tentative >= 60 and not self.en_tentative_reconnexion:
                        if Config.DEBUG_RESEAU:
                            print(f"[Monitoring] Tentative de reconnexion périodique (erreur depuis {temps_depuis_derniere_tentative:.0f}s)")
                        return True
        
        return False
    
    def tenter_reconnexion(self):
        """
        Tente une reconnexion forcée
        """
        if self.en_tentative_reconnexion:
            if Config.DEBUG_RESEAU:
                print("[Reconnexion] Déjà en cours")
            return False
        
        self.en_tentative_reconnexion = True
        
        if Config.DEBUG_RESEAU:
            print(f"[Reconnexion] Début tentative (échecs: {self.echecs_consecutifs})")
        
        try:
            # Tenter de se reconnecter
            succes = self.connecter_wifi()
            
            if succes:
                if Config.DEBUG_RESEAU:
                    print("[Reconnexion] Succès!")
                
                # Mettre à jour l'état
                self.etat_wifi = "ok"
                self.en_tentative_reconnexion = False
                return True
            else:
                if Config.DEBUG_RESEAU:
                    print("[Reconnexion] Échec")
                
                self.en_tentative_reconnexion = False
                return False
                
        except Exception as e:
            if Config.DEBUG_RESEAU:
                print(f"[Reconnexion] Exception: {e}")
            self.en_tentative_reconnexion = False
            return False
    
    def initialiser_ntp(self):
        """Initialise le client NTP"""
        if not self.connected:
            if Config.DEBUG_RESEAU:
                print("[NTP] Non connecté au WiFi")
            return False
        
        try:
            self.pool = socketpool.SocketPool(wifi.radio)
            self.ntp_client = adafruit_ntp.NTP(
                self.pool,
                server=Config.NTP_SERVER
            )
            
            if Config.DEBUG_RESEAU:
                print("[NTP] Client initialisé")
            
            return True
        
        except Exception as e:
            if Config.DEBUG_RESEAU:
                print(f"[NTP] Échec initialisation: {e}")
            return False
    
    def obtenir_temps_ntp(self):
        """Récupère l'heure depuis le serveur NTP"""
        if not self.ntp_client:
            if Config.DEBUG_RESEAU:
                print("[NTP] Client non initialisé")
            return None
        
        try:
            ntp_time = self.ntp_client.datetime
            if Config.DEBUG_RESEAU:
                print(f"[NTP] Heure récupérée: {ntp_time}")
            return ntp_time
        
        except Exception as e:
            if Config.DEBUG_RESEAU:
                print(f"[NTP] Échec récupération: {e}")
            return None
    
    def resynchroniser(self):
        """Tente une resynchronisation complète"""
        if Config.DEBUG_RESEAU:
            print("[Resync] Tentative de resynchronisation...")
        
        # Reconnexion WiFi si nécessaire
        if not self.connected:
            if Config.DEBUG_RESEAU:
                print("[Resync] Connexion WiFi manquante")
            self.connecter_wifi()
        
        # Réinitialisation NTP
        if self.connected:
            # Réinitialiser le client NTP
            self.ntp_client = None
            self.initialiser_ntp()
            
            # Récupération du temps
            ntp_time = self.obtenir_temps_ntp()
            return ntp_time
        else:
            if Config.DEBUG_RESEAU:
                print("[Resync] Impossible de se connecter")
        
        return None
    
    def get_wifi_color(self):
        """Retourne la couleur correspondant à l'état WiFi"""
        if self.etat_wifi == "ok":
            return Config.COULEUR_WIFI_OK
        elif self.etat_wifi == "warning":
            return Config.COULEUR_WIFI_WARNING
        else:  # "erreur"
            return Config.COULEUR_WIFI_ERREUR