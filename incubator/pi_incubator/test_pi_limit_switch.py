from gpiozero import Button
from signal import pause

def switch_closed():
    print("Switch was turned ON!")

def switch_opened():
    print("Switch was turned OFF!")

switch = Button(7)

# Assign functions to state changes
switch.when_pressed = switch_closed
switch.when_released = switch_opened

print("Waiting for switch events...")
pause() # Keeps the script running efficiently in the background

