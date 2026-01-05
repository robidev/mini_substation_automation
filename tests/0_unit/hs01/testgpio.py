import RPi.GPIO as GPIO

# List of GPIO pins
gpio_pins = [27, 18, 5, 6, 12, 13, 16, 19, 20, 21, 24, 22, 23, 25]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in gpio_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initialize as OFF

def toggle_pin_by_index(index):
    pin = gpio_pins[index]
    GPIO.output(pin, not GPIO.input(pin))
    state_str = "ON" if GPIO.input(pin) else "OFF"
    print(f"GPIO {pin} is now {state_str}")

try:
    while True:
        # Show indexed list
        print("\nGPIO pins:")
        for i, pin in enumerate(gpio_pins):
            print(f"{i}: GPIO {pin}")
        
        choice = input("Enter index to toggle (or 'q' to quit): ")
        if choice.lower() == 'q':
            break
        
        try:
            idx = int(choice)
            if 0 <= idx < len(gpio_pins):
                toggle_pin_by_index(idx)
            else:
                print("Invalid index. Choose from the list.")
        except ValueError:
            print("Please enter a valid number.")

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    GPIO.cleanup()

