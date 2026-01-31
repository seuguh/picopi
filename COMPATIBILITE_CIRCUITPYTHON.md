# Guide de compatibilité CircuitPython

## ⚠️ Problème résolu : ImportError typing

### Symptôme
```
ImportError: no module named 'typing'
```

### Cause
Le module `typing` (pour les type hints) n'est **pas disponible** dans CircuitPython. Il est uniquement disponible dans Python standard (CPython).

### Solution appliquée
Tous les type hints ont été **retirés** du code pour assurer la compatibilité avec CircuitPython :

**Avant (ne fonctionne pas sur CircuitPython) :**
```python
from typing import Tuple, Callable

def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
    pass
```

**Après (compatible CircuitPython) :**
```python
def set_pixel(self, x, y, color):
    pass
```

## 📋 Différences CircuitPython vs Python

### Modules NON disponibles dans CircuitPython

❌ **Ne fonctionnent PAS :**
- `typing` - Type hints
- `asyncio` - Programmation asynchrone
- `threading` - Multithreading
- `multiprocessing` - Multiprocessing
- `socket` - Sockets réseau (sauf sur certaines boards WiFi)
- `requests` - Requêtes HTTP (utilisez `adafruit_requests` à la place)
- `numpy` - Calculs numériques
- `pandas` - Manipulation de données
- `PIL/Pillow` - Traitement d'images

### Modules DISPONIBLES dans CircuitPython

✅ **Fonctionnent :**
- `board` - Accès aux pins GPIO
- `digitalio` - Entrées/sorties numériques
- `analogio` - Entrées analogiques
- `time` - Fonctions temporelles
- `math` - Fonctions mathématiques
- `random` - Nombres aléatoires
- `neopixel` - Contrôle des LEDs WS2812
- `busio` - Communication I2C, SPI, UART
- `storage` - Gestion du stockage

### Syntaxe Python supportée

✅ **Supporté :**
```python
# Classes
class MaClasse:
    def __init__(self):
        pass

# Compréhensions de liste
liste = [x * 2 for x in range(10)]

# Lambdas
func = lambda x: x * 2

# Try/except
try:
    # code
except Exception as e:
    print(e)

# With context managers
with open("file.txt") as f:
    data = f.read()
```

❌ **NON supporté :**
```python
# Type hints
def fonction(x: int) -> str:
    pass

# Async/await
async def ma_fonction():
    await autre_fonction()

# F-strings complexes (supportés de base mais attention aux limites)
# Threading
import threading
```

## 🔧 Optimisations pour CircuitPython

### 1. Gestion de la mémoire

CircuitPython a une **mémoire limitée**. Quelques astuces :

```python
# Libérer la mémoire régulièrement
import gc
gc.collect()

# Utiliser des générateurs au lieu de listes
# Mauvais (consomme beaucoup de mémoire)
pixels = [calculer(i) for i in range(1000)]

# Bon (économe en mémoire)
def generer_pixels():
    for i in range(1000):
        yield calculer(i)
```

### 2. Importations optimisées

```python
# Importer uniquement ce qui est nécessaire
from neopixel import NeoPixel  # Bon
import neopixel  # Moins bon (importe tout le module)

# Supprimer les imports inutilisés
# import typing  # ❌ Ne pas importer
```

### 3. Boucles et performances

```python
# Éviter les calculs répétés dans les boucles
# Mauvais
for i in range(100):
    x = math.sqrt(255)  # Calculé 100 fois

# Bon
sqrt_255 = math.sqrt(255)
for i in range(100):
    x = sqrt_255  # Calculé une seule fois
```

## 📦 Bibliothèques alternatives CircuitPython

| Python standard | CircuitPython | Notes |
|----------------|---------------|-------|
| `requests` | `adafruit_requests` | Requêtes HTTP |
| `datetime` | `adafruit_datetime` | Manipulation de dates |
| `logging` | `adafruit_logging` | Système de logs |
| `PIL` | Pas d'équivalent | Traitement d'images limité |
| `numpy` | `ulab` | Calculs numériques (limité) |

## 🐛 Débogage CircuitPython

### Console série

Pour voir les messages d'erreur :

1. **Windows** : PuTTY ou Tera Term sur le port COM
2. **macOS/Linux** : `screen /dev/ttyACM0 115200`
3. **Mu Editor** : Mode "Serial" intégré

### Messages d'erreur courants

#### MemoryError
```python
# Symptôme
MemoryError: memory allocation failed

# Solution
import gc
gc.collect()  # Libérer la mémoire
```

#### AttributeError
```python
# Symptôme
AttributeError: 'module' object has no attribute 'X'

# Solution : Vérifier la documentation CircuitPython
# Certaines fonctions Python standard n'existent pas
```

#### ImportError
```python
# Symptôme
ImportError: no module named 'X'

# Solutions :
# 1. Vérifier que le module existe dans CircuitPython
# 2. Installer la bibliothèque Adafruit si nécessaire
# 3. Copier le fichier .mpy dans /lib/
```

## 📚 Ressources

### Documentation officielle
- [CircuitPython.org](https://circuitpython.org/)
- [Bibliothèques Adafruit](https://circuitpython.org/libraries)
- [Guide de démarrage](https://learn.adafruit.com/welcome-to-circuitpython)

### Outils recommandés
- **Mu Editor** - IDE simple pour CircuitPython
- **Thonny** - IDE Python avec support CircuitPython
- **Visual Studio Code** avec extension CircuitPython

### Bundle de bibliothèques
Télécharger le bundle complet :
[CircuitPython Library Bundle](https://circuitpython.org/libraries)

## ✅ Checklist de compatibilité

Avant de copier du code Python vers CircuitPython :

- [ ] Retirer tous les imports de `typing`
- [ ] Retirer tous les type hints (`: int`, `-> str`, etc.)
- [ ] Vérifier que tous les modules importés existent dans CircuitPython
- [ ] Remplacer les modules non supportés par des équivalents
- [ ] Tester la consommation mémoire avec `gc.mem_free()`
- [ ] Vérifier les boucles infinies avec `time.sleep()`
- [ ] Ajouter `gc.collect()` dans les boucles longues

## 🔄 Migration Python → CircuitPython

### Exemple complet

**Code Python standard :**
```python
from typing import List, Tuple
import numpy as np

def traiter_donnees(valeurs: List[int]) -> Tuple[int, int]:
    arr = np.array(valeurs)
    return (int(arr.min()), int(arr.max()))

resultat = traiter_donnees([1, 2, 3, 4, 5])
print(f"Min: {resultat[0]}, Max: {resultat[1]}")
```

**Code CircuitPython compatible :**
```python
# Pas d'import typing, pas de numpy

def traiter_donnees(valeurs):
    return (min(valeurs), max(valeurs))

resultat = traiter_donnees([1, 2, 3, 4, 5])
print("Min: " + str(resultat[0]) + ", Max: " + str(resultat[1]))
```

## 📊 Limites matérielles

### Raspberry Pi Pico

- **RAM** : ~264 KB (dont ~200 KB disponible)
- **Flash** : 2 MB
- **CPU** : 133 MHz (dual-core, mais CircuitPython utilise 1 core)
- **GPIO** : 26 pins

### Conséquences

- **Pas de gros fichiers** en mémoire
- **Pas de calculs lourds** (matrices, images HD)
- **Optimiser les boucles** et structures de données
- **Utiliser le stockage flash** pour les données permanentes

## 💡 Astuces finales

1. **Toujours tester** sur le matériel cible
2. **Commencer simple** puis ajouter des fonctionnalités
3. **Utiliser `print()`** pour déboguer
4. **Lire les exemples** Adafruit (très bien documentés)
5. **Rejoindre la communauté** (Discord Adafruit, forums)

---

**Date :** Janvier 2026  
**Version :** 1.0  
**Compatibilité :** CircuitPython 7.0+
