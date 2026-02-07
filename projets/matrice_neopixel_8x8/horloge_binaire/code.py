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
        if Config.DEBUG:
            print("=== Horloge BCD ===")
        
        self.hardware = Hardware()
        self.time_manager = TimeManager()
        self.display = DisplayManager(self.hardware)
        self.button = ButtonManager(self.hardware)
        self.state = StateManager()
        self.network = NetworkManager()
        
        self.dernier_affichage = None
        self.dernier_sync_ntp = 0
    
    def initialiser_systeme(self):
        if Config.DEBUG:
            print("Initialisation...")
        
        # WiFi
        if not self.network.connecter_wifi():
            self.display.afficher_erreur()
            return False
        
        # NTP
        if not self.network.initialiser_ntp():
            self.display.afficher_erreur()
            return False
        
        # Sync NTP
        ntp_time = self.network.obtenir_temps_ntp()
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            
            if Config.DEBUG:
                h, m, s, pm = self.time_manager.obtenir_heure_actuelle()
                am_pm = "PM" if pm else "AM"
                print(f"Heure: {h:02d}:{m:02d}:{s:02d} {am_pm}")
            
            return True
        
        self.display.afficher_erreur()
        return False
    
    def executer(self):
        if Config.DEBUG:
            print("Démarrage...")
        
        while True:
            try:
                # Bouton
                type_appui = self.button.detecter_appui()
                
                if type_appui and Config.DEBUG:
                    print(f"Bouton: {type_appui}")
                
                # Gérer état
                if type_appui:
                    nouvel_etat, action = self.state.traiter_appui_bouton(type_appui)
                    
                    if self.state.transition(nouvel_etat):
                        if nouvel_etat == State.ETEINT:
                            self.display.eteindre()
                        elif nouvel_etat == State.AFFICHE:
                            self.dernier_affichage = None
                    
                    if action == "resync":
                        self.synchroniser_ntp()
                
                # Affichage
                if self.state.state == State.AFFICHE:
                    # Resync périodique
                    if self.time_manager.besoin_resynchronisation():
                        self.synchroniser_ntp()
                    
                    # Afficher
                    self.display.afficher_heure(self.time_manager)
                    
                    # Log
                    h, m, s, pm = self.time_manager.obtenir_heure_actuelle()
                    if Config.DEBUG and s == 0:
                        am_pm = "PM" if pm else "AM"
                        print(f"{h:02d}:{m:02d}:{s:02d} {am_pm}")
                
                time.sleep(Config.REFRESH_RATE)
                
            except Exception as e:
                if Config.DEBUG:
                    print(f"ERREUR: {e}")
                time.sleep(1)
    
    def synchroniser_ntp(self):
        ntp_time = self.network.resynchroniser()
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            return True
        return False

def main():
    horloge = BCDClock()
    horloge.initialiser_systeme()
    horloge.executer()

if __name__ == "__main__":
    main()