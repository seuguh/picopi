# Documentation - Minuteur BCD 8×8

## 📋 Vue d'ensemble

Minuteur visuel sur matrice LED NeoPixel 8×8 avec affichage binaire (BCD - Binary Coded Decimal) et contrôle tactile. Affiche le temps au format HH:MM:SS avec des transitions fluides adaptatives et des blocs lumineux de différentes tailles.

---

## 🛠️ Matériel requis

| Composant | Spécification | Connexion |
|-----------|---------------|-----------|
| **Microcontrôleur** | Raspberry Pi Pico RP2040 | - |
| **Firmware** | Adafruit CircuitPython 10.0.3 | - |
| **Matrice LED** | NeoPixel 8×8 (64 LEDs) | GP0 |
| **Capteur tactile** | Module touch capacitif | GP1 |
| **Bibliothèque** | `neopixel` (dernière version) | - |

### Configuration de la matrice

- **Organisation** : Colonnes (0-7), chaque colonne monte verticalement
- **Origine** : LED (0,0) = bas gauche
- **Maximum** : LED (7,7) = haut droite
- **Câblage** : Data In sur GP0

---

## 📊 Format d'affichage

### Layout de la matrice 8×8

```
┌────────────────────────────────────────┐
│  Col:  0-1    2    3-4    5    6-7     │
│       ┌───┐ ┌─┐  ┌───┐ ┌─┐  ┌───┐     │
│  7    │   │ │ │  │   │ │ │  │   │     │
│  6    │   │ │ │  │   │ │ │  │   │     │
│  5    │ H │ │D│  │ D │ │U│  │ U │     │
│  4    │ H │ │S│  │ M │ │S│  │ M │     │
│  3    │   │ │ │  │   │ │ │  │   │     │
│  2    │   │ │ │  │   │ │ │  │   │     │
│  1    │   │ │ │  │   │ │ │  │   │     │
│  0    └───┘ └─┘  └───┘ └─┘  └───┘     │
└────────────────────────────────────────┘
```

**Colonnes :**
- **0-1** : Heures (HH) - 0 à 9
- **2** : Dizaines de secondes (DS) - 0 à 5
- **3-4** : Dizaines de minutes (DM) - 0 à 5
- **5** : Unités de secondes (US) - 0 à 9
- **6-7** : Unités de minutes (UM) - 0 à 9

### Types de blocs

| Zone | Taille bloc | Description |
|------|-------------|-------------|
| Heures, Minutes | 2×2 LEDs | Blocs carrés épais |
| Secondes | 1×2 LEDs | Blocs verticaux fins |

---

## 🎨 Codage binaire (BCD)

Chaque chiffre (0-9) est codé sur **4 bits** affichés verticalement :

| Bit | Lignes Y | Poids |
|-----|----------|-------|
| 0 (LSB) | 0-1 | 2⁰ = 1 |
| 1 | 2-3 | 2¹ = 2 |
| 2 | 4-5 | 2² = 4 |
| 3 (MSB) | 6-7 | 2³ = 8 |

### Exemples de chiffres

```
Chiffre 0 = 0000    Chiffre 5 = 0101    Chiffre 9 = 1001
┌───┐               ┌───┐               ┌───┐
│   │ bit 3         │   │               │ █ │
│   │ bit 2         │ █ │               │   │
│   │ bit 1         │   │               │   │
│   │ bit 0         │ █ │               │ █ │
└───┘               └───┘               └───┘
```

### Exemple d'affichage complet

**Temps affiché : 2h 34m 56s**

| Élément | Valeur | Binaire | LEDs allumées |
|---------|--------|---------|---------------|
| Heures | 2 | 0010 | Lignes 2-3 |
| Dizaines min | 3 | 0011 | Lignes 0-1, 2-3 |
| Unités min | 4 | 0100 | Lignes 4-5 |
| Dizaines sec | 5 | 101 | Lignes 0-1, 4-5 |
| Unités sec | 6 | 0110 | Lignes 2-3, 4-5 |

---

## 🎨 Couleurs

### Palette par défaut (RGB 0-255)

```python
COULEUR_NORMALE_BASE = (0, 0, 100)    # Bleu - Mode normal
COULEUR_PAUSE_BASE = (100, 100, 0)    # Jaune - Mode pause
COULEUR_SECONDES = (0, 50, 50)        # Cyan - Colonnes secondes
```

### Effet d'explosion (fin du timer)

```python
COULEURS_EXPLOSION = [
    (50, 50, 0),   # Jaune
    (50, 0, 0),    # Rouge
    (0, 0, 50)     # Bleu
]
```

### Modification des couleurs

⚠️ **Important** : Tenir compte de la luminosité globale du NeoPixel (définie à 0.3 par défaut). Les valeurs RGB sont multipliées par ce facteur.

---

## 🎬 Transitions adaptatives

Le système ajuste automatiquement la durée des transitions selon l'importance du changement :

| Type de changement | Durée | Variable | Effet |
|-------------------|-------|----------|-------|
| **Seconde** | 0.15s | `DUREE_FADE_SECONDE` | Rapide et subtil |
| **Minute** | 0.3s | `DUREE_FADE_MINUTE` | Visible et fluide |
| **Heure** | 0.5s | `DUREE_FADE_HEURE` | Marqué et spectaculaire |
| **État** (pause/reset) | 0.4s | `DUREE_FADE_ETAT` | Transition d'interface |

### Fonctionnement

1. **Détection automatique** du type de changement
2. **Interpolation couleur** entre état actuel et nouveau
3. **Animation fluide** en 20ms par étape
4. **Buffer double** pour éviter le scintillement

---

## 🎮 États du minuteur

### Diagramme de transition

```
    ┌─────────┐  appui court   ┌───────────┐
    │ ARRET   │───────────────>│ EN_COURS  │
    │         │<───────────────│           │
    └─────────┘  appui long    └───────────┘
         ▲         (reset)            │
         │                        appui court
         │                            │
         │                            ▼
    ┌─────────┐  appui court   ┌───────────┐
    │TERMINE  │                │  PAUSE    │
    │         │                │           │
    └─────────┘                └───────────┘
```

### 1. État ARRET

**Description** : Timer réinitialisé, prêt à démarrer

**Affichage** : Temps configuré (bleu)

**Actions disponibles** :
- ⏯️ **Appui court** : Démarre le décompte
- 💡 **Appui long** : Éteint l'affichage (fade out)

### 2. État EN_COURS

**Description** : Décompte actif, temps décroît

**Affichage** : Temps restant (bleu) avec transitions

**Actions disponibles** :
- ⏸️ **Appui court** : Met en pause (transition bleu → jaune)

### 3. État PAUSE

**Description** : Décompte suspendu

**Affichage** : Temps gelé (jaune)

**Actions disponibles** :
- ▶️ **Appui court** : Reprend le décompte (transition jaune → bleu)
- 🔄 **Appui long** : Réinitialise à zéro (fade out → fade in)

### 4. État TERMINE

**Description** : Temps écoulé (0:00:00)

**Affichage** : Effet d'explosion automatique

**Actions disponibles** :
- 💤 **Appui long** : Éteint et réinitialise (fade out)

---

## 🎯 Contrôles tactiles

### Détection des appuis

```python
APPUI_LONG = 1.5  # Seuil en secondes
```

| Durée d'appui | Type | Détection |
|---------------|------|-----------|
| < 1.5 seconde | Court | Relâchement rapide |
| ≥ 1.5 seconde | Long | Maintien prolongé |

### Tableau récapitulatif

| État actuel | Appui court | Appui long |
|-------------|-------------|------------|
| **ARRET** | ▶️ Démarrer | 💡 Éteindre |
| **EN_COURS** | ⏸️ Pause | — |
| **PAUSE** | ▶️ Reprendre | 🔄 Reset |
| **TERMINE** | — | 💤 Éteindre + Reset |

---

## ⚙️ Configuration

### Variables modifiables

Au début du fichier `code.py` :

```python
# ===== CONFIGURATION =====
DUREE_TIMER = 90              # Durée en secondes (1-35940)
DUREE_EXPLOSION = 10          # Durée effet final en secondes
APPUI_LONG = 1.5              # Seuil appui court/long
DUREE_FADE_SECONDE = 0.15     # Transition seconde
DUREE_FADE_MINUTE = 0.3       # Transition minute
DUREE_FADE_HEURE = 0.5        # Transition heure
DUREE_FADE_ETAT = 0.4         # Transition état
```

### Limites et capacités

| Paramètre | Minimum | Maximum | Unité |
|-----------|---------|---------|-------|
| Durée timer | 1 | 35940 | secondes |
| Heures affichables | 0 | 9 | chiffre unique |
| Minutes affichables | 0 | 59 | — |
| Secondes affichables | 0 | 59 | — |
| Durée maximale | — | 9h 59m | — |

---

## 🎆 Effet d'explosion

Séquence automatique en 3 phases à la fin du timer :

### Phase 1 : Remplissage aléatoire (33%)

- Allumage progressif des 64 LEDs
- Ordre aléatoire (algorithme Fisher-Yates)
- Couleurs aléatoires (jaune/rouge/bleu)
- Durée : `DUREE_EXPLOSION / 3`

### Phase 2 : Clignotements (33%)

- Alternance allumé/éteint rapide
- Fréquence : ~5 Hz (0.2s par cycle)
- Nouvelles couleurs aléatoires à chaque cycle
- Nombre de clignotements adaptatif

### Phase 3 : Extinction progressive (33%)

- Diminution graduelle de la luminosité
- Facteur d'atténuation calculé : `0.95^(1/nb_etapes)`
- Étapes de 50ms
- Extinction complète finale

**Message console** : `Explosion terminée en X.Xs`

---

## 🔧 Optimisations techniques

### Anti-scintillement

**Problème** : Rafraîchissement trop fréquent cause des clignotements

**Solutions implémentées** :

1. **Buffer double** :
   ```python
   buffer_affichage_actuel = None  # Stocke l'état actuel
   nouveau_buffer = generer_affichage_bcd(...)  # Calcule le nouvel état
   ```

2. **Mise à jour différentielle** :
   - Comparaison pixel par pixel
   - Modification uniquement des pixels changés

3. **Rafraîchissement conditionnel** :
   ```python
   if temps_restant != dernier_affichage:
       afficher_bcd(...)
   ```

4. **Variable de suivi** :
   ```python
   dernier_affichage = -1  # Évite les doublons
   temps_precedent = None  # Pour détecter le type de changement
   ```

### Performances

| Paramètre | Valeur | Impact |
|-----------|--------|--------|
| Boucle principale | 50ms (20 Hz) | Réactivité bouton |
| Mise à jour décompte | 1000ms | Précision temps |
| Étape transition | 20ms | Fluidité animation |
| Détection bouton | ~10ms | Temps de réponse |

---

## 💬 Messages console

### Au démarrage

```
Minuteur BCD démarré - Format HH:MM:SS avec transitions adaptatives
Durée configurée: 90 secondes (0h 1m 30s)
Durée explosion: 10 secondes
Transitions: seconde=0.15s, minute=0.3s, heure=0.5s
Les secondes s'affichent sur les colonnes de séparation
Appui court: démarrer/pause/reprendre
Appui long (1.5s): reset ou extinction
```

### Pendant l'utilisation

| Événement | Message |
|-----------|---------|
| Démarrage | `Timer démarré` |
| Pause | `Pause - Temps restant: Xs` |
| Reprise | `Reprise du timer` |
| Reset | `Reset du timer` |
| Fin | `Timer terminé!` |
| Fin explosion | `Explosion terminée en X.Xs` |
| Extinction | `Extinction - Timer réinitialisé` |
| Éteindre | `Affichage éteint` |

---

## 📖 Exemples d'utilisation

### Exemple 1 : Timer de cuisine (10 minutes)

```python
DUREE_TIMER = 600  # 10 minutes = 600 secondes
```

**Affichage** : `0:10:00` → compte à rebours jusqu'à `0:00:00`

### Exemple 2 : Pomodoro (25 minutes)

```python
DUREE_TIMER = 1500  # 25 minutes
DUREE_EXPLOSION = 5  # Explosion rapide
```

### Exemple 3 : Méditation (1 heure)

```python
DUREE_TIMER = 3600  # 1 heure
DUREE_FADE_MINUTE = 0.5  # Transitions plus lentes
COULEUR_NORMALE_BASE = (0, 50, 0)  # Vert apaisant
```

### Exemple 4 : Marathon (2 heures)

```python
DUREE_TIMER = 7200  # 2 heures
COULEUR_NORMALE_BASE = (50, 0, 50)  # Violet
```

---

## 🐛 Dépannage

### Les LEDs scintillent

**Causes possibles** :
- Rafraîchissement trop fréquent
- Buffer non synchronisé

**Solutions** :
1. Vérifier que `dernier_affichage` est mis à jour
2. Augmenter `time.sleep(0.05)` si nécessaire
3. Désactiver temporairement les transitions : `avec_transition=False`

### Le bouton ne répond pas

**Diagnostic** :

1. Vérifier le câblage sur GP1
2. Tester avec le script de diagnostic :

```python
import board
import digitalio
import time

touch = digitalio.DigitalInOut(board.GP1)
touch.direction = digitalio.Direction.INPUT
touch.pull = digitalio.Pull.DOWN

while True:
    print("État:", "TOUCHÉ" if touch.value else "RELÂCHÉ")
    time.sleep(0.5)
```

3. Vérifier la configuration pull-down

### L'affichage est incorrect

**Causes possibles** :
- Matrice organisée différemment
- Index de coordonnées inversé

**Solution** :

Adapter la fonction `coords_to_index()` :

```python
def coords_to_index(x, y):
    # Pour matrice en lignes au lieu de colonnes :
    return y * 8 + x
```

### Transitions trop lentes/rapides

**Ajustement** :

```python
# Plus rapide
DUREE_FADE_SECONDE = 0.08
DUREE_FADE_MINUTE = 0.15

# Plus lent
DUREE_FADE_SECONDE = 0.25
DUREE_FADE_MINUTE = 0.5
```

### La durée maximale est dépassée

**Limite** : 35940 secondes (9h 59m 59s)

**Solution** : Pour des durées plus longues, modifier le format d'affichage pour inclure les dizaines d'heures.

---

## 🎨 Personnalisation avancée

### Modifier les couleurs

```python
# Thème "Coucher de soleil"
COULEUR_NORMALE_BASE = (80, 40, 0)  # Orange
COULEUR_PAUSE_BASE = (80, 0, 40)    # Magenta
COULEUR_SECONDES = (60, 30, 0)      # Orange foncé
```

### Créer un effet personnalisé

Remplacer `effet_explosion()` :

```python
def effet_personnalise():
    # Effet spirale
    for i in range(64):
        pixels[i] = (50, 0, 50)
        pixels.show()
        time.sleep(0.05)
    
    # Extinction
    for _ in range(20):
        for i in range(64):
            r, g, b = pixels[i]
            pixels[i] = (int(r*0.8), int(g*0.8), int(b*0.8))
        pixels.show()
        time.sleep(0.05)
```

### Ajouter un buzzer

```python
import pwmio

# Initialisation
buzzer = pwmio.PWMOut(board.GP2, frequency=440, duty_cycle=0)

# Dans ETAT_TERMINE, après effet_explosion()
buzzer.duty_cycle = 32768  # 50%
time.sleep(0.5)
buzzer.duty_cycle = 0
```

### Mode "compte à rebours avec avertissements"

```python
# Dans la boucle EN_COURS
if temps_restant == 60:  # 1 minute restante
    # Flasher en rouge
    for _ in range(3):
        pixels.fill((100, 0, 0))
        pixels.show()
        time.sleep(0.2)
        clear_matrix()
        time.sleep(0.2)
```

---

## 📚 Structure du code

### Organisation des fichiers

```
/
├── code.py                 # Programme principal
└── lib/
    └── neopixel.mpy        # Bibliothèque NeoPixel
```

### Fonctions principales

| Fonction | Rôle |
|----------|------|
| `coords_to_index(x, y)` | Convertit coordonnées → index LED |
| `generer_affichage_bcd()` | Crée buffer d'affichage |
| `transition_fade()` | Anime transition entre états |
| `detecter_type_changement()` | Identifie seconde/minute/heure |
| `afficher_bcd()` | Affiche le temps avec transition |
| `effet_explosion()` | Animation de fin |
| `detecter_appui()` | Gestion du bouton tactile |

### Flux d'exécution

```
1. Initialisation matériel
2. Affichage message démarrage
3. Boucle infinie:
   ├─> Détection appui bouton
   ├─> Gestion changement d'état
   ├─> Mise à jour décompte (si EN_COURS)
   ├─> Affichage avec transition adaptée
   └─> Délai 50ms
```

---

## 🔬 Algorithmes clés

### Interpolation de couleur

```python
def interpoler_couleur(couleur1, couleur2, facteur):
    # facteur ∈ [0.0, 1.0]
    # 0.0 → couleur1
    # 1.0 → couleur2
    r = r1 + (r2 - r1) × facteur
    g = g1 + (g2 - g1) × facteur
    b = b1 + (b2 - b1) × facteur
```

### Détection de changement

```python
if ancien_heures ≠ nouveau_heures:
    → DUREE_FADE_HEURE
elif ancien_minutes ≠ nouveau_minutes:
    → DUREE_FADE_MINUTE
else:
    → DUREE_FADE_SECONDE
```

### Shuffle Fisher-Yates (manuel)

```python
for i from n-1 to 1:
    j = random(0, i)
    swap(array[i], array[j])
```

---

## 📊 Consommation électrique

### Estimation

| État | Courant approximatif | Remarques |
|------|---------------------|-----------|
| Tout éteint | ~50mA | RP2040 seul |
| Affichage minimal | ~150mA | Quelques LEDs |
| Affichage complet | ~500mA | Toutes LEDs à 30% |
| Effet explosion | ~800mA | Pic temporaire |

⚠️ **Alimentation recommandée** : 5V / 1A minimum

---

## 🌐 Ressources supplémentaires

### Documentation officielle

- [CircuitPython sur RP2040](https://circuitpython.org/board/raspberry_pi_pico/)
- [Bibliothèque NeoPixel](https://docs.circuitpython.org/projects/neopixel/en/latest/)
- [Guide DigitalIO](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/)

### Communauté

- [Forum Adafruit](https://forums.adafruit.com/viewforum.php?f=60)
- [Discord CircuitPython](https://adafru.it/discord)

---

## 📝 Notes de version

### Version actuelle : 2.0

**Nouveautés** :
- ✨ Transitions adaptatives (seconde/minute/heure)
- 🎨 Système de buffer double
- 🚀 Optimisation anti-scintillement
- 📊 Affichage HH:MM:SS sur 8×8
- 🎆 Effet d'explosion paramétrable

**Corrections** :
- Scintillement lors des mises à jour
- Détection de changement de temps
- Gestion mémoire améliorée

---

## 📄 Licence

Ce projet est fourni "tel quel", libre d'utilisation et de modification pour un usage personnel et éducatif.

---

## ✍️ Auteur et contribution

**Développé pour** : Projet Raspberry Pi Pico + NeoPixel  
**Langage** : CircuitPython 10.0.3  
**Date** : Février 2026

**Contributions bienvenues** : N'hésitez pas à adapter ce code à vos besoins !

---

## 🎯 Conseils d'utilisation

### Pour débuter

1. Commencez avec `DUREE_TIMER = 60` (1 minute) pour tester
2. Utilisez les messages console pour comprendre le fonctionnement
3. Ajustez les couleurs selon votre matrice LED

### Pour optimiser

1. Réduisez `brightness` du NeoPixel si trop lumineux
2. Ajustez les durées de fade selon vos préférences
3. Désactivez les transitions pour économiser la batterie

### Pour personnaliser

1. Modifiez les couleurs dans la section configuration
2. Créez vos propres effets d'animation
3. Ajoutez des fonctionnalités (buzzer, WiFi, etc.)

---

**Bon timing avec votre minuteur BCD ! ⏱️✨**
