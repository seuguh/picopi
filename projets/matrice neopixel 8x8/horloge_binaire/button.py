"""
Gestion du bouton poussoir
"""

import time
from config import Config

class ButtonManager:
    def __init__(self, hardware):
        self.hardware = hardware
        self.last_press_time = 0
        self.debounce_delay = 0.05  # 50ms pour le debounce
    
    def detecter_appui(self):
        """
        Détecte les appuis sur le bouton
        
        Returns:
            str ou None: "court", "long", ou None
        """
        if not self.hardware.get_button_state():
            return None
        
        # Debounce: attendre un peu et vérifier à nouveau
        time.sleep(self.debounce_delay)
        if not self.hardware.get_button_state():
            return None
        
        # Mesurer la durée de l'appui
        debut = time.monotonic()
        
        # Attendre le relâchement
        while self.hardware.get_button_state():
            time.sleep(0.01)
            
            # Vérifier si c'est un appui long
            if time.monotonic() - debut >= Config.BOUTON_APPUI_LONG:
                # Attendre que le bouton soit relâché
                while self.hardware.get_button_state():
                    time.sleep(0.01)
                return "long"
        
        # Appui court détecté
        return "court"