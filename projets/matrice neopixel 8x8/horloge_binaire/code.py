"""
Horloge BCD 12h - Programme Principal
Version simplifiée du monitoring
"""

import time
from config import Config
from hardware import Hardware
from time_utils import TimeManager
from display import DisplayManager
from button import ButtonManager
from state_manager import State, StateManager
from network import NetworkManager

class BCDClock:
    def __init__(self):
        """Initialise l'horloge BCD avec monitoring simplifié"""
        if Config.DEBUG:
            print("=== Initialisation Horloge BCD ===")
            print(f"Monitoring réseau: {'ACTIVÉ' if Config.MONITORING_ACTIF else 'DÉSACTIVÉ'}")
        
        # Initialiser les managers
        self.hardware = Hardware()
        self.time_manager = TimeManager()
        self.display = DisplayManager(self.hardware)
        self.button = ButtonManager(self.hardware)
        self.state = StateManager()
        self.network = NetworkManager()
        
        # Variables d'état
        self.dernier_affichage = None
        self.dernier_sync_ntp = 0
        self.erreur_affichee = False
        
        # Pour l'animation des secondes
        self.derniere_seconde = -1
        
        # Pour le monitoring (plus simple)
        self.dernier_check_wifi = 0
    
    def initialiser_systeme(self):
        """Initialise tout le système"""
        if Config.DEBUG:
            print("Initialisation du système...")
        
        # Connexion WiFi initiale
        if not self.network.connecter_wifi():
            if Config.DEBUG:
                print("ERREUR: Impossible de se connecter au WiFi")
            # On continue quand même, le monitoring essaiera plus tard
        else:
            # Initialisation NTP
            if not self.network.initialiser_ntp():
                if Config.DEBUG:
                    print("ERREUR: Impossible d'initialiser NTP")
            else:
                # Synchronisation NTP initiale
                ntp_time = self.network.obtenir_temps_ntp()
                if ntp_time:
                    self.time_manager.synchroniser_ntp(ntp_time)
                    self.dernier_sync_ntp = time.monotonic()
                    
                    if Config.DEBUG:
                        heures, minutes, secondes, pm = self.time_manager.obtenir_heure_actuelle()
                        am_pm = "PM" if pm else "AM"
                        print(f"Heure synchronisée: {heures:02d}:{minutes:02d}:{secondes:02d} {am_pm}")
        
        return True  # Toujours retourner True pour continuer
    
    def verifier_et_reconnecter_wifi(self):
        """Vérifie l'état WiFi et tente de reconnecter si nécessaire"""
        if not Config.MONITORING_ACTIF:
            return
        
        temps_actuel = time.monotonic()
        
        # Vérifier toutes les 30 secondes
        if temps_actuel - self.dernier_check_wifi >= Config.INTERVALLE_MONITORING:
            self.dernier_check_wifi = temps_actuel
            
            if Config.DEBUG_RESEAU:
                print(f"[Main] Vérification WiFi (échecs: {self.network.echecs_consecutifs})")
            
            # Utiliser le monitoring du NetworkManager
            besoin_reconnecter = self.network.monitoring_reseau()
            
            if besoin_reconnecter and not self.network.en_tentative_reconnexion:
                if Config.DEBUG_RESEAU:
                    print(f"[Main] Tentative de reconnexion WiFi")
                
                if self.network.tenter_reconnexion():
                    # Réussite
                    if Config.DEBUG_RESEAU:
                        print("[Main] WiFi reconnecté avec succès")
                    
                    # Réinitialiser NTP si perdu
                    if not self.network.ntp_client:
                        self.network.initialiser_ntp()
                    
                    # Resynchroniser l'heure
                    ntp_time = self.network.obtenir_temps_ntp()
                    if ntp_time:
                        self.time_manager.synchroniser_ntp(ntp_time)
                        self.dernier_sync_ntp = temps_actuel
                        
                        if Config.DEBUG:
                            print("[Main] Heure resynchronisée après reconnexion")
    
    def executer(self):
        """Boucle principale simplifiée"""
        if Config.DEBUG:
            print("Démarrage de la boucle principale...")
        
        while True:
            try:
                # 1. Détecter les appuis sur le bouton
                type_appui = self.button.detecter_appui()
                
                if type_appui and Config.DEBUG:
                    print(f"Appui détecté: {type_appui}")
                
                # 2. Gérer les transitions d'état
                if type_appui:
                    nouvel_etat, action = self.state.traiter_appui_bouton(type_appui)
                    
                    if self.state.transition(nouvel_etat):
                        if Config.DEBUG:
                            etat_nom = "AFFICHE" if nouvel_etat == State.AFFICHE else "ETEINT"
                            print(f"Changement d'état vers: {etat_nom}")
                        
                        if nouvel_etat == State.ETEINT:
                            self.display.eteindre(avec_transition=True)
                        elif nouvel_etat == State.AFFICHE:
                            self.display.allumer(self.time_manager, avec_transition=True, network_manager=self.network)
                            self.dernier_affichage = None
                    
                    if action == "resync":
                        if Config.DEBUG:
                            print("Resynchronisation NTP forcée...")
                        self.synchroniser_ntp()
                
                # 3. Vérifier et reconnecter WiFi si nécessaire
                self.verifier_et_reconnecter_wifi()
                
                # 4. Mettre à jour l'affichage selon l'état
                if self.state.state == State.AFFICHE:
                    # Resynchronisation NTP périodique
                    if self.time_manager.besoin_resynchronisation():
                        if Config.DEBUG:
                            print("Resynchronisation périodique NTP...")
                        self.synchroniser_ntp()
                    
                    # Obtenir et afficher l'heure
                    heures, minutes, secondes, pm = self.time_manager.obtenir_heure_actuelle()
                    
                    self.display.afficher_heure(
                        self.time_manager, 
                        avec_transition=True,
                        network_manager=self.network
                    )
                    
                    # Log chaque minute
                    if Config.DEBUG and secondes == 0 and self.derniere_seconde != 0:
                        am_pm = "PM" if pm else "AM"
                        etat_wifi = self.network.etat_wifi
                        print(f"{heures:02d}:{minutes:02d}:{secondes:02d} {am_pm} - WiFi: {etat_wifi} (échecs: {self.network.echecs_consecutifs})")
                    
                    self.derniere_seconde = secondes
                
                # Pause
                time.sleep(Config.REFRESH_RATE)
                
            except Exception as e:
                if Config.DEBUG:
                    print(f"ERREUR dans la boucle principale: {e}")
                time.sleep(1)
    
    def synchroniser_ntp(self):
        """Synchronise avec le serveur NTP"""
        ntp_time = self.network.resynchroniser()
        
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            
            if Config.DEBUG:
                print("Synchronisation NTP réussie!")
            return True
        else:
            if Config.DEBUG:
                print("Échec synchronisation NTP")
            return False

def main():
    """Point d'entrée principal"""
    horloge = BCDClock()
    horloge.initialiser_systeme()
    horloge.executer()

if __name__ == "__main__":
    main()