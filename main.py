import pygame
import RPi.GPIO as GPIO
import time
import threading

# GPIO setup
RELAIS_PIN = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAIS_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Set relay pin as output, default to HIGH (relay off for active-low)
GPIO.setwarnings(False)

pygame.init()
pygame.joystick.init()

# Global state variables for firing and reloading
is_firing = False
is_reloading = False

# Lock to synchronize access to firing and reloading state
lock = threading.Lock()

def fire():
    global is_firing, is_reloading
    with lock:
        if is_firing or is_reloading:
            # If already firing or reloading, print an error and ignore the fire request
            print("Error: Cannot fire. System is currently busy (firing or reloading).")
            return
        is_firing = True

    # Fire sequence
    GPIO.output(RELAIS_PIN, GPIO.LOW)  # Active-low: Set LOW to turn relay on
    print("Relay ON (GPIO LOW)")
    time.sleep(0.5)  # Hold relay on for 0.5 seconds
    GPIO.output(RELAIS_PIN, GPIO.HIGH)  # Set HIGH to turn relay off
    print("Relay OFF (GPIO HIGH)")

    # Reset firing state and start reload in a new thread
    with lock:
        is_firing = False
    reload_thread = threading.Thread(target=reload)
    reload_thread.start()

def reload():
    global is_reloading
    with lock:
        if is_reloading:
            return
        is_reloading = True

    print("Reloading...")
    time.sleep(20)  # Reload time delay
    print("Reload complete")

    # Reset reloading state
    with lock:
        is_reloading = False

# Check if a joystick was found
if pygame.joystick.get_count() == 0:
    print("No joystick found!")
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Joystick Name: {joystick.get_name()}")
    print(f"Number of Axes: {joystick.get_numaxes()}")
    print(f"Number of Buttons: {joystick.get_numbuttons()}")

    try:
        while True:
            # Process all pygame events to update joystick state
            pygame.event.get()

            # Button states
            button_pressed = joystick.get_button(5)  # Change button index if needed
            if button_pressed:
                # Start the fire function in a new thread if button pressed
                fire_thread = threading.Thread(target=fire)
                fire_thread.start()

            # Small delay to avoid flooding output
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        # Proper cleanup for GPIO and pygame
        GPIO.cleanup()
        pygame.quit()
