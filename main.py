import pygame
import time
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

    last_movement_time = time.time()

    try:
        while True:
            # Process all pygame events to update joystick state
            pygame.event.get()

            rb_button_pressed = joystick.get_button(5)  # Change button index if needed
            if rb_button_pressed:
                cannon.fire()

            right_stick_vertical = round(joystick.get_axis(4), 3)

            # If joystick is moved, step the motor and activate the relay
            if abs(right_stick_vertical) > 0.5:
                # Activate relay before moving the motor
                stepper_relay_status = stepper.get_relay_status()
                if stepper_relay_status == "inactive":
                    stepper.activate_relay()

                if right_stick_vertical < -0.5:
                    stepper.step(10, "left")
                elif right_stick_vertical > 0.5:
                    stepper.step(10, "right")

                # Reset the last movement time
                last_movement_time = time.time()

            # Check for idle time (no movement for 1 second)
            if time.time() - last_movement_time > 1:
                # If no movement for 1 second, deactivate relay
                stepper_relay_status = stepper.get_relay_status()
                if stepper_relay_status == "active":
                    stepper.deactivate_relay()

            # Small delay to avoid flooding output
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        # Proper cleanup for GPIO and pygame
        pygame.quit()
        cannon.__del__()
        stepper.__del__()
