# Documentation - Sélecteur d'Effets avec Bouton

## 🎮 Vue d'ensemble

Ce programme permet de sélectionner et d'afficher différents effets visuels sur une matrice LED NeoPixel 8x8 en appuyant sur un bouton. Chaque appui affiche le numéro de l'effet avec un défilement, puis lance l'effet correspondant.

## 🔌 Branchements

```
Raspberry Pi Pico  →  Composants
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GP0 (Pin 1)        →  NeoPixel DIN
GP1 (Pin 2)        →  Bouton (un côté)
GND                →  Bouton (autre côté)
3.3V / VBUS        →  NeoPixel VCC*
GND                →  NeoPixel GND

* Utilisez VBUS (5V) pour l'alimentation des LEDs si possible
  ou une alimentation externe 5V pour plus de 8 LEDs
```

### Schéma du bouton
```
         GP1 ────┬──── Bouton ──── GND
                 │
            Pull-up interne
                 │
                3.3V
```

Le bouton utilise la résistance pull-up interne du Pico, donc pas besoin de résistance externe.

## ✨ Fonctionnalités

### 9 Effets disponibles

1. **Dégradé animé** - Dégradé de couleurs qui change progressivement
2. **Arc-en-ciel rotatif** - Arc-en-ciel qui tourne sur la matrice
3. **Vague** - Effet de vague sinusoïdale
4. **Spirale** - Spirale colorée qui tourne
5. **Feu** - Simulation de flammes réaliste
6. **Pluie** - Gouttes de pluie qui tombent
7. **Cœur battant** - Cœur rouge qui pulse
8. **Damier clignotant** - Damier avec changement de couleurs
9. **Étoiles scintillantes** - Étoiles qui apparaissent et disparaissent

### Affichage des numéros

Chaque effet est associé à un numéro (1-9) qui :
- **Défile** de droite à gauche sur la matrice
- S'affiche en **couleur arc-en-ciel** unique
- Reste visible pendant **1.5 secondes**
- Puis l'effet démarre automatiquement

## 🚀 Utilisation

### Installation

1. **Copier les fichiers** sur votre Raspberry Pi Pico :
   - `neopixel_matrix_optimized.py`
   - `main_with_button.py`

2. **Renommer** `main_with_button.py` en `code.py` pour qu'il démarre automatiquement

3. **Brancher** les composants selon le schéma ci-dessus

4. **Redémarrer** le Pico

### Utilisation

1. Le programme démarre avec l'**Effet 1** (Dégradé animé)
2. **Appuyez sur le bouton** pour passer à l'effet suivant
3. Le **numéro de l'effet** défile sur la matrice
4. L'effet démarre automatiquement
5. Après l'effet 9, retour à l'effet 1

## 🔧 Configuration

### Réglages dans le code

```python
# En haut du fichier main_with_button.py

LED_PIN = board.GP0              # Pin des LEDs NeoPixel
BUTTON_PIN = board.GP1           # Pin du bouton
BRIGHTNESS = 0.3                 # Luminosité (0.0 à 1.0)
EFFECT_DISPLAY_TIME = 1.5        # Temps d'affichage du numéro (secondes)
```

### Anti-rebond du bouton

Le programme inclut un système anti-rebond de **200 ms** pour éviter les appuis multiples non désirés.

```python
self.debounce_time = 0.2  # Dans la classe Button
```

## 📝 Structure du code

### Classes principales

#### `Button`
Gère le bouton avec anti-rebond.

**Méthodes :**
- `is_pressed()` - Détecte un appui avec anti-rebond

#### `Effect`
Classe de base pour tous les effets.

**Méthodes :**
- `run()` - Exécute l'effet (à surcharger)
- `stop()` - Arrête l'effet proprement

#### `EffectManager`
Gère la sélection et l'exécution des effets.

**Méthodes :**
- `next_effect()` - Passe à l'effet suivant
- `run_current_effect()` - Exécute l'effet actuel
- `check_button()` - Vérifie les appuis bouton

### Chiffres 8x8

Les chiffres 0-9 sont définis en ASCII art dans le dictionnaire `DIGITS` :

```python
DIGITS = {
    0: [
        "  ████  ",
        " ██  ██ ",
        "██    ██",
        # ...
    ],
    # ...
}
```

## 🎨 Ajouter un nouvel effet

### Étape 1 : Créer la classe d'effet

```python
class Effect10_MonNouvelEffet(Effect):
    """Effet 10 : Description de l'effet"""
    
    def run(self):
        while self.running:
            # Votre code d'animation ici
            self.matrix.fill((255, 0, 0))
            self.matrix.show()
            time.sleep(0.1)
```

### Étape 2 : Ajouter à la liste des effets

```python
# Dans la classe EffectManager
self.effects = [
    Effect1_Gradient,
    Effect2_Rainbow,
    # ... autres effets ...
    Effect10_MonNouvelEffet  # Ajouter ici
]
```

### Conseils pour créer des effets

1. **Toujours vérifier `self.running`** dans la boucle
2. **Utiliser `time.sleep()`** pour contrôler la vitesse
3. **Appeler `self.matrix.show()`** pour afficher les changements
4. **Tester l'arrêt** avec le bouton pour s'assurer que l'effet s'arrête proprement

## 🐛 Dépannage

### Le bouton ne répond pas

**Problème :** Appuis non détectés

**Solutions :**
1. Vérifier les connexions (GP1 et GND)
2. Tester le bouton avec un multimètre
3. Augmenter le temps d'anti-rebond :
   ```python
   self.debounce_time = 0.5  # 500ms
   ```
4. Vérifier que le bouton n'est pas inversé (normalement ouvert vs fermé)

---

### Le bouton déclenche plusieurs fois

**Problème :** Un appui change plusieurs effets

**Solutions :**
1. Augmenter le temps d'anti-rebond
2. Vérifier les connexions (faux contacts)
3. Ajouter un condensateur (10-100nF) entre le bouton et la masse

---

### Les numéros ne s'affichent pas correctement

**Problème :** Chiffres mal formés ou absents

**Solutions :**
1. Vérifier que `EFFECT_DISPLAY_TIME` n'est pas trop court
2. S'assurer que la luminosité n'est pas à 0
3. Vérifier l'orientation de la matrice

---

### Un effet ne démarre pas

**Problème :** Écran noir après sélection d'un effet

**Solutions :**
1. Vérifier les erreurs dans la console série
2. S'assurer que `self.running = True` dans la classe Effect
3. Vérifier que la boucle `while self.running:` existe

---

### Le programme plante

**Problème :** Le Pico redémarre ou freeze

**Solutions :**
1. Réduire la luminosité : `BRIGHTNESS = 0.2`
2. Vérifier l'alimentation (voltage stable)
3. Ajouter des try/except dans les effets :
   ```python
   try:
       # Code de l'effet
   except Exception as e:
       print(f"Erreur : {e}")
   ```

---

### Mémoire insuffisante

**Problème :** MemoryError lors de l'exécution

**Solutions :**
1. Réduire le nombre d'effets actifs
2. Supprimer les imports inutilisés
3. Simplifier les effets complexes (moins de variables)
4. Utiliser `gc.collect()` entre les effets :
   ```python
   import gc
   gc.collect()  # Libérer la mémoire
   ```

## 💡 Optimisations

### Réduire la consommation mémoire

```python
# Au lieu de stocker tout l'historique
drops = []  # Liste qui grandit

# Limiter la taille
MAX_DROPS = 10
if len(drops) > MAX_DROPS:
    drops = drops[-MAX_DROPS:]
```

### Améliorer la réactivité du bouton

```python
# Dans Effect.run(), vérifier le bouton régulièrement
def run(self):
    steps = 0
    while self.running:
        # Code de l'effet
        steps += 1
        
        # Vérifier l'arrêt tous les 10 steps
        if steps % 10 == 0:
            time.sleep(0.001)  # Laisser le temps au système
```

### Réduire la consommation électrique

```python
# Utiliser une luminosité plus faible
BRIGHTNESS = 0.2  # Au lieu de 0.3

# Ou adapter par effet
class Effect5_Fire(Effect):
    def __init__(self, matrix):
        super().__init__(matrix)
        self.matrix.pixels.brightness = 0.4  # Feu plus lumineux
```

## 🎓 Améliorations possibles

1. **Mode aléatoire** - Changer d'effet automatiquement
2. **Sauvegarde** - Mémoriser le dernier effet utilisé
3. **Vitesse variable** - Ajuster avec un potentiomètre
4. **Mode démo** - Cycler tous les effets automatiquement
5. **Double bouton** - Effet précédent / suivant
6. **Détection longue pression** - Menu de configuration
7. **Indicateur LED** - LED pour montrer quel effet est actif
8. **Mode veille** - Extinction automatique après inactivité

## 📊 Tableau des effets

| # | Nom | Couleurs | Vitesse | Complexité | Mémoire |
|---|-----|----------|---------|------------|---------|
| 1 | Dégradé | RGB variable | Moyenne | Faible | Faible |
| 2 | Arc-en-ciel | Toutes | Rapide | Moyenne | Faible |
| 3 | Vague | Bleu/Cyan | Moyenne | Moyenne | Faible |
| 4 | Spirale | Toutes | Rapide | Haute | Faible |
| 5 | Feu | Rouge/Jaune | Variable | Haute | Moyenne |
| 6 | Pluie | Bleu | Lente | Moyenne | Moyenne |
| 7 | Cœur | Rouge | Lente | Faible | Faible |
| 8 | Damier | Variable | Lente | Faible | Faible |
| 9 | Étoiles | Blanc | Variable | Moyenne | Moyenne |

## 🔗 Ressources complémentaires

- [Guide débutant CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython)
- [Référence digitalio](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html)
- [Tutoriel boutons](https://learn.adafruit.com/circuitpython-essentials/circuitpython-digital-in-out)

## 📄 Licence

Code fourni à titre éducatif. Libre modification et redistribution.

---

**Version :** 1.0  
**Date :** Janvier 2026  
**Compatibilité :** CircuitPython 7.0+
