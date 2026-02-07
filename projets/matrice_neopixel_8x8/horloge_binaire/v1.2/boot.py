"""
Fichier de démarrage pour Raspberry Pi Pico W
"""
import microcontroller
import time

# Désactiver le mode debug pour plus de performance
import usb_cdc
usb_cdc.enable(console=True, data=False)

# Attendre un peu pour permettre la connexion série
time.sleep(1)

print("=== Horloge BCD - Démarrage ===")
print(f"CPU: {microcontroller.cpu.frequency / 1000000} MHz")