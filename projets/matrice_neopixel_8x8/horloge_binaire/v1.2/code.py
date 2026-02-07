"""
Horloge BCD 12h - Programme Principal
Architecture modulaire pour Raspberry Pi Pico W
Nouvelle organisation des colonnes, sans indicateur PM
"""

import time
from config import Config
from modules.hardware import Hardware
from modules.time_utils import TimeManager
from modules.display import DisplayManager
from modules.button import ButtonManager
from modules.state_manager import State, StateManager
from modules.network import NetworkManager

class BCDClock:
    def __init__(self):
        """Initialise l'horloge BCD"""
        if Config.DEBUG:
            print("=== Initialisation Horloge BCD ===")
            print("Nouvelle organisation des colonnes:")
            print("  0-1: Heures (2 colonnes, 4 bits)")
            print("  6:   Dizaines secondes (1 colonne, 3 bits)")
            print("  2-3: Dizaines minutes (2 colonnes, 3 bits)")
            print("  7:   Unités secondes (1 colonne, 4 bits)")
            print("  4-5: Unités minutes (2 colonnes, 4 bits)")
            print("  Pas d'indicateur PM")
        
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
    
    def initialiser_systeme(self):
        """Initialise tout le système"""
        if Config.DEBUG:
            print("Initialisation du système...")
        
        # Connexion WiFi
        if not self.network.connecter_wifi():
            self.display.afficher_erreur()
            self.erreur_affichee = True
            if Config.DEBUG:
                print("ERREUR: Impossible de se connecter au WiFi")
            return False
        
        # Initialisation NTP
        if not self.network.initialiser_ntp():
            self.display.afficher_erreur()
            self.erreur_affichee = True
            if Config.DEBUG:
                print("ERREUR: Impossible d'initialiser NTP")
            return False
        
        # Synchronisation NTP initiale
        ntp_time = self.network.obtenir_temps_ntp()
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            self.erreur_affichee = False
            
            if Config.DEBUG:
                heures, minutes, secondes, pm = self.time_manager.obtenir_heure_actuelle()
                am_pm = "PM" if pm else "AM"
                print(f"Heure synchronisée: {heures:02d}:{minutes:02d}:{secondes:02d} {am_pm}")
            
            return True
        else:
            self.display.afficher_erreur()
            self.erreur_affichee = True
            return False
    
    def executer(self):
        """Boucle principale de l'application"""
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
                            # Réafficher l'heure
                            self.dernier_affichage = None
                    
                    if action == "resync":
                        if Config.DEBUG:
                            print("Resynchronisation NTP forcée...")
                        self.synchroniser_ntp()
                
                # 3. Mettre à jour l'affichage selon l'état
                if self.state.state == State.AFFICHE:
                    # Vérifier si on doit resynchroniser NTP
                    if self.time_manager.besoin_resynchronisation():
                        if Config.DEBUG:
                            print("Resynchronisation périodique NTP...")
                        self.synchroniser_ntp()
                    
                    # Obtenir l'heure actuelle
                    heure_actuelle = self.time_manager.obtenir_heure_actuelle()
                    
                    # Afficher si l'heure a changé
                    if heure_actuelle != self.dernier_affichage:
                        self.display.afficher_heure(
                            self.time_manager,
                            avec_transition=True
                        )
                        self.dernier_affichage = heure_actuelle
                        
                        if Config.DEBUG and heure_actuelle[2] == 0:
                            # Afficher l'heure chaque minute
                            h, m, s, pm = heure_actuelle
                            am_pm = "PM" if pm else "AM"
                            print(f"Heure affichée: {h:02d}:{m:02d}:{s:02d} {am_pm}")
                
                # 4. Gérer les erreurs réseau
                if not self.network.connected and not self.erreur_affichee:
                    self.display.afficher_erreur()
                    self.erreur_affichee = True
                    if Config.DEBUG:
                        print("ERREUR: Perte de connexion WiFi")
                
                # Pause pour limiter le refresh
                time.sleep(Config.REFRESH_RATE)
                
            except Exception as e:
                if Config.DEBUG:
                    print(f"ERREUR dans la boucle principale: {e}")
                time.sleep(1)  # Pause en cas d'erreur
    
    def synchroniser_ntp(self):
        """Synchronise avec le serveur NTP"""
        ntp_time = self.network.resynchroniser()
        
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            self.erreur_affichee = False
            
            if Config.DEBUG:
                print("Synchronisation NTP réussie!")
            return True
        else:
            self.display.afficher_erreur()
            self.erreur_affichee = True
            
            if Config.DEBUG:
                print("Échec synchronisation NTP")
            return False

def main():
    """Point d'entrée principal"""
    horloge = BCDClock()
    
    # Initialisation
    if not horloge.initialiser_systeme():
        if Config.DEBUG:
            print("Échec initialisation, démarrage en mode erreur")
    
    # Boucle principale
    horloge.executer()

if __name__ == "__main__":
    main()