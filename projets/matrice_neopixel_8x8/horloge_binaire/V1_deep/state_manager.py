"""
Gestion des états de l'application
"""

from config import Config

class State:
    AFFICHE = 0  # Horloge visible et mise à jour
    ETEINT = 1   # LEDs éteintes

class StateManager:
    def __init__(self):
        self.state = State.AFFICHE
        self.last_state_change = 0
    
    def transition(self, nouvel_etat):
        """Change l'état de l'application"""
        if self.state != nouvel_etat:
            self.state = nouvel_etat
            self.last_state_change = 0
            return True
        return False
    
    def traiter_appui_bouton(self, type_appui):
        """
        Traite un appui bouton selon l'état courant
        
        Returns:
            tuple: (nouvel_etat, action)
        """
        if self.state == State.ETEINT:
            if type_appui == "court":
                return State.AFFICHE, "allumer"
        
        elif self.state == State.AFFICHE:
            if type_appui == "court":
                return State.AFFICHE, "resync"
            elif type_appui == "long":
                return State.ETEINT, "eteindre"
        
        return self.state, None