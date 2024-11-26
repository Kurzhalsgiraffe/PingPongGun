import atexit
import threading
import time
import RPi.GPIO as GPIO  # type: ignore

class Cannon:
    def __init__(self, fire_relay_pin, reload_relay_pin):
        self.fire_relay_pin = fire_relay_pin
        self.reload_relay_pin = reload_relay_pin
        self.is_firing = False
        self.is_reloading = False
        self.fire_time = 0.5
        self.reload_time = 15
        self.time_until_ready = self.reload_time
        self.lock = threading.Lock()

        self.last_print_time = 0  # To prevent spam printing

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.fire_relay_pin, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.reload_relay_pin, GPIO.OUT, initial=GPIO.HIGH)

        # Start reload in a separate thread to avoid blocking
        threading.Thread(target=self._reload_thread).start()
        atexit.register(self.cleanup)

    def fire(self):
        threading.Thread(target=self._fire_thread).start()

    def _fire_thread(self):
        with self.lock:
            if self.is_firing:
                return
            if self.is_reloading:
                current_time = time.time()
                if current_time - self.last_print_time >= 1:
                    print(f"System is currently reloading. ({self.time_until_ready} seconds left)")
                    self.last_print_time = current_time
                return
            self.is_firing = True

        # Fire sequence
        print("Firing...")
        GPIO.output(self.fire_relay_pin, GPIO.LOW)
        time.sleep(self.fire_time)
        GPIO.output(self.fire_relay_pin, GPIO.HIGH)

        with self.lock:
            self.is_firing = False

            if not self.is_reloading:
                self.is_reloading = True
                threading.Thread(target=self._reload_thread).start()

    def _reload_thread(self):
        with self.lock:
            if self.is_reloading:
                return
            self.is_reloading = True
            print("Reloading...")

        GPIO.output(self.reload_relay_pin, GPIO.LOW)
        for i in range(self.reload_time, 0, -1):
            with self.lock:
                self.time_until_ready = i
            time.sleep(1)

        GPIO.output(self.reload_relay_pin, GPIO.HIGH)
        print("Reload complete")
        with self.lock:
            self.is_reloading = False
            self.time_until_ready = 0

    def cleanup(self):
        GPIO.cleanup()
        print("GPIO cleanup done.")
