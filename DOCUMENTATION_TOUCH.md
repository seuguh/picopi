# Documentation - Capteur Tactile Capacitif

## 🎯 Vue d'ensemble

Cette version utilise un **module tactile capacitif** (touch sensor) au lieu d'un bouton mécanique. Le capteur détecte la proximité ou le contact d'un doigt grâce à la variation de capacitance.

## 🔌 Types de capteurs tactiles compatibles

### 1. Module TTP223
```
Module TTP223
┌─────────────┐
│    ( )      │ ← Zone tactile
│             │
│ VCC  SIG  GND
│  │    │    │
└──┼────┼────┼─┘
   │    │    │
```
**Branchement :**
- VCC → 3.3V (Pico)
- SIG → GP1
- GND → GND

### 2. Capteur tactile intégré (touchio)
Le Raspberry Pi Pico peut transformer **n'importe quel pin GPIO** en capteur tactile grâce à `touchio`. Il suffit de connecter un fil ou une surface conductrice au pin.

```
   GP1 ●───────┬──────  Zone tactile
                │       (fil, plaque cuivre, etc.)
               ╱│╲
              ╱ │ ╲     Votre doigt
                │       (capacité humaine)
               GND
```

### 3. Capteur capacitif AT42QT1010
```
Module AT42QT1010
┌─────────────┐
│   TOUCH     │
│             │
│ VCC OUT GND │
│  │   │   │  │
└──┼───┼───┼──┘
   │   │   │
```

## 🔧 Branchements

### Configuration 1 : Module TTP223 (recommandé pour débutants)

```
Raspberry Pi Pico      Module TTP223
────────────────       ─────────────

3.3V (Pin 36)  ●──────● VCC
GP1  (Pin 2)   ●──────● SIG (Signal)
GND  (Pin 3)   ●──────● GND
```

### Configuration 2 : Touchio natif (sans module externe)

```
Raspberry Pi Pico      Zone tactile
────────────────       ─────────────

GP1 (Pin 2)    ●──────● Fil/Plaque conductrice
                        (5-10 cm recommandé)

Note : Aucune connexion GND nécessaire !
```

**Exemple de zone tactile :**
- Fil de cuivre dénudé
- Plaque de cuivre autocollante
- Papier aluminium
- Objet métallique

### Configuration 3 : Module capacitif commercial

```
Raspberry Pi Pico      Module Capacitif
────────────────       ────────────────

3.3V (Pin 36)  ●──────● VCC
GP1  (Pin 2)   ●──────● OUT
GND  (Pin 3)   ●──────● GND
```

## ⚙️ Configuration du code

### Paramètres de base

```python
# En haut du fichier main_with_touch.py

TOUCH_PIN = board.GP1           # Pin du capteur tactile
TOUCH_THRESHOLD = 500           # Seuil de détection (à ajuster)
BRIGHTNESS = 0.3                # Luminosité des LEDs
EFFECT_DISPLAY_TIME = 1.5       # Temps d'affichage du numéro
```

### Ajuster le seuil de détection

Le seuil (`threshold`) détermine la sensibilité du capteur :

**Valeur trop BASSE** → Déclenchements intempestifs (sans toucher)
**Valeur trop HAUTE** → Capteur ne réagit pas au toucher

```python
# Valeurs typiques selon le type de capteur :

# Module TTP223 (signal digital)
TOUCH_THRESHOLD = 0  # Non utilisé, signal ON/OFF

# Touchio natif avec fil court (< 5cm)
TOUCH_THRESHOLD = 300-500

# Touchio natif avec fil long (5-15cm)
TOUCH_THRESHOLD = 800-1500

# Surface métallique large
TOUCH_THRESHOLD = 1000-2000
```

## 🔍 Calibration automatique

Le code inclut une fonction de calibration pour trouver le seuil optimal :

```python
# Dans main_with_touch.py, décommenter ces lignes :

print("\nCalibration du capteur tactile...")
touch_sensor.calibrate()
time.sleep(2)
```

### Processus de calibration

1. **Démarrer le programme** avec la calibration activée
2. **Ne touchez PAS** le capteur quand demandé → mesure valeur de base
3. **Touchez le capteur** quand demandé → mesure valeur contact
4. Le seuil optimal est calculé et appliqué automatiquement

**Sortie console exemple :**
```
=== Calibration du capteur tactile ===
Ne touchez PAS le capteur...
Valeur de base (sans contact): 450

Maintenez votre doigt sur le capteur...
Valeur avec contact: 1200

Seuil recommandé: 825
Seuil actuel: 500

Nouveau seuil appliqué: 825
========================================
```

## 📝 Différences avec le bouton mécanique

| Aspect | Bouton mécanique | Capteur tactile |
|--------|------------------|-----------------|
| Module Python | `digitalio` | `touchio` |
| Résistance pull-up | Requise | Non nécessaire |
| Détection | Contact physique | Proximité capacitive |
| Rebonds | Fréquents | Rares |
| Durée de vie | ~100k appuis | Illimitée (pas d'usure) |
| Câblage | 2 fils (pin + GND) | 1 fil (pin uniquement) avec touchio |
| Sensibilité | Fixe | Ajustable (threshold) |

## 🐛 Dépannage

### Le capteur ne réagit pas

**Symptôme :** Aucune détection au toucher

**Solutions :**

1. **Vérifier les connexions** (VCC, SIG, GND pour modules externes)

2. **Lancer la calibration** pour trouver le bon seuil
   ```python
   touch_sensor.calibrate()
   ```

3. **Diminuer le seuil** manuellement
   ```python
   TOUCH_THRESHOLD = 300  # Au lieu de 500
   ```

4. **Vérifier le bon module**
   - Pour module TTP223 : utiliser `digitalio` à la place
   - Pour touchio natif : s'assurer que le fil est suffisamment long

5. **Tester la valeur brute**
   ```python
   import board
   import touchio
   
   touch = touchio.TouchIn(board.GP1)
   while True:
       print(touch.raw_value)
       time.sleep(0.1)
   ```

---

### Déclenchements intempestifs

**Symptôme :** Effets changent sans toucher le capteur

**Solutions :**

1. **Augmenter le seuil**
   ```python
   TOUCH_THRESHOLD = 1000  # Au lieu de 500
   ```

2. **Augmenter le temps anti-rebond**
   ```python
   self.debounce_time = 0.5  # Au lieu de 0.3
   ```

3. **Éloigner le fil tactile des sources électromagnétiques**
   - LEDs NeoPixel
   - Alimentation
   - Autres câbles

4. **Raccourcir le fil tactile** (< 10 cm recommandé)

5. **Ajouter un condensateur de filtrage** (10-100nF entre pin et GND)

---

### Module TTP223 ne fonctionne pas avec touchio

**Symptôme :** Le module TTP223 fonctionne mal avec `touchio`

**Solution :** Utiliser `digitalio` à la place pour les modules TTP223

```python
import digitalio

# Remplacer la classe TouchSensor par :
class TouchSensor:
    def __init__(self, pin, threshold=None):
        self.touch = digitalio.DigitalInOut(pin)
        self.touch.direction = digitalio.Direction.INPUT
        self.last_touch_time = 0
        self.debounce_time = 0.3
        self.was_touched = False
    
    def is_touched(self):
        current_time = time.monotonic()
        is_currently_touched = self.touch.value  # True/False
        
        if (is_currently_touched and not self.was_touched and 
            (current_time - self.last_touch_time) > self.debounce_time):
            self.last_touch_time = current_time
            self.was_touched = True
            return True
        
        if not is_currently_touched:
            self.was_touched = False
        
        return False
```

---

### Sensibilité fluctuante

**Symptôme :** Parfois très sensible, parfois pas du tout

**Solutions :**

1. **Stabiliser l'alimentation** (condensateur 100µF sur 3.3V)

2. **Recalibrer régulièrement**
   ```python
   # Recalibration toutes les 5 minutes
   last_calibration = time.monotonic()
   
   while True:
       if time.monotonic() - last_calibration > 300:
           touch_sensor.calibrate()
           last_calibration = time.monotonic()
   ```

3. **Vérifier l'humidité** (l'humidité affecte la capacitance)

4. **Nettoyer la surface tactile** (saleté, graisse)

---

### Le capteur reste "collé" (toujours actif)

**Symptôme :** Le capteur semble rester touché en permanence

**Solutions :**

1. **Vérifier le câblage** (court-circuit possible)

2. **Redémarrer le Pico** (reset de l'état du capteur)

3. **Augmenter drastiquement le seuil**
   ```python
   TOUCH_THRESHOLD = 2000
   ```

4. **Isoler électriquement** la zone tactile (ruban isolant sur le dos)

## 💡 Optimisations

### Améliorer la fiabilité

```python
class TouchSensor:
    def __init__(self, pin, threshold=500):
        self.touch = touchio.TouchIn(pin)
        self.touch.threshold = threshold
        self.last_touch_time = 0
        self.debounce_time = 0.3
        self.was_touched = False
        
        # Historique pour filtrage
        self.history = []
        self.history_size = 5
    
    def is_touched(self):
        current_time = time.monotonic()
        is_currently_touched = self.touch.value
        
        # Filtrage par moyenne mobile
        self.history.append(is_currently_touched)
        if len(self.history) > self.history_size:
            self.history.pop(0)
        
        # Considérer comme touché si majoritaire
        touch_count = sum(self.history)
        is_filtered_touched = touch_count > self.history_size // 2
        
        if (is_filtered_touched and not self.was_touched and 
            (current_time - self.last_touch_time) > self.debounce_time):
            self.last_touch_time = current_time
            self.was_touched = True
            return True
        
        if not is_filtered_touched:
            self.was_touched = False
        
        return False
```

### Feedback visuel du toucher

```python
def next_effect(self):
    # Flash blanc au toucher pour feedback
    self.matrix.fill((255, 255, 255))
    self.matrix.show()
    time.sleep(0.1)
    
    # Puis continuer normalement
    self.current_effect_index = (self.current_effect_index + 1) % len(self.effects)
    # ...
```

### Mode veille économie d'énergie

```python
# Éteindre les LEDs après 5 minutes sans toucher
SLEEP_TIMEOUT = 300  # secondes

last_activity = time.monotonic()

while True:
    if manager.check_touch():
        last_activity = time.monotonic()
        manager.next_effect()
    
    # Mode veille
    if time.monotonic() - last_activity > SLEEP_TIMEOUT:
        matrix.clear()
        time.sleep(0.5)  # Économie d'énergie
        continue
    
    manager.run_current_effect()
```

## 🎨 Créer votre propre zone tactile

### Matériaux recommandés

1. **Papier aluminium** (facile, pas cher)
   - Coller sur du carton
   - Connecter avec fil et scotch conducteur

2. **Feuille de cuivre adhésive**
   - Plus durable
   - Forme personnalisée possible

3. **Peinture conductrice**
   - Dessiner des formes
   - Permet des designs créatifs

4. **Capsules métalliques** (type bouteille)
   - Aspect rétro
   - Robuste

### Exemple : Pad tactile en aluminium

```
Matériel nécessaire :
- Papier aluminium (10x10 cm)
- Carton rigide (10x10 cm)
- Fil de cuivre (20 cm)
- Scotch double face
- Scotch isolant

Instructions :
1. Coller le papier aluminium sur le carton
2. Fixer le fil sur l'aluminium (scotch conducteur ou soudure)
3. Protéger avec film transparent (optionnel)
4. Connecter l'autre bout du fil à GP1
5. Calibrer le capteur
```

### Schéma

```
┌─────────────────────────┐
│  Film transparent       │  (protection)
├─────────────────────────┤
│  Papier aluminium       │  (surface tactile)
├─────────────────────────┤
│  Carton rigide          │  (support)
└──────────┬──────────────┘
           │ Fil de cuivre
           │
           ● GP1 (Pico)
```

## 📚 Ressources

### Documentation officielle
- [touchio CircuitPython](https://docs.circuitpython.org/en/latest/shared-bindings/touchio/)
- [Guide capteurs tactiles Adafruit](https://learn.adafruit.com/touch-deck-diy-trellis-neokey)

### Tutoriels
- [Créer des pads tactiles DIY](https://learn.adafruit.com/make-it-sense)
- [Capteurs capacitifs Arduino](https://playground.arduino.cc/Main/CapacitiveSensor/)

## ✅ Checklist de validation

Avant utilisation :

- [ ] Capteur correctement branché (VCC, SIG/OUT, GND)
- [ ] Calibration effectuée
- [ ] Seuil de détection ajusté
- [ ] Anti-rebond configuré (0.3s minimum)
- [ ] Test de détection fonctionnel
- [ ] Pas de déclenchements intempestifs
- [ ] Feedback visuel au toucher (optionnel)

---

**Date :** Janvier 2026  
**Version :** 1.0  
**Compatibilité :** CircuitPython 7.0+ avec module `touchio`
