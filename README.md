# 🌈 NeoPixel Matrix Controller - Version Optimisée

Contrôleur orienté objet pour matrices LED NeoPixel (8x8 ou autre dimension) avec Raspberry Pi Pico et CircuitPython.

## 🚀 Démarrage rapide

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

## 📦 Installation

1. **Installer CircuitPython** sur votre Raspberry Pi Pico
2. **Copier la bibliothèque** `neopixel.mpy` dans le dossier `lib/`
3. **Copier le fichier** `neopixel_matrix_optimized.py` sur votre Pico
4. **Brancher vos LEDs** : GP0 → DIN, 3.3V → VCC, GND → GND

## ✨ Fonctionnalités

- ✅ Interface orientée objet intuitive
- ✅ Gestion automatique de la luminosité
- ✅ Coordonnées cartésiennes (x, y)
- ✅ Motifs personnalisables
- ✅ Fonctions prédéfinies (arc-en-ciel, damier, etc.)
- ✅ Optimisations de performance
- ✅ Documentation complète

## 📖 Documentation

Consultez [DOCUMENTATION.md](DOCUMENTATION.md) pour :
- Guide d'utilisation détaillé
- Documentation de l'API complète
- Exemples d'utilisation avancés
- Solutions de dépannage
- Optimisations techniques

## 🎨 Exemples

### Pixel individuel
```python
matrix.set_pixel(3, 4, (255, 0, 0))  # Rouge en position (3, 4)
matrix.show()
```

### Remplissage
```python
matrix.fill((0, 255, 0))  # Toute la matrice en vert
matrix.show()
```

### Motif personnalisé
```python
def mon_motif(x, y):
    return (x * 32, y * 32, 128)

matrix.draw_pattern(mon_motif)
```

### Arc-en-ciel
```python
from neopixel_matrix_optimized import rainbow_pattern
matrix.draw_pattern(rainbow_pattern)
```

## 🔧 Améliorations par rapport au code original

| Aspect | Avant | Après |
|--------|-------|-------|
| Architecture | Procédurale | Orientée objet |
| Contrôle | Index seulement | Coordonnées (x, y) |
| Motifs | 1 fixe | Illimités |
| Performance | Basique | Optimisée |
| Documentation | Absente | Complète |
| Luminosité | Non contrôlée | Configurable |

## 🎓 Exemples avancés

### Animation de dégradé
```python
import time

scale = 0
while True:
    matrix.draw_gradient(x_scale=scale, y_scale=scale)
    scale = (scale + 1) % 256
    time.sleep(0.05)
```

### Damier animé
```python
from neopixel_matrix_optimized import checkerboard_pattern

while True:
    matrix.draw_pattern(checkerboard_pattern)
    time.sleep(0.5)
```

## 📊 Performance

- **Buffer interne** : évite les recalculs
- **auto_write=False** : mises à jour groupées
- **Validation** : prévention des erreurs
- **Économie d'énergie** : contrôle de luminosité

## 🐛 Dépannage rapide

**LEDs ne s'allument pas ?**
- Vérifier les connexions
- Augmenter la luminosité : `brightness=1.0`
- Tester : `matrix.fill((255, 0, 0))`

**Couleurs incorrectes ?**
- Essayer : `pixel_order=neopixel.GRB`
- Vérifier l'alimentation (5V stable)

**Scintillement ?**
- Réduire la fréquence de rafraîchissement
- Ajouter un condensateur 1000µF

## 📂 Structure du projet

```
.
├── neopixel_matrix_optimized.py  # Code principal optimisé
├── DOCUMENTATION.md               # Documentation complète
└── README.md                      # Ce fichier
```

## 🎯 Cas d'usage

- Matrices LED décoratives
- Jeux (Snake, Tetris, etc.)
- Visualisations de données
- Horloges LED
- Art génératif
- Notifications visuelles
- Tableaux de bord IoT

## 🔗 Ressources

- [Documentation CircuitPython](https://docs.circuitpython.org/)
- [Guide NeoPixel Adafruit](https://learn.adafruit.com/adafruit-neopixel-uberguide)
- [Pinout Raspberry Pi Pico](https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf)

## 📝 Licence

Code fourni à titre éducatif. Libre modification et redistribution.

## 🙏 Crédits

- **Bibliothèque NeoPixel** : Adafruit
- **CircuitPython** : Adafruit
- **Optimisation** : Claude (Anthropic)

---

**💡 Astuce** : Consultez [DOCUMENTATION.md](DOCUMENTATION.md) pour des exemples avancés et des tutoriels détaillés !
