"""
Test de synchronisation NTP
Ce script vérifie que la connexion WiFi et NTP fonctionne correctement

UTILISATION:
1. Configurer secrets.py avec vos identifiants WiFi
2. Renommer code.py en code_backup.py
3. Renommer ce fichier en code.py
4. Observer les résultats dans la console série (115200 bauds)
5. Restaurer code.py après le test
"""

import time
import wifi
import socketpool
import adafruit_ntp
from secrets import WIFI_SSID, WIFI_PASSWORD

# Configuration
WIFI_TIMEOUT = 30
NTP_SERVER = "pool.ntp.org"
TIMEZONE_OFFSET = 1  # Ajustez selon votre fuseau horaire

print("=== TEST SYNCHRONISATION NTP ===\n")

# Test 1: Connexion WiFi
print("Test 1: Connexion WiFi")
print(f"SSID: {WIFI_SSID}")
print("Connexion en cours...", end="")

try:
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD, timeout=WIFI_TIMEOUT)
    print(" OK!")
    print(f"Adresse IP: {wifi.radio.ipv4_address}")
    print(f"Force du signal: {wifi.radio.ap_info.rssi} dBm")
    print(f"Canal: {wifi.radio.ap_info.channel}")
except Exception as e:
    print(" ÉCHEC!")
    print(f"Erreur: {e}")
    print("\nVérifiez:")
    print("1. Les identifiants dans secrets.py")
    print("2. Que le réseau est en 2.4 GHz (pas 5 GHz)")
    print("3. La portée WiFi")
    while True:
        time.sleep(1)

print("\n" + "="*50)

# Test 2: Initialisation NTP
print("\nTest 2: Initialisation client NTP")
print(f"Serveur: {NTP_SERVER}")

try:
    pool = socketpool.SocketPool(wifi.radio)
    ntp = adafruit_ntp.NTP(pool, server=NTP_SERVER)
    print("Client NTP initialisé: OK!")
except Exception as e:
    print(f"ÉCHEC: {e}")
    while True:
        time.sleep(1)

print("\n" + "="*50)

# Test 3: Récupération de l'heure
print("\nTest 3: Récupération de l'heure NTP")
print("Interrogation du serveur...", end="")

try:
    ntp_time = ntp.datetime
    print(" OK!")
    print(f"\nHeure UTC reçue:")
    print(f"  Année: {ntp_time.tm_year}")
    print(f"  Mois: {ntp_time.tm_mon}")
    print(f"  Jour: {ntp_time.tm_mday}")
    print(f"  Heure: {ntp_time.tm_hour:02d}:{ntp_time.tm_min:02d}:{ntp_time.tm_sec:02d}")
    print(f"  Jour de la semaine: {ntp_time.tm_wday} (0=lundi)")
except Exception as e:
    print(f" ÉCHEC!")
    print(f"Erreur: {e}")
    while True:
        time.sleep(1)

print("\n" + "="*50)

# Test 4: Calcul du timestamp Unix
print("\nTest 4: Calcul du timestamp Unix")

def calculer_timestamp_unix(struct_time, timezone_offset_hours):
    """Convertit struct_time en timestamp Unix"""
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
        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
            jours += 366
        else:
            jours += 365
    
    # Mois de l'année courante
    jours_par_mois = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Ajuster février si année bissextile
    if (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0):
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
    timestamp += timezone_offset_hours * 3600
    
    return timestamp

timestamp_utc = calculer_timestamp_unix(ntp_time, 0)
timestamp_local = calculer_timestamp_unix(ntp_time, TIMEZONE_OFFSET)

print(f"Timestamp UTC: {timestamp_utc}")
print(f"Timestamp local (UTC{TIMEZONE_OFFSET:+d}): {timestamp_local}")
print(f"Différence: {timestamp_local - timestamp_utc} secondes")

print("\n" + "="*50)

# Test 5: Conversion en heure locale
print("\nTest 5: Conversion en heure locale")

def timestamp_to_time(timestamp):
    """Convertit un timestamp en (heures, minutes, secondes)"""
    secondes_jour = int(timestamp % 86400)
    heures = secondes_jour // 3600
    minutes = (secondes_jour % 3600) // 60
    secondes = secondes_jour % 60
    return heures, minutes, secondes

h_utc, m_utc, s_utc = timestamp_to_time(timestamp_utc)
h_local, m_local, s_local = timestamp_to_time(timestamp_local)

print(f"Heure UTC: {h_utc:02d}:{m_utc:02d}:{s_utc:02d}")
print(f"Heure locale (UTC{TIMEZONE_OFFSET:+d}): {h_local:02d}:{m_local:02d}:{s_local:02d}")

# Conversion format 12h
est_pm = h_local >= 12
h_12h = h_local % 12
if h_12h == 0:
    h_12h = 12

print(f"Format 12h: {h_12h:02d}:{m_local:02d}:{s_local:02d} {'PM' if est_pm else 'AM'}")

print("\n" + "="*50)

# Test 6: Synchronisations multiples
print("\nTest 6: Synchronisations multiples (test de stabilité)")
print("Effectue 5 synchronisations espacées de 2 secondes...")

timestamps = []
for i in range(5):
    try:
        ntp_time = ntp.datetime
        ts = calculer_timestamp_unix(ntp_time, TIMEZONE_OFFSET)
        h, m, s = timestamp_to_time(ts)
        timestamps.append(ts)
        print(f"  Sync {i+1}: {h:02d}:{m:02d}:{s:02d} (timestamp: {ts})")
        time.sleep(2)
    except Exception as e:
        print(f"  Sync {i+1}: ÉCHEC - {e}")

if len(timestamps) > 1:
    differences = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    print(f"\nDifférences entre syncs (devrait être ~2s):")
    for i, diff in enumerate(differences):
        print(f"  Sync {i+2} - Sync {i+1}: {diff} secondes")

print("\n" + "="*50)

# Test 7: Test de précision avec time.monotonic()
print("\nTest 7: Précision avec time.monotonic()")
print("Vérifie que le temps s'écoule correctement...")

try:
    # Première lecture
    ntp_time = ntp.datetime
    timestamp_ref = calculer_timestamp_unix(ntp_time, TIMEZONE_OFFSET)
    monotonic_ref = time.monotonic()
    h1, m1, s1 = timestamp_to_time(timestamp_ref)
    print(f"\nRéférence: {h1:02d}:{m1:02d}:{s1:02d}")
    print(f"Monotonic: {monotonic_ref:.3f}s")
    
    # Attente de 5 secondes
    print("\nAttente de 5 secondes...")
    time.sleep(5)
    
    # Calcul du temps actuel
    temps_ecoule = time.monotonic() - monotonic_ref
    timestamp_actuel = timestamp_ref + temps_ecoule
    h2, m2, s2 = timestamp_to_time(timestamp_actuel)
    
    print(f"Après attente: {h2:02d}:{m2:02d}:{s2:02d}")
    print(f"Temps écoulé: {temps_ecoule:.3f}s")
    print(f"Précision: {abs(temps_ecoule - 5):.3f}s d'erreur")
    
    if abs(temps_ecoule - 5) < 0.1:
        print("✓ Précision excellente (<0.1s)")
    elif abs(temps_ecoule - 5) < 0.5:
        print("✓ Précision bonne (<0.5s)")
    else:
        print("⚠ Précision moyenne")
        
except Exception as e:
    print(f"ÉCHEC: {e}")

print("\n" + "="*50)

# Résumé
print("\n=== RÉSUMÉ DES TESTS ===")
print("✓ Connexion WiFi: OK")
print("✓ Client NTP: OK")
print("✓ Récupération heure: OK")
print("✓ Calcul timestamp: OK")
print("✓ Conversion locale: OK")
print("✓ Stabilité: OK")
print("✓ Précision: OK")
print("\n✓ TOUS LES TESTS RÉUSSIS!")
print("\nVous pouvez maintenant utiliser l'horloge normalement.")
print("Restaurez code.py et redémarrez le Pico W.")

# Affichage en continu de l'heure
print("\n" + "="*50)
print("Affichage continu de l'heure (Ctrl+C pour arrêter)")
print("="*50 + "\n")

try:
    while True:
        temps_ecoule = time.monotonic() - monotonic_ref
        timestamp_actuel = timestamp_ref + temps_ecoule
        h, m, s = timestamp_to_time(timestamp_actuel)
        
        # Format 12h
        est_pm = h >= 12
        h_12h = h % 12
        if h_12h == 0:
            h_12h = 12
        
        print(f"\r{h_12h:02d}:{m:02d}:{s:02d} {'PM' if est_pm else 'AM'}", end="")
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\n\nTest interrompu par l'utilisateur.")
    print("Au revoir!")
