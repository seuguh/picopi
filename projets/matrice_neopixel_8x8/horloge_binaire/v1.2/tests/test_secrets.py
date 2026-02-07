def obtenir_heure_actuelle():
    """Version simplifiée pour tester"""
    global timestamp_reference, monotonic_reference
    
    # Si pas de référence, utiliser l'heure actuelle
    if timestamp_reference == 0:
        # Utiliser une heure de départ fixe
        timestamp_reference = 18 * 3600 + 10 * 60 + 0  # 18:10:00
        monotonic_reference = time.monotonic()
    
    # Calculer le temps écoulé
    temps_ecoule = time.monotonic() - monotonic_reference
    
    # Ajouter à l'heure de départ
    total_secondes = timestamp_reference + temps_ecoule
    
    # Secondes depuis minuit
    secondes_jour = int(total_secondes % 86400)
    heures = secondes_jour // 3600
    minutes = (secondes_jour % 3600) // 60
    secondes = int(secondes_jour % 60)
    
    # Afficher pour déboguer
    if Config.DEBUG and secondes % 10 == 0:
        print(f"[TEST] {heures:02d}:{minutes:02d}:{secondes:02d} - Écoulé: {temps_ecoule:.1f}s")
    
    # Convertir en format 12h
    if Config.FORMAT_12H:
        est_pm = heures >= 12
        heures_12 = heures % 12
        if heures_12 == 0:
            heures_12 = 12
        return heures_12, minutes, secondes, est_pm
    else:
        return heures, minutes, secondes, False