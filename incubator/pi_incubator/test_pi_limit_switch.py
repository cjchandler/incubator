from gpiozero import Button
from signal import pause


class switch: #0 is open, 1 is closed
	def __init__(self , gpio):
		self.switch_val = 0
		self.s = Button(gpio)
		s.when_pressed = self.switch_closed()
		s.when_released = self.switch_opened()
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

