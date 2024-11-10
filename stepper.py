import time
import RPi.GPIO as GPIO

class Stepper:
	"""
	This is a custom Class to control the Stepper Motor of the W.A.F.F.E Project.
	The Setup requires a Relay to shut off the 12V Motor Power when it is not used.
	Default Pins are: stepPin=15, directionPin=11, enablePin=16, relayPin=10
	"""
	def __init__(self, stepPin, directionPin, enablePin, relayPin):
		self.stepPin = stepPin
		self.directionPin = directionPin
		self.enablePin = enablePin
		self.relayPin = relayPin

		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)

		GPIO.setup(self.relayPin, GPIO.OUT, initial=GPIO.HIGH)  # Set relay pin as output, default to HIGH (relay off for active-low)
		GPIO.setup(self.stepPin, GPIO.OUT)
		GPIO.setup(self.directionPin, GPIO.OUT)
		GPIO.setup(self.enablePin, GPIO.OUT)
		GPIO.output(self.enablePin, True)

		print(f"Stepper initialized (step={self.stepPin}, direction={self.directionPin}, enable={self.enablePin})")

	def cleanGPIO(self):
		GPIO.cleanup()

	def step(self, steps, dir, speed=1):
		stepCounter = 0
		waitTime = 0.01/speed

		GPIO.output(self.enablePin, False)
		GPIO.output(self.relayPin, GPIO.LOW)
		time.sleep(0.05)

		if (dir == 'right'):
			GPIO.output(self.directionPin, False)
		elif (dir == 'left'):
			GPIO.output(self.directionPin, True)
		else:
			print("STEPPER ERROR: no direction supplied")
			return False

		while stepCounter < steps:
			GPIO.output(self.stepPin, True)
			GPIO.output(self.stepPin, False)
			stepCounter += 1
			time.sleep(waitTime)

		GPIO.output(self.enablePin, True)
		GPIO.output(self.relayPin, GPIO.HIGH)
		time.sleep(0.05)

		print(f"Stepper turned {dir} {steps} steps")
