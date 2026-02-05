"""
Utilitaires de gestion du temps et NTP
"""

import time
from config import Config

class TimeManager:
    def __init__(self):
        self.timestamp_reference = 0
        self.monotonic_reference = 0
        self.timezone_offset = Config.TIMEZONE_OFFSET
        self.last_ntp_sync = 0
    
    def calculer_timestamp_unix(self, struct_time):
        """
        Convertit un struct_time en timestamp Unix
        
        Args:
            struct_time: objet time.struct_time de NTP
        
        Returns:
            int: timestamp Unix en secondes
        """
        annee = struct_time.tm_year
        mois = struct_time.tm_mon
        jour = struct_time.tm_mday
        heure = struct_time.tm_hour
        minute = struct_time.tm_min
        seconde = struct_time.tm_sec
        
        # Compter les jours depuis le 1er janvier 1970
        jours = 0
        
        # Années complètes depuis 1970
        for y in range(1970, annee):
            if self._est_bissextile(y):
                jours += 366
            else:
                jours += 365
        
        # Mois de l'année courante
        jours_par_mois = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Ajuster février si année bissextile
        if self._est_bissextile(annee):
            jours_par_mois[1] = 29
        
        # Ajouter les jours des mois écoulés
        for m in range(1, mois):
            jours += jours_par_mois[m - 1]
        
        # Ajouter les jours du mois courant
        jours += jour - 1
        
        # Convertir en secondes
        timestamp = jours * 86400
        timestamp += heure * 3600
        timestamp += minute * 60
        timestamp += seconde
        
        # Appliquer le fuseau horaire
        timestamp += self.timezone_offset * 3600
        
        return int(timestamp)
    
    def _est_bissextile(self, annee):
        """Détermine si une année est bissextile"""
        return (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0)
    
    def synchroniser_ntp(self, ntp_time):
        """
        Synchronise l'horloge interne avec le temps NTP
        
        Args:
            ntp_time: struct_time récupéré de NTP
        """
        self.timestamp_reference = self.calculer_timestamp_unix(ntp_time)
        self.monotonic_reference = time.monotonic()
        self.last_ntp_sync = time.monotonic()
    
    def obtenir_timestamp_actuel(self):
        """
        Retourne le timestamp Unix actuel basé sur la dernière synchronisation
        """
        temps_ecoule = time.monotonic() - self.monotonic_reference
        return self.timestamp_reference + int(temps_ecoule)
    
    def obtenir_heure_actuelle(self):
        """
        Retourne (heures, minutes, secondes, est_pm)
        Note: est_pm est toujours False en format 24h, True/False en format 12h
        """
        timestamp = self.obtenir_timestamp_actuel()
        
        # Extraire l'heure du jour (0-86399 secondes)
        secondes_jour = timestamp % 86400
        
        heures = secondes_jour // 3600
        minutes = (secondes_jour % 3600) // 60
        secondes = secondes_jour % 60
        
        # Conversion format 12h
        if Config.FORMAT_12H:
            est_pm = heures >= 12
            heures_12h = heures % 12
            if heures_12h == 0:
                heures_12h = 12
            return heures_12h, minutes, secondes, est_pm
        else:
            # Format 24h: est_pm est toujours False
            return heures, minutes, secondes, False
    
    def besoin_resynchronisation(self):
        """Vérifie si une resynchronisation NTP est nécessaire"""
        return time.monotonic() - self.last_ntp_sync >= Config.NTP_SYNC_INTERVAL