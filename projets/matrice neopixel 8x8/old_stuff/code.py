import board
import neopixel
import digitalio
import time

# Configuration de la matrice NeoPixel
pixels = neopixel.NeoPixel(board.GP0, 64, brightness=0.2, auto_write=False)

# Configuration du bouton
bouton = digitalio.DigitalInOut(board.GP1)
bouton.direction = digitalio.Direction.INPUT
bouton.pull = digitalio.Pull.UP

# Définition des chiffres 0-9 (format 8x8)
chiffres = [
    # 0
    [0x3C, 0x66, 0xC3, 0xC3, 0xC3, 0xC3, 0x66, 0x3C],
    # 1
    [0x18, 0x38, 0x78, 0x18, 0x18, 0x18, 0x18, 0x7E],
    # 2
    [0x3C, 0x66, 0x06, 0x0C, 0x30, 0x60, 0xC0, 0xFE],
    # 3
    [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x06, 0x66, 0x3C],
    # 4
    [0x06, 0x0E, 0x1E, 0x36, 0x66, 0xFF, 0x06, 0x06],
    # 5
    [0xFE, 0xC0, 0xFC, 0x06, 0x06, 0x06, 0xC6, 0x7C],
    # 6
    [0x3C, 0x66, 0xC0, 0xFC, 0xC6, 0xC6, 0x66, 0x3C],
    # 7
    [0xFE, 0x06, 0x0C, 0x18, 0x30, 0x60, 0xC0, 0xC0],
    # 8
    [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x66, 0x3C],
    # 9
    [0x3C, 0x66, 0xC6, 0xC6, 0x7E, 0x06, 0x66, 0x3C]
]

couleur = (0, 255, 0)  # Vert
numero_actuel = 0
transition_active = False
etat_precedent = bouton.value
duree_transition = 1.0  # 1 seconde

def afficher_chiffre(n):
    print(f"Affichage du chiffre {n}")  # Debug
    pixels.fill((0, 0, 0))
    for ligne in range(8):
        valeur_ligne = chiffres[n][ligne]
        for colonne in range(8):
            if valeur_ligne & (0x80 >> colonne):
                pixels[ligne * 8 + colonne] = couleur
    pixels.show()

def transition_verticale(debut, fin):
    print(f"Transition de {debut} à {fin}")  # Debug
    etapes = 20  # Nombre d'étapes pour la transition
    for i in range(etapes + 1):
        pixels.fill(0)
        progression = i / etapes
        
        # Calcul du décalage vertical avec 2 lignes vides
        decalage = int(progression * 10)  # 8 lignes + 2 lignes vides
        
        # Dessin des deux chiffres décalés verticalement
        for ligne in range(8):
            for colonne in range(8):
                # Chiffre sortant (en haut)
                ligne_debut = ligne + decalage
                if 0 <= ligne_debut < 8:
                    if chiffres[debut][ligne_debut] & (0x80 >> colonne):
                        pixels[ligne * 8 + colonne] = couleur
                
                # Chiffre entrant (en bas, avec 2 lignes vides)
                ligne_fin = ligne - (10 - decalage)  # 8 lignes + 2 lignes vides
                if 0 <= ligne_fin < 8:
                    if chiffres[fin][ligne_fin] & (0x80 >> colonne):
                        pixels[ligne * 8 + colonne] = couleur
        
        pixels.show()
        time.sleep(duree_transition / etapes)

# Initialisation
afficher_chiffre(numero_actuel)

# Boucle principale
while True:
    etat_actuel = bouton.value
    if etat_precedent and not etat_actuel and not transition_active:
        print("Bouton pressé !")  # Debug
        transition_active = True
        ancien_numero = numero_actuel
        numero_actuel = (numero_actuel + 1) % 10
        transition_verticale(ancien_numero, numero_actuel)
        transition_active = False
    
    etat_precedent = etat_actuel
    time.sleep(0.01)