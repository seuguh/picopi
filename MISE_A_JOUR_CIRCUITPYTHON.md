# Guide de mise à jour de CircuitPython sur Raspberry Pi Pico

**Dernière mise à jour** : 31 janvier 2026  
**Niveau de difficulté** : Débutant

## Vue d'ensemble
Ce guide détaille la procédure pour installer ou mettre à jour le firmware CircuitPython sur une carte Raspberry Pi Pico (ou compatible RP2040). CircuitPython remplace MicroPython sur la carte et crée un lecteur `CIRCUITPY` où vous pouvez directement éditer vos fichiers Python.

## Prérequis
- **Carte** : Raspberry Pi Pico, Pico W, Pico 2 ou carte compatible RP2040.
- **Câble** : Un câble USB de données (pas seulement un câble de charge).
- **Connexion Internet** : Pour télécharger le firmware.
- **Ordinateur** : Windows, macOS ou Linux.

## Étapes de mise à jour

### 1. Télécharger le bon firmware
1. Identifiez le modèle exact de votre carte (ex. "Raspberry Pi Pico", "Pico W", "Pico 2").
2. Accédez au site officiel [CircuitPython.org](https://circuitpython.org/).
3. Sur la page d'accueil, utilisez le menu "Downloads" ou la barre de recherche pour trouver votre carte.
    - Exemple direct : [circuitpython.org/board/raspberry_pi_pico/](https://circuitpython.org/board/raspberry_pi_pico/)
4. Téléchargez le fichier **`.uf2`** de la dernière version **STABLE** (pas la version Alpha ou Beta).

### 2. Mettre la carte en mode bootloader
Cette étape rend la carte détectable comme un stockage USB.
1. **Maintenez le bouton `BOOTSEL`** (Bouton Blanc) enfoncé sur la carte.
2. **Branchez le câble USB** à la carte et à votre ordinateur.
3. **Relâchez le bouton `BOOTSEL`**.

**Résultat attendu** : Un nouveau lecteur nommé **`RPI-RP2`** apparaît sur votre ordinateur (comme une clé USB).

### 3. Installer le firmware CircuitPython
1. Accédez au dossier de téléchargement et localisez le fichier **`.uf2`**.
2. Faites un **Glisser-Déposer** (ou Copier-Coller) de ce fichier vers le lecteur **`RPI-RP2`**.
3. Le processus de copie est très rapide. La carte **se redémarre automatiquement**.
4. Le lecteur **`RPI-RP2`** disparaît et est remplacé par un nouveau lecteur nommé **`CIRCUITPY`**.

**✅ La mise à jour est terminée.** Le firmware CircuitPython est maintenant installé.

## Vérification et dépannage

### Comment vérifier la version installée ?
1. Ouvrez un terminal de communication série (ex. `screen` sur macOS/Linux, Putty sur Windows).
2. Connectez-vous au port série de la carte (ex. `COM3` sur Windows, `/dev/tty.usbmodemXX` sur macOS).
3. Un prompt **`>>>`** (REPL) CircuitPython s'affiche.
4. Tapez les commandes suivantes :
    ```python
    import os
    os.uname()
    ```
    La version de CircuitPython s'affichera dans la réponse.

### Problèmes courants et solutions

| Problème | Cause probable | Solution |
| :--- | :--- | :--- |
| Le lecteur **`RPI-RP2`** n'apparaît pas. | 1. Câble USB non adapté (charge uniquement). <br> 2. Bouton `BOOTSEL` mal actionné. <br> 3. Pilote manquant (Windows ancien). | 1. **Changez de câble USB.** C'est la cause la plus fréquente. <br> 2. Recommencez : enfoncez le bouton, branchez, relâchez. <br> 3. Sous Windows, attendez l'installation automatique ou installez le pilote "RP2 Boot". |
| Erreur à la copie du fichier `.uf2`. | Lecteur **`RPI-RP2`** plein ou en lecture seule. | C'est normal. La carte ne libère pas son espace avant un nouveau flash. Recommencez depuis l'**Étape 2**. |
| Le lecteur **`CIRCUITPY`** n'apparaît pas après le flash. | Flash échoué ou fichier `.uf2` incorrect. | 1. Vérifiez que le fichier correspond exactement à votre modèle de carte. <br> 2. Recommencez toute la procédure. |
| La carte semble "morte" (aucun lecteur). | Bootloader corrompu (rare). | Forcez le mode bootloader avec une séquence spéciale : débranchez USB, appuyez sur `BOOTSEL`, rebranchez USB, relâchez `BOOTSEL`. |

## Programmer après la mise à jour

### Avec VSCode
1. Installez l'extension **`RT-Thread MicroPython`** (anciennement MicroPico) dans VSCode.
2. Ouvrez le dossier correspondant au lecteur **`CIRCUITPY`**.
3. Créez ou modifiez le fichier **`code.py`** (ou `main.py`). **Chaque sauvegarde** sur ce fichier provoque un redémarrage automatique de la carte et exécute le nouveau code.

### Fichiers importants sur `CIRCUITPY`
- **`code.py`** : Script principal, exécuté automatiquement au démarrage.
- **`lib/`** : Dossier pour les bibliothèques externes (`.mpy`).
- **`settings.toml`** : Pour configurer les paramètres WiFi (sur Pico W).

## Ressources utiles
- **Documentation officielle** : [learn.adafruit.com/welcome-to-circuitpython](https://learn.adafruit.com/welcome-to-circuitpython)
- **Guide d'installation vidéo** : [Adafruit CircuitPython Installation](https://www.youtube.com/watch?v=8w8qHcPhiPM)
- **Bibliothèque de pilotes (drivers)** : [circuitpython.org/libraries](https://circuitpython.org/libraries)

---

*Note : Ce processus efface tout le système de fichiers précédent de la carte. Sauvegardez vos fichiers importants du lecteur `CIRCUITPY` avant de procéder si vous effectuez une mise à jour.*