# ~ from gpiozero import Button
# ~ from signal import pause

# ~ class ButtonController:
    # ~ def __init__(self, pin_number):
        # ~ # 1. Initialize the button
        # ~ self.button = Button(pin_number)
        
        # ~ # 2. Bind events to class methods using 'self'
        # ~ self.button.when_pressed = self.on_button_pressed
        # ~ self.button.when_released = self.on_button_released
        # ~ self.button.when_held = self.on_button_held
        
        # ~ # Optional: Configure custom hold time (defaults to 1 second)
        # ~ self.button.hold_time = 2.0 
        
        # ~ # Track state if needed
        # ~ self.press_count = 0

    # ~ def on_button_pressed(self):
        # ~ self.press_count += 1
        # ~ print(f"Button pressed! Total count: {self.press_count}")

    # ~ def on_button_released(self):
        # ~ print("Button released!")

    # ~ def on_button_held(self):
        # ~ print("Button held down for 2 seconds!")

# ~ if True:
    # ~ # Create an instance targeting BCM Pin 7
    # ~ controller = ButtonController(pin_number=7)
    
    # ~ print("Application is running. Press the button to trigger events.")
    # ~ # Keep the background listener thread alive
    # ~ pause()



from gpiozero import Button
from signal import pause


class switch: #0 is open, 1 is closed
	def __init__(self , gpio):
		
		self.s = Button(gpio)
		self.s.when_pressed = self.switch_closed()
		self.s.when_released = self.switch_opened()
		self.switch_val = 0
	def switch_closed(self):
		self.switch_val = 1
		print("switch closed")
	def switch_opened(self):
		self.switch_val = 0
		print("switch opened")

	
s1 = switch(7)



print("Waiting for switch events...")
pause() # Keeps the script running efficiently in the background


##super simple test

# ~ from gpiozero import Button
# ~ button = Button(7)


# ~ button.wait_for_press()
# ~ print('You pushed me')

