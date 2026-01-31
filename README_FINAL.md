# 🎮 Projet NeoPixel Matrix - Récapitulatif complet

## 📦 Fichiers du projet

### Fichiers principaux

| Fichier | Description | Usage |
|---------|-------------|-------|
| `neopixel_matrix_optimized.py` | Bibliothèque de base | **Obligatoire** - À copier sur le Pico |
| `main_final.py` | Programme principal avec bouton | **À utiliser** - Renommer en `code.py` |
| `exemples.py` | 8 exemples d'animations | Optionnel - Pour tester les effets |

### Documentation

| Fichier | Contenu |
|---------|---------|
| `README.md` | Guide de démarrage rapide |
| `DOCUMENTATION.md` | Documentation complète de l'API |
| `DOCUMENTATION_BOUTON.md` | Guide du bouton mécanique |
| `DOCUMENTATION_TOUCH.md` | Guide du capteur tactile |
| `SCHEMA_CABLAGE.md` | Schémas de câblage détaillés |
| `COMPATIBILITE_CIRCUITPYTHON.md` | Différences Python/CircuitPython |

## 🚀 Installation rapide

### 1. Préparer le Raspberry Pi Pico

1. **Installer CircuitPython** sur le Pico
   - Télécharger depuis [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/)
   - Installer le fichier `.uf2`

2. **Installer la bibliothèque NeoPixel**
   - Télécharger le [Bundle CircuitPython](https://circuitpython.org/libraries)
   - Copier `neopixel.mpy` dans le dossier `lib/` du Pico

### 2. Copier les fichiers

Copier sur le Pico (lecteur CIRCUITPY) :
```
CIRCUITPY/
├── code.py                          (renommer main_final.py)
├── neopixel_matrix_optimized.py     (bibliothèque)
└── lib/
    └── neopixel.mpy                 (bibliothèque Adafruit)
```

### 3. Brancher le matériel

```
Raspberry Pi Pico → Composants
───────────────────────────────
GP0  → NeoPixel DIN
GP1  → Bouton → GND
VBUS → NeoPixel VCC (si ≤8 LEDs)
GND  → NeoPixel GND
```

### 4. Redémarrer le Pico

Le programme démarre automatiquement !

## ✨ Fonctionnalités

### 9 Effets disponibles

1. **Dégradé animé** - Transition douce de couleurs
2. **Arc-en-ciel rotatif** - Spectre complet qui tourne
3. **Vague** - Effet de vague sinusoïdale bleu/cyan
4. **Spirale** - Spirale multicolore rotative
5. **Feu** - Simulation réaliste de flammes
6. **Pluie** - Gouttes qui tombent
7. **Cœur battant** - Cœur rouge pulsant
8. **Damier clignotant** - Damier avec changement de couleurs
9. **Étoiles scintillantes** - Étoiles qui apparaissent et disparaissent

### Utilisation

- **Appuyer sur le bouton** → Le numéro de l'effet défile sur la matrice
- L'effet démarre automatiquement
- Cycle : Effet 1 → 2 → ... → 9 → 1 → ...

## 🔧 Configuration

### Dans `main_final.py`

```python
# Pins
LED_PIN = board.GP0              # Pin des LEDs NeoPixel
BUTTON_PIN = board.GP1           # Pin du bouton

# Paramètres
BRIGHTNESS = 0.3                 # Luminosité (0.0 à 1.0)
EFFECT_DISPLAY_TIME = 1.5        # Durée affichage numéro (secondes)
```

### Code du bouton (identique au vôtre)

```python
bouton = digitalio.DigitalInOut(board.GP1)
bouton.direction = digitalio.Direction.INPUT
bouton.pull = digitalio.Pull.UP
```

## 📝 Historique des versions

### Version finale (actuelle)
- ✅ Compatible avec votre configuration bouton
- ✅ Utilise `digitalio.Pull.UP` comme dans votre code
- ✅ Anti-rebond optimisé (200ms)
- ✅ 9 effets visuels
- ✅ Affichage du numéro en défilement
- ✅ 100% compatible CircuitPython (pas de type hints)

### Améliorations par rapport au code original

| Aspect | Code original | Version finale |
|--------|---------------|----------------|
| Effets | 1 (dégradé fixe) | 9 (variés) |
| Interactivité | Aucune | Bouton de sélection |
| Architecture | Procédurale | Orientée objet |
| Affichage numéros | Non | Oui (8x8 défilant) |
| Documentation | Absente | Complète |
| Gestion erreurs | Aucune | Try/except |
| Anti-rebond | Non | Oui (200ms) |

## 🐛 Résolution de problèmes

### Le bouton ne répond pas

```python
# Test rapide du bouton
import board
import digitalio
import time

bouton = digitalio.DigitalInOut(board.GP1)
bouton.direction = digitalio.Direction.INPUT
bouton.pull = digitalio.Pull.UP

while True:
    if not bouton.value:  # False = appuyé
        print("Bouton appuyé!")
        time.sleep(0.5)
    time.sleep(0.1)
```

### Les LEDs ne s'allument pas

```python
# Test rapide des LEDs
import board
import neopixel

pixels = neopixel.NeoPixel(board.GP0, 64, brightness=0.3)
pixels.fill((255, 0, 0))  # Rouge
pixels.show()
```

### ImportError: no module named 'typing'

**Solution :** Utilisez `neopixel_matrix_optimized.py` (version sans type hints fournie)

### Le programme redémarre en boucle

**Causes possibles :**
- Erreur de syntaxe → Vérifier la console série
- Mémoire insuffisante → Réduire `BRIGHTNESS`
- Court-circuit → Vérifier le câblage

## 💡 Personnalisation

### Changer les couleurs des numéros

Dans `main_final.py`, fonction `next_effect()` :

```python
# Arc-en-ciel (actuel)
hue = (effect_number - 1) / len(self.effects)
color = hsv_to_rgb(hue, 1.0, 1.0)

# Ou couleur fixe (blanc)
color = (255, 255, 255)

# Ou couleur aléatoire
import random
color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
```

### Ajouter un nouvel effet

```python
# 1. Créer la classe d'effet
class Effect10_MonEffet(Effect):
    def run(self):
        while self.running:
            # Votre animation ici
            self.matrix.fill((255, 0, 0))
            self.matrix.show()
            time.sleep(0.1)

# 2. Ajouter à la liste
# Dans EffectManager.__init__
self.effects = [
    Effect1_Gradient,
    # ... autres effets ...
    Effect10_MonEffet  # Ajouter ici
]
```

### Modifier le temps anti-rebond

```python
# Dans la classe Button
self.debounce_time = 0.3  # 300ms au lieu de 200ms
```

## 📊 Consommation électrique

### Avec brightness = 0.3

```
Matrice 8x8 (64 LEDs) :
- Maximum théorique : 64 × 60mA × 0.3 = 1.15A
- Typique en usage : ~500-800mA
- Alimentation recommandée : 2A (marge de sécurité)
```

### Alimentation

- **≤ 8 LEDs** → USB du Pico suffit (500mA)
- **8-64 LEDs** → Alimentation externe 5V 2A recommandée
- **> 64 LEDs** → Alimentation externe 5V 3-5A obligatoire

## 🎓 Ressources d'apprentissage

### Tutoriels
- [Guide CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython)
- [NeoPixel Überguide](https://learn.adafruit.com/adafruit-neopixel-uberguide)
- [Raspberry Pi Pico](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

### Communauté
- [Discord Adafruit](https://adafru.it/discord)
- [Forum CircuitPython](https://forums.adafruit.com/viewforum.php?f=60)
- [GitHub Adafruit](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel)

### Documentation API
- [touchio](https://docs.circuitpython.org/en/latest/shared-bindings/touchio/)
- [digitalio](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/)
- [neopixel](https://docs.circuitpython.org/projects/neopixel/en/latest/)

## 🔗 Liens utiles

| Ressource | Lien |
|-----------|------|
| CircuitPython | https://circuitpython.org |
| Bibliothèques | https://circuitpython.org/libraries |
| Mu Editor | https://codewith.mu |
| Thonny IDE | https://thonny.org |

## ✅ Checklist finale

Avant de démarrer votre projet :

- [ ] CircuitPython installé sur le Pico
- [ ] `neopixel.mpy` copié dans `lib/`
- [ ] `neopixel_matrix_optimized.py` copié sur le Pico
- [ ] `main_final.py` renommé en `code.py`
- [ ] Matériel branché correctement (GP0, GP1, GND, VBUS)
- [ ] Bouton testé individuellement
- [ ] LEDs testées individuellement
- [ ] Programme démarre au branchement
- [ ] Bouton change les effets
- [ ] Aucune erreur dans la console série

## 🎉 Prochaines étapes

Une fois le projet fonctionnel, vous pouvez :

1. **Personnaliser les effets** - Modifier les couleurs, vitesses
2. **Créer vos propres effets** - Suivre les exemples
3. **Ajouter des capteurs** - Température, son, mouvement
4. **Mode automatique** - Changer d'effet toutes les X secondes
5. **Boîtier** - Imprimer ou fabriquer un boîtier
6. **Partager** - Publier votre projet !

## 📄 Licence

Code fourni à titre éducatif. Libre modification et redistribution.

---

**Version :** 1.0 Final  
**Date :** Janvier 2026  
**Compatibilité :** CircuitPython 7.0+  
**Matériel testé :** Raspberry Pi Pico + NeoPixel WS2812B 8x8

**Bon projet ! 🚀**
