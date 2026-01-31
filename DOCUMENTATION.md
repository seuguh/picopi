# Documentation - Contrôleur de Matrice LED NeoPixel

## 📋 Table des matières
- [Introduction](#introduction)
- [Améliorations apportées](#améliorations-apportées)
- [Installation](#installation)
- [Utilisation rapide](#utilisation-rapide)
- [Documentation de l'API](#documentation-de-lapi)
- [Exemples d'utilisation](#exemples-dutilisation)
- [Optimisations techniques](#optimisations-techniques)
- [Dépannage](#dépannage)

---

## 🎯 Introduction

Ce module fournit une interface orientée objet pour contrôler une matrice LED NeoPixel 8x8 (ou de toute autre dimension). Il simplifie la manipulation des pixels individuels et offre des fonctionnalités avancées pour créer des motifs visuels.

### Caractéristiques principales
- ✅ Interface orientée objet claire et extensible
- ✅ Gestion automatique de la luminosité
- ✅ Support des coordonnées cartésiennes (x, y)
- ✅ Fonctions de motifs prédéfinis
- ✅ Système de buffer pour optimiser les performances
- ✅ Gestion propre des erreurs
- ✅ Documentation complète avec type hints

---

## 🚀 Améliorations apportées

### 1. **Architecture orientée objet**
- Création d'une classe `NeoPixelMatrix` réutilisable
- Encapsulation des données et méthodes
- Meilleure organisation du code

### 2. **Optimisations de performance**
- **Buffer interne** : évite les recalculs inutiles
- **Contrôle de luminosité** : `brightness` réduit la consommation d'énergie
- **Limitation des valeurs RGB** : utilisation de `min()` pour éviter les dépassements
- **`auto_write=False`** : mise à jour manuelle pour de meilleures performances

### 3. **Fonctionnalités ajoutées**
- Conversion bidirectionnelle index ↔ coordonnées (x, y)
- Méthode `set_pixel()` pour contrôle pixel par pixel
- Méthode `fill()` pour remplissage rapide
- Méthode `clear()` pour éteindre tous les LEDs
- Support des motifs personnalisés via callbacks
- Fonctions utilitaires (arc-en-ciel, damier, conversion HSV→RGB)

### 4. **Robustesse**
- Type hints pour une meilleure documentation
- Validation des coordonnées
- Gestion des exceptions (`KeyboardInterrupt`)
- Nettoyage automatique à l'arrêt

### 5. **Maintenabilité**
- Constants configurables en haut du fichier
- Documentation docstring complète
- Commentaires explicatifs
- Structure modulaire

---

## 📦 Installation

### Prérequis
- Raspberry Pi Pico ou microcontrôleur compatible CircuitPython
- CircuitPython 7.0+
- Bande LED NeoPixel (WS2812B ou compatible)

### Installation des dépendances
```bash
# Sur votre Raspberry Pi Pico, assurez-vous d'avoir CircuitPython installé
# Copiez les bibliothèques nécessaires dans le dossier lib/
# - neopixel.mpy
```

### Configuration matérielle
```
Raspberry Pi Pico  →  NeoPixel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GP0 (Pin 1)        →  DIN (Data In)
3.3V               →  VCC
GND                →  GND
```

⚠️ **Important** : Pour plus de 8 LEDs, utilisez une alimentation externe 5V.

---

## ⚡ Utilisation rapide

### Exemple minimal
```python
import board
from neopixel_matrix_optimized import NeoPixelMatrix

# Initialisation
matrix = NeoPixelMatrix(board.GP0, width=8, height=8, brightness=0.3)

# Afficher un dégradé
matrix.draw_gradient()

# Nettoyer
matrix.clear()
```

### Exemple avec boucle
```python
import time

matrix = NeoPixelMatrix(board.GP0)

try:
    while True:
        matrix.draw_gradient()
        time.sleep(0.1)
except KeyboardInterrupt:
    matrix.clear()
```

---

## 📖 Documentation de l'API

### Classe `NeoPixelMatrix`

#### `__init__(pin, width=8, height=8, brightness=0.3)`
Initialise la matrice LED.

**Paramètres :**
- `pin` : Pin GPIO (ex: `board.GP0`)
- `width` : Largeur de la matrice (défaut: 8)
- `height` : Hauteur de la matrice (défaut: 8)
- `brightness` : Luminosité de 0.0 à 1.0 (défaut: 0.3)

**Exemple :**
```python
matrix = NeoPixelMatrix(board.GP0, width=16, height=16, brightness=0.5)
```

---

#### `get_index(x, y) -> int`
Convertit les coordonnées (x, y) en index de pixel.

**Paramètres :**
- `x` : Coordonnée x (0 à width-1)
- `y` : Coordonnée y (0 à height-1)

**Retourne :** Index du pixel (int)

**Exemple :**
```python
index = matrix.get_index(3, 2)  # Retourne 19 pour une matrice 8x8
```

---

#### `get_coords(index) -> Tuple[int, int]`
Convertit un index en coordonnées (x, y).

**Paramètres :**
- `index` : Index du pixel (0 à num_pixels-1)

**Retourne :** Tuple (x, y)

**Exemple :**
```python
x, y = matrix.get_coords(19)  # Retourne (3, 2)
```

---

#### `set_pixel(x, y, color)`
Définit la couleur d'un pixel spécifique.

**Paramètres :**
- `x` : Coordonnée x
- `y` : Coordonnée y
- `color` : Tuple RGB (r, g, b) avec valeurs 0-255

**Exemple :**
```python
matrix.set_pixel(0, 0, (255, 0, 0))  # Pixel rouge en haut à gauche
matrix.show()  # Ne pas oublier d'afficher !
```

---

#### `fill(color)`
Remplit toute la matrice avec une couleur.

**Paramètres :**
- `color` : Tuple RGB (r, g, b)

**Exemple :**
```python
matrix.fill((0, 255, 0))  # Toute la matrice en vert
matrix.show()
```

---

#### `clear()`
Éteint tous les LEDs.

**Exemple :**
```python
matrix.clear()  # Équivalent à fill((0, 0, 0)) + show()
```

---

#### `show()`
Met à jour l'affichage de la matrice.

**Exemple :**
```python
matrix.set_pixel(0, 0, (255, 0, 0))
matrix.set_pixel(1, 1, (0, 255, 0))
matrix.show()  # Affiche les changements
```

---

#### `draw_gradient(x_scale=32, y_scale=32, z_value=50)`
Dessine un dégradé de couleurs.

**Paramètres :**
- `x_scale` : Facteur pour la composante rouge (défaut: 32)
- `y_scale` : Facteur pour la composante verte (défaut: 32)
- `z_value` : Valeur constante pour le bleu (défaut: 50)

**Exemple :**
```python
matrix.draw_gradient(x_scale=40, y_scale=40, z_value=100)
```

---

#### `draw_pattern(pattern_func)`
Dessine un motif personnalisé.

**Paramètres :**
- `pattern_func` : Fonction qui prend (x, y) et retourne un tuple RGB

**Exemple :**
```python
def mon_motif(x, y):
    if x == y:
        return (255, 255, 255)  # Diagonale blanche
    return (0, 0, 0)            # Reste noir

matrix.draw_pattern(mon_motif)
```

---

### Fonctions utilitaires

#### `rainbow_pattern(x, y) -> Tuple[int, int, int]`
Crée un motif arc-en-ciel.

**Exemple :**
```python
matrix.draw_pattern(rainbow_pattern)
```

---

#### `checkerboard_pattern(x, y) -> Tuple[int, int, int]`
Crée un damier noir et blanc.

**Exemple :**
```python
matrix.draw_pattern(checkerboard_pattern)
```

---

#### `hsv_to_rgb(h, s, v) -> Tuple[int, int, int]`
Convertit HSV en RGB.

**Paramètres :**
- `h` : Teinte (0.0 à 1.0)
- `s` : Saturation (0.0 à 1.0)
- `v` : Valeur/Luminosité (0.0 à 1.0)

**Exemple :**
```python
couleur = hsv_to_rgb(0.5, 1.0, 1.0)  # Cyan pur
matrix.fill(couleur)
matrix.show()
```

---

## 💡 Exemples d'utilisation

### Exemple 1 : Animation de dégradé
```python
import board
import time
from neopixel_matrix_optimized import NeoPixelMatrix

matrix = NeoPixelMatrix(board.GP0)

try:
    scale = 0
    while True:
        matrix.draw_gradient(x_scale=scale, y_scale=scale, z_value=50)
        scale = (scale + 1) % 256
        time.sleep(0.05)
except KeyboardInterrupt:
    matrix.clear()
```

---

### Exemple 2 : Damier animé
```python
import time
from neopixel_matrix_optimized import NeoPixelMatrix, checkerboard_pattern

matrix = NeoPixelMatrix(board.GP0, brightness=0.2)

def animated_checker(x, y):
    offset = int(time.monotonic() * 2) % 2
    if (x + y + offset) % 2 == 0:
        return (255, 0, 0)
    return (0, 0, 255)

try:
    while True:
        matrix.draw_pattern(animated_checker)
        time.sleep(0.5)
except KeyboardInterrupt:
    matrix.clear()
```

---

### Exemple 3 : Smiley
```python
matrix = NeoPixelMatrix(board.GP0)

# Définir les pixels du smiley
eyes = [(2, 2), (5, 2)]
mouth = [(2, 5), (3, 6), (4, 6), (5, 5)]

matrix.clear()

# Dessiner les yeux
for x, y in eyes:
    matrix.set_pixel(x, y, (255, 255, 0))

# Dessiner la bouche
for x, y in mouth:
    matrix.set_pixel(x, y, (255, 255, 0))

matrix.show()
```

---

### Exemple 4 : Texte défilant (concept)
```python
def draw_letter_A(matrix, offset_x=0):
    """Dessine la lettre A"""
    pixels = [
        (1+offset_x, 0), (2+offset_x, 0),
        (0+offset_x, 1), (3+offset_x, 1),
        (0+offset_x, 2), (1+offset_x, 2), (2+offset_x, 2), (3+offset_x, 2),
        (0+offset_x, 3), (3+offset_x, 3),
        (0+offset_x, 4), (3+offset_x, 4)
    ]
    
    matrix.clear()
    for x, y in pixels:
        if 0 <= x < 8:  # Vérifier les limites
            matrix.set_pixel(x, y, (0, 255, 0))
    matrix.show()

# Animation de défilement
for offset in range(-4, 8):
    draw_letter_A(matrix, offset)
    time.sleep(0.1)
```

---

## 🔧 Optimisations techniques

### 1. Buffer interne
Le code utilise un buffer `_buffer` pour stocker les couleurs. Cela permet :
- De connaître l'état actuel sans interroger le hardware
- D'optimiser les opérations répétées
- De faciliter les animations

### 2. Contrôle de la luminosité
```python
matrix = NeoPixelMatrix(board.GP0, brightness=0.3)
```
- Réduit la consommation d'énergie
- Évite la surchauffe
- Prolonge la durée de vie des LEDs

### 3. Limitation des valeurs RGB
```python
color = (min(x * scale, 255), min(y * scale, 255), min(z, 255))
```
Évite les dépassements qui pourraient causer des couleurs incorrectes.

### 4. `auto_write=False`
```python
pixels = neopixel.NeoPixel(pin, num_pixels, auto_write=False)
```
- Permet de grouper plusieurs modifications
- Réduit les communications I2C/SPI
- Améliore les performances globales

---

## 🐛 Dépannage

### Problème : Les LEDs ne s'allument pas
**Solutions :**
1. Vérifier les connexions (DIN, VCC, GND)
2. Vérifier que le bon pin est configuré
3. Augmenter la luminosité : `brightness=1.0`
4. Tester avec une seule LED :
   ```python
   matrix.set_pixel(0, 0, (255, 0, 0))
   matrix.show()
   ```

---

### Problème : Couleurs incorrectes
**Solutions :**
1. Vérifier l'ordre des couleurs (RGB vs GRB) :
   ```python
   pixels = neopixel.NeoPixel(pin, num, pixel_order=neopixel.GRB)
   ```
2. Tester avec des couleurs primaires pures
3. Vérifier l'alimentation (les LEDs NeoPixel sont sensibles au voltage)

---

### Problème : Scintillement
**Solutions :**
1. Réduire le temps de rafraîchissement : `time.sleep(0.05)` → `time.sleep(0.1)`
2. Utiliser une alimentation stabilisée
3. Ajouter un condensateur (1000µF) sur l'alimentation

---

### Problème : Performances lentes
**Solutions :**
1. Éviter d'appeler `show()` trop fréquemment
2. Grouper les modifications :
   ```python
   for x in range(8):
       for y in range(8):
           matrix.set_pixel(x, y, color)
   matrix.show()  # Une seule fois à la fin
   ```
3. Utiliser `fill()` au lieu de boucles pour remplir entièrement

---

### Problème : Mémoire insuffisante
**Solutions :**
1. Réduire la taille de la matrice
2. Utiliser CircuitPython au lieu de MicroPython
3. Supprimer les imports inutilisés
4. Réduire le nombre de fonctions de motifs

---

## 📊 Comparaison : Code original vs Code optimisé

| Aspect | Code original | Code optimisé |
|--------|---------------|---------------|
| Lignes de code | ~20 lignes | ~280 lignes (avec doc) |
| Réutilisabilité | Faible | Élevée (classe) |
| Extensibilité | Difficile | Facile (méthodes) |
| Performance | Basique | Optimisée (buffer) |
| Gestion d'erreurs | Aucune | Complète |
| Documentation | Absente | Complète |
| Contrôle pixel | Indirect | Direct (x, y) |
| Motifs | 1 (dégradé) | Illimités (callbacks) |
| Économie d'énergie | Non | Oui (brightness) |

---

## 📝 Licence et crédits

Ce code est fourni à titre éducatif et peut être librement modifié et redistribué.

### Bibliothèques utilisées
- **CircuitPython** : https://circuitpython.org/
- **Adafruit NeoPixel** : https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel

### Ressources complémentaires
- [Guide NeoPixel d'Adafruit](https://learn.adafruit.com/adafruit-neopixel-uberguide)
- [Documentation CircuitPython](https://docs.circuitpython.org/)
- [Raspberry Pi Pico Pinout](https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf)

---

## 🎓 Pour aller plus loin

### Idées d'amélioration
1. **Animations prédéfinies** : vague, spirale, explosion
2. **Support de sprites** : affichage d'images bitmap
3. **Effets sonores** : réagir à un microphone
4. **Mode économie d'énergie** : extinction automatique
5. **API web** : contrôle via WiFi (avec Pico W)
6. **Sauvegarde de motifs** : stocker des configurations
7. **Détection de mouvement** : avec capteur PIR
8. **Horloge LED** : affichage de l'heure

### Défis de programmation
1. Créer un jeu de Snake sur la matrice
2. Implémenter un visualiseur de spectre audio
3. Faire une animation de feu réaliste
4. Créer un générateur de QR codes affichable
5. Implémenter le Jeu de la Vie de Conway

---

**Version :** 1.0  
**Dernière mise à jour :** Janvier 2026  
**Auteur :** Code optimisé par Claude (Anthropic)
