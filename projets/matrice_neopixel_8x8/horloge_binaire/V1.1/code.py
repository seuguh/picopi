"""
Horloge BCD 12h - Programme Principal
Architecture modulaire pour Raspberry Pi Pico W
Nouvelle organisation des colonnes, sans indicateur PM
Avec indicateurs WiFi/Internet
"""

import time
from config import Config
from modules.hardware import Hardware
from modules.time_utils import TimeManager
from modules.display import DisplayManager
from modules.button import ButtonManager
from modules.state_manager import State, StateManager
from modules.network_tester import NetworkTester

class BCDClock:
    def __init__(self):
        """Initialise l'horloge BCD"""
        if Config.DEBUG:
            print("=== Initialisation Horloge BCD ===")
            print("Nouvelle organisation des colonnes:")
            print("  0-1: Heures (2 colonnes, 4 bits)")
            print("  6:   Dizaines secondes (1 colonne, 3 bits)")
            print("  2-3: Dizaines minutes (2 colonnes, 3 bits) + Indicateurs")
            print("  7:   Unités secondes (1 colonne, 4 bits)")
            print("  4-5: Unités minutes (2 colonnes, 4 bits)")
            print("  Indicateurs WiFi/Internet sur colonnes 2-3, rangées 6-7")
        
        # Initialiser les managers
        self.hardware = Hardware()
        self.time_manager = TimeManager()
        self.display = DisplayManager(self.hardware)
        self.button = ButtonManager(self.hardware)
        self.state = StateManager()
        self.network_tester = NetworkTester()
        
        # Connecter le network_tester au display
        self.display.set_network_tester(self.network_tester)
        
        # Variables d'état
        self.dernier_affichage = None
        self.dernier_sync_ntp = 0
        self.erreur_affichee = False
        self.initial_sync_done = False  # Pour savoir si on a eu une synchro NTP initiale
        self.last_network_test_check = 0
    
    def initialiser_systeme(self):
        """Initialise tout le système"""
        if Config.DEBUG:
            print("Initialisation du système...")
        
        # Démarrer les tests réseau immédiatement
        self.network_tester.start_test()
        self.last_network_test_check = time.monotonic()
        
        if Config.DEBUG:
            print("Tests réseau démarrés (indicateurs jaunes)")
        
        # Ne pas bloquer sur l'initialisation WiFi
        # On laisse les tests se faire en arrière-plan
        return True
    
    def executer(self):
        """Boucle principale de l'application"""
        if Config.DEBUG:
            print("Démarrage de la boucle principale...")
        
        while True:
            try:
                current_time = time.monotonic()
                
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
                            # Mode éteint
                            self.display.eteindre(avec_transition=True)
                            self.network_tester.disconnect()  # Déconnecter WiFi
                            if Config.DEBUG:
                                print("Mode éteint: WiFi déconnecté")
                        elif nouvel_etat == State.AFFICHE:
                            # Mode allumé - AFFICHER D'ABORD L'HEURE
                            # Réafficher l'heure immédiatement
                            self.dernier_affichage = None
                            heure_actuelle = self.time_manager.obtenir_heure_actuelle()
                            self.display.afficher_heure(
                                self.time_manager,
                                avec_transition=True
                            )
                            self.dernier_affichage = heure_actuelle
                            
                            # Ensuite, réinitialiser les états réseau
                            self.network_tester.reset_states()
                            # Démarrer les tests réseau (sans bloquer)
                            self.network_tester.start_test()
                            
                            if Config.DEBUG:
                                print("Mode allumé: heure affichée, tests réseau lancés")
                    
                    if action == "resync":
                        if Config.DEBUG:
                            print("Resynchronisation NTP forcée...")
                        self.synchroniser_ntp()
                
                # 3. Gérer les tests réseau (uniquement si allumé)
                if self.state.state == State.AFFICHE:
                    # Exécuter les étapes de test en cours
                    if self.network_tester.test_in_progress:
                        test_fini = self.network_tester.run_test_step()
                        if test_fini:
                            # Mettre à jour l'affichage des indicateurs
                            self.display.mettre_a_jour_indicateurs()
                            
                            # Si WiFi et Internet sont OK, synchroniser NTP
                            if (self.network_tester.get_wifi_state() == NetworkTester.ETAT_OK and
                                self.network_tester.get_internet_state() == NetworkTester.ETAT_OK):
                                
                                # Synchroniser NTP si c'est la première fois ou si besoin
                                if not self.initial_sync_done or self.time_manager.besoin_resynchronisation():
                                    self.synchroniser_ntp()
                    
                    # Vérifier si un nouveau test périodique est nécessaire
                    if self.network_tester.should_test():
                        self.network_tester.start_test()
                        if Config.DEBUG:
                            print("Test réseau périodique démarré")
                
                # 4. Mettre à jour l'affichage selon l'état
                if self.state.state == State.AFFICHE:
                    # Obtenir l'heure actuelle
                    heure_actuelle = self.time_manager.obtenir_heure_actuelle()
                    
                    # Afficher si l'heure a changé (sauf juste après un réveil)
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
                    else:
                        # Mettre à jour juste les indicateurs si nécessaire
                        # (pour les changements d'état entre tests)
                        if current_time - self.last_network_test_check > 1:  # Toutes les secondes
                            self.display.mettre_a_jour_indicateurs()
                            self.last_network_test_check = current_time
                
                # 5. Gérer l'erreur initiale (croix rouge uniquement au démarrage)
                if not self.initial_sync_done and not self.erreur_affichee:
                    # Vérifier si on a échoué à obtenir une heure NTP
                    # Attendre un peu pour laisser le temps aux tests
                    if current_time > 10:  # Après 10 secondes
                        ntp_time = self.network_tester.get_ntp_time()
                        if not ntp_time:
                            # Afficher la croix rouge (erreur initiale)
                            self.display.afficher_erreur()
                            self.erreur_affichee = True
                            if Config.DEBUG:
                                print("ERREUR: Pas de synchro NTP initiale")
                        else:
                            self.initial_sync_done = True
                
                # Pause pour limiter le refresh
                time.sleep(Config.REFRESH_RATE)
                
            except Exception as e:
                if Config.DEBUG:
                    print(f"ERREUR dans la boucle principale: {e}")
                time.sleep(1)  # Pause en cas d'erreur
    
    def synchroniser_ntp(self):
        """Synchronise avec le serveur NTP"""
        ntp_time = self.network_tester.get_ntp_time()
        
        if ntp_time:
            self.time_manager.synchroniser_ntp(ntp_time)
            self.dernier_sync_ntp = time.monotonic()
            self.erreur_affichee = False
            self.initial_sync_done = True
            
            if Config.DEBUG:
                print("Synchronisation NTP réussie!")
            return True
        else:
            if Config.DEBUG:
                print("Échec synchronisation NTP (pas de temps disponible)")
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