import board
import digitalio
import time

button = digitalio.DigitalInOut(board.GP1)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Test bouton - appuyez pour tester (Ctrl+C pour quitter)")
print("Valeur affichee: 1=bouton relache, 0=bouton appuye")

last_value = button.value
press_count = 0

try:
    while True:
        current_value = button.value
        
        if current_value != last_value:
            last_value = current_value
            if not current_value:  # Bouton appuyé (False)
                press_count += 1
                print(f"\nBouton appuye! (appui #{press_count})")
        
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print(f"\nTotal appuis: {press_count}")