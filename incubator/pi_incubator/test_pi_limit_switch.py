from gpiozero import Button

# Configure the limit switchs. 
# "pull_up=True" uses the internal Pi resistor to keep the pin HIGH until grounded.
limit_switch_S1 = Button(7, pull_up=True)

def switch_triggered():
    print("Limit switch hit! Halting movement.")

def switch_cleared():
    print("Limit switch released. Path clear.")

# Assign event callbacks for changes in state
limit_switch_S1.when_pressed = switch_cleared     # Circuit closes (released if NC)
limit_switch_S1.when_released = switch_triggered   # Circuit opens (pressed/broken if NC)

time.sleep(10000)
