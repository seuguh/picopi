# Schéma de câblage détaillé

## Vue d'ensemble du montage

```
┌─────────────────────────────────────────────────────────────┐
│                   RASPBERRY PI PICO                         │
│                                                             │
│  GP0 (Pin 1)  ●─────────────────────┐                     │
│  GP1 (Pin 2)  ●──────────────┐      │                     │
│  GND (Pin 3)  ●──────┐       │      │                     │
│  3.3V (Pin 36)●      │       │      │                     │
│  VBUS (Pin 40)●──────│───────│──────│──────┐             │
│               │      │       │      │      │             │
└───────────────│──────│───────│──────│──────│─────────────┘
                │      │       │      │      │
                │      │       │      │      │
                │      └───────┼──────┘      │
                │              │             │
                │         ┌────┴────┐        │
                │         │ BOUTON  │        │
                │         │  PUSH   │        │
                │         └─────────┘        │
                │                            │
                │                            │
                │         ┌──────────────────┴──────────────┐
                │         │    MATRICE NEOPIXEL 8x8        │
                │         │                                 │
                │         │  DIN ●  (Data Input)           │
                └─────────┼──────────────────────────────┐ │
                          │  VCC ●  (5V Power)           │ │
                          │                              │ │
                          │  GND ●                       │ │
                          │                              │ │
                          └──────────────────────────────┘ │
                                                           │
                          ┌────────────────────────────────┘
                          │
                      ┌───┴────┐
                      │  TERRE │
                      │  (GND) │
                      └────────┘
```

## Détail du câblage du bouton

### Configuration avec pull-up interne

```
                    +3.3V (pull-up interne activé)
                      │
                     ╱│╲ 
                    ╱ │ ╲  Résistance pull-up (10kΩ interne)
                   ╱  │  ╲
                      │
                      │
        GP1 ●─────────┼──────┐
                      │      │
                      │    ──┴──  Bouton poussoir
                      │    ──┬──  (Normally Open)
                      │      │
        GND ●─────────┴──────┘
```

**État du bouton :**
- **Non appuyé** : GP1 = HIGH (3.3V via pull-up)
- **Appuyé** : GP1 = LOW (0V, connexion à GND)

### Avec condensateur anti-rebond (optionnel)

```
        GP1 ●─────────┬──────┐
                      │      │
                     ═╪═    ──┴──  Bouton
                     ─┴─    ──┬──
                   10-100nF   │
                      │       │
        GND ●─────────┴───────┘
```

## Détail du câblage NeoPixel

### Connexion simple (≤8 LEDs)

```
Raspberry Pi Pico          Matrice NeoPixel 8x8
─────────────────          ────────────────────

GP0 (Pin 1)  ●────────────● DIN (Data In)
                           
VBUS (5V)    ●────────────● VCC (Power)
                           ⚠️ Max 500mA par USB
GND (Pin 3)  ●────────────● GND (Ground)
```

### Alimentation externe recommandée (>8 LEDs)

```
                            ┌───────────────────┐
Raspberry Pi Pico          │ Matrice NeoPixel  │
─────────────────          │                   │
                           │                   │
GP0 (Pin 1)  ●────────────●│ DIN               │
                           │                   │
                      ┌───●│ VCC               │
GND (Pin 3)  ●────────┼───●│ GND               │
             │        │    │                   │
             │        │    └───────────────────┘
             │        │
             │        │    ┌───────────────────┐
             │        │    │  Alimentation 5V  │
             │        │    │  (2-3A minimum)   │
             │        │    │                   │
             │        └────● +5V               │
             └─────────────● GND               │
                           │                   │
                           └───────────────────┘
```

**⚠️ IMPORTANT :**
- Ne PAS brancher VCC de l'alimentation externe au VBUS du Pico
- Partager uniquement la masse (GND) commune
- L'alimentation externe doit fournir au moins 2A

## Liste du matériel

### Composants essentiels

| Composant | Quantité | Référence | Notes |
|-----------|----------|-----------|-------|
| Raspberry Pi Pico | 1 | - | Avec headers soudés |
| Matrice NeoPixel 8x8 | 1 | WS2812B | 64 LEDs RGB |
| Bouton poussoir | 1 | Normally Open | 6x6mm ou similaire |
| Câbles Dupont | 5-10 | M-M ou M-F | Selon montage |

### Composants optionnels

| Composant | Quantité | Usage |
|-----------|----------|-------|
| Condensateur 10-100nF | 1 | Anti-rebond bouton |
| Condensateur 1000µF | 1 | Stabilisation alimentation LEDs |
| Alimentation 5V 2-3A | 1 | Pour >8 LEDs |
| Breadboard | 1 | Prototypage |
| Résistance 470Ω | 1 | Protection ligne de données |

## Calcul de la consommation

### Consommation par LED

```
1 LED blanche max = 60mA (R+G+B à 100%)
1 LED moyenne    = 20mA (utilisation typique)
64 LEDs max      = 64 × 60mA = 3840mA = 3.84A
64 LEDs typique  = 64 × 20mA = 1280mA = 1.28A
```

### Avec brightness = 0.3

```
Consommation réelle = Consommation max × Brightness
                    = 3840mA × 0.3
                    = 1152mA
                    ≈ 1.2A

→ Alimentation 2A recommandée (marge de sécurité)
```

## Précautions

### Électriques

✅ **À FAIRE :**
- Vérifier la polarité avant de brancher
- Utiliser une alimentation stable (5V ±5%)
- Ajouter un condensateur 1000µF sur l'alimentation
- Commencer avec brightness faible (0.2-0.3)
- Débrancher avant de modifier le câblage

❌ **À NE PAS FAIRE :**
- Ne jamais dépasser 5.5V sur les NeoPixels
- Ne pas brancher/débrancher sous tension
- Ne pas court-circuiter VCC et GND
- Ne pas alimenter >8 LEDs via USB uniquement
- Ne pas toucher les connexions sous tension

### Logicielles

✅ **À FAIRE :**
- Tester avec 1 LED avant la matrice complète
- Commencer par des effets simples
- Vérifier le bon pin (GP0 pour data)
- Utiliser `auto_write=False` pour performances

❌ **À NE PAS FAIRE :**
- Ne pas utiliser `brightness=1.0` sans alimentation externe
- Ne pas faire de boucles infinies sans `time.sleep()`
- Ne pas oublier `matrix.show()` après modifications

## Tests de vérification

### Test 1 : LED unique

```python
import board
import neopixel

pixels = neopixel.NeoPixel(board.GP0, 1, brightness=0.3)
pixels[0] = (255, 0, 0)  # Rouge
```

**Résultat attendu :** La première LED s'allume en rouge

---

### Test 2 : Bouton simple

```python
import board
import digitalio

button = digitalio.DigitalInOut(board.GP1)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

while True:
    if not button.value:
        print("Bouton appuyé!")
```

**Résultat attendu :** Message affiché lors de l'appui

---

### Test 3 : Matrice complète

```python
from neopixel_matrix_optimized import NeoPixelMatrix
matrix = NeoPixelMatrix(board.GP0, brightness=0.2)
matrix.fill((255, 0, 0))
matrix.show()
```

**Résultat attendu :** Toute la matrice en rouge

---

### Test 4 : Programme complet

```python
# Lancer main_with_button.py
```

**Résultat attendu :** 
- Effet 1 démarre automatiquement
- Appui bouton → affichage numéro → changement d'effet

## Dépannage visuel

### Problème : Aucune LED ne s'allume

```
Vérifier :
GP0 ──────?──────● DIN     ← Connexion correcte ?
VBUS ─────?──────● VCC     ← Alimentation présente ?
GND ──────?──────● GND     ← Masse commune ?
                  └─────── ← Orientation correcte ?
```

### Problème : Couleurs incorrectes

```
Vérifier l'ordre des couleurs :
RGB → pixels[i] = (255, 0, 0)    # Rouge
GRB → pixels[i] = (0, 255, 0)    # Rouge avec GRB

Changer dans le code :
pixels = neopixel.NeoPixel(board.GP0, 64, 
                           pixel_order=neopixel.GRB)
```

### Problème : LEDs scintillent

```
Ajouter un condensateur :

         VCC ●───┬──────● VCC (LEDs)
                 │
                ═╪═ 1000µF
                ─┴─ électrolytique
                 │
         GND ●───┴──────● GND (LEDs)
```

## Photos de montage recommandées

### Vue d'ensemble suggérée

```
┌────────────────────────────────┐
│    [Raspberry Pi Pico]         │
│                                 │
│    ┌─────┐                     │
│    │ USB │ ← Alimentation      │
│    └─────┘                     │
│                                 │
│  [Bouton]                      │
│   GP1 GND                      │
│                                 │
└────────────────────────────────┘
         │
         │ Câbles
         ▼
┌────────────────────────────────┐
│                                 │
│   Matrice NeoPixel 8x8         │
│   ┌─┬─┬─┬─┬─┬─┬─┬─┐           │
│   └─┴─┴─┴─┴─┴─┴─┴─┘           │
│   (64 LEDs RGB WS2812B)        │
│                                 │
│   DIN  VCC  GND                │
│    │    │    │                 │
└────┼────┼────┼─────────────────┘
     GP0 VBUS GND
```

## Code de test complet

```python
"""
Test de validation du montage complet
"""
import board
import digitalio
import neopixel
import time

# Configuration
LED_PIN = board.GP0
BUTTON_PIN = board.GP1

# Initialisation LEDs
pixels = neopixel.NeoPixel(LED_PIN, 64, brightness=0.2, auto_write=False)

# Initialisation bouton
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Test de validation")
print("1. Toutes les LEDs en rouge...")
pixels.fill((255, 0, 0))
pixels.show()
time.sleep(2)

print("2. Toutes les LEDs en vert...")
pixels.fill((0, 255, 0))
pixels.show()
time.sleep(2)

print("3. Toutes les LEDs en bleu...")
pixels.fill((0, 0, 255))
pixels.show()
time.sleep(2)

print("4. Test du bouton (appuyez...)") 
while True:
    if not button.value:
        print("✓ Bouton détecté!")
        pixels.fill((255, 255, 255))
        pixels.show()
        break
    time.sleep(0.1)

print("\nTest réussi! Montage OK ✓")
pixels.fill((0, 0, 0))
pixels.show()
```

---

**Date :** Janvier 2026  
**Version :** 1.0
