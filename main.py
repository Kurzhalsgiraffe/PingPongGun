import pygame
import time
import threading
from stepper import Stepper
from cannon import Cannon

pygame.init()
pygame.joystick.init()

cannon = Cannon(relay_pin=8)
stepper = Stepper(stepPin=15, directionPin=11, enablePin=16, relayPin=10)

if __name__ == "__main__":
    if pygame.joystick.get_count() == 0:
        print("No joystick found!")
        exit(1)

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
                fire_thread = threading.Thread(target=cannon.fire)
                fire_thread.start()

            # Small delay to avoid flooding output
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        # Proper cleanup for GPIO and pygame
        pygame.quit()
