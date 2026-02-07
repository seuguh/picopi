NOTICE TECHNIQUE - HORLOGE BCD MATRICIELLE
===========================================

DESCRIPTION GENERALE
--------------------
Horloge numerique utilisant un codage BCD (Binary Coded Decimal) sur matrice 
LED 8x8, avec synchronisation WiFi et indicateurs de connexion reseau. 
Developpee pour Raspberry Pi Pico W en CircuitPython.

FONCTIONNALITES PRINCIPALES
---------------------------

AFFICHAGE:
- Format: Heure en 12h (AM/PM) avec minutes et secondes
- Codage: BCD sur matrice 8x8 NeoPixel (64 LEDs)
- Organisation des colonnes:
  * Colonnes 0-1: Heures (4 bits)
  * Colonnes 2-3: Dizaines minutes (3 bits) + indicateurs reseau
  * Colonnes 4-5: Unites minutes (4 bits)
  * Colonne 6: Dizaines secondes (3 bits)
  * Colonne 7: Unites secondes (4 bits)

COULEURS:
- Heures/Minutes: Bleu (6h-22h) / Rouge fonce (22h-6h)
- Secondes: Cyan
- Indicateurs WiFi/Internet:
  * Vert: Connecte et fonctionnel
  * Jaune: Test en cours
  * Rouge: Probleme de connexion

GESTION RESEAU:
- Connexion WiFi automatique
- Synchronisation horaire via NTP (pool.ntp.org)
- Tests periodiques de connexion (30 secondes)
- Tentatives de reconnexion automatique (2x a 5s d'intervalle)
- Indicateurs visuels en temps reel

GESTION ENERGETIQUE:
- Mode eteint avec deconnexion WiFi
- Transitions douces entre etats
- Bouton de controle multi-fonctions

UTILISATION
-----------

LECTURE DE L'HEURE:
1. Heures: 2 colonnes a gauche, lisez la hauteur d'allumage
2. Minutes: 4 colonnes centrales (dizaines + unites)
3. Secondes: 2 colonnes a droite (dizaines + unites)
4. Connexion: Points centraux (WiFi bas, Internet haut)

COMMANDES BOUTON:
- Appui court (<1.5s):
  * Mode eteint -> Allume et synchronise
  * Mode allume -> Force resynchronisation NTP
- Appui long (>=1.5s): Allume -> Eteint l'affichage

INDICATEURS RESEAU:
WiFi (rangee 6, colonnes 2-3):
  - Vert: Connecte au reseau local
  - Jaune: Test de connexion en cours
  - Rouge: Impossible de se connecter

Internet (rangee 7, colonnes 2-3):
  - Vert: Acces Internet/NTP fonctionnel
  - Jaune: Test de connectivite en cours
  - Rouge: Pas d'acces Internet

CONFIGURATION
-------------

PARAMETRES MODIFIABLES (config.py):
# WiFi
WIFI_TIMEOUT = 30  # Secondes

# NTP
NTP_SERVER = "pool.ntp.org"
TIMEZONE_OFFSET = 1  # UTC+1 pour Paris
NTP_SYNC_INTERVAL = 3600  # 1 heure

# Tests reseau
TEST_WIFI_INTERVAL = 30       # Test toutes les 30s
TEST_WIFI_RETRIES = 2         # 2 tentatives
TEST_WIFI_RETRY_INTERVAL = 5  # 5s entre tentatives

# Luminosite
MATRICE_LUMINOSITE = 0.1      # 10% de luminosite

CONFIGURATION WiFi (secrets.py):
WIFI_SSID = "votre_ssid"
WIFI_PASSWORD = "votre_mot_de_passe"

COMPORTEMENT DES TESTS RESEAU
-----------------------------

SEQUENCE AU DEMARRAGE:
1. Indicateurs passent en jaune immediatement
2. Test WiFi -> Vert ou Rouge
3. Si WiFi vert, test Internet -> Vert ou Rouge
4. Si les deux verts, synchronisation NTP automatique

EN FONCTIONNEMENT:
- Toutes les 30 secondes: Test automatique
- En cas d'echec: 2 tentatives a 5s d'intervalle
- Apres double echec: Indicateur rouge pendant 30s
- Mode eteint: Tests arretes, WiFi deconnecte

INDICATEURS VISUELS
-------------------

ETAT NORMAL:
- Heure affichee en continu
- Indicateurs reseau verts
- Transition douce entre changements de minute/seconde

PROBLEMES RESEAU:
- Indicateur concerne passe en jaune pendant les tests
- Apres echec: passe en rouge
- L'horloge continue avec la derniere heure connue

ERREUR INITIALE:
- Croix rouge sur toute la matrice uniquement si:
  * Pas de connexion WiFi initiale
  * Pas de synchronisation NTP dans les 10 premieres secondes

ARCHITECTURE LOGICIELLE
-----------------------

COMPOSANTS PRINCIPAUX:
1. BCDClock: Classe