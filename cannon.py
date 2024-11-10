import threading
import time
import RPi.GPIO as GPIO #type:ignore

class Cannon:
    def __init__(self, relay_pin):
        self.relay_pin = relay_pin
        self.is_firing = False
        self.is_reloading = False
        self.fire_time = 0.5
        self.reload_time = 20
        self.time_until_ready = self.reload_time
        self.lock = threading.Lock()

        self.last_print_time = 0  # To prevent spam printing

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.relay_pin, GPIO.OUT, initial=GPIO.HIGH)

    def fire(self):
        fire_thread = threading.Thread(target=self.fire_thread)
        fire_thread.start()

    def fire_thread(self):
        with self.lock:
            if self.is_firing:
                return
            if self.is_reloading:
                # Prevent spam print by checking the time
                current_time = time.time()
                if current_time - self.last_print_time >= 1:  # Only print once every second
                    print(f"System is currently reloading. ({self.time_until_ready} Seconds left)")
                    self.last_print_time = current_time
                return
            self.is_firing = True

        # Fire sequence
        print("Firing...")
        GPIO.output(self.relay_pin, GPIO.LOW)  # Active-low: Set LOW to turn relay on
        time.sleep(self.fire_time)
        GPIO.output(self.relay_pin, GPIO.HIGH)  # Set HIGH to turn relay off

        # Reset firing state and start reload in a new thread
        with self.lock:
            self.is_firing = False

            if self.is_reloading:
                return
            self.is_reloading = True

        print("Reloading...")
        for i in range(self.reload_time, 0, -1):
            self.time_until_ready = i
            time.sleep(1)
        self.time_until_ready = 0
        print("Reload complete")

        # Reset reloading state
        with self.lock:
            self.is_reloading = False

    def __del__(self):
        """Destructor to clean up GPIO when the object is deleted."""
        GPIO.cleanup()
        print("GPIO cleanup done.")
