from stepper import Stepper
import time

testStepper = Stepper(stepPin=15, directionPin=11, enablePin=16, relayPin=10)

while True:
    testStepper.step(100, "right"); #steps, dir, speed, stayOn
    time.sleep(10)
    testStepper.step(100, "left"); #steps, dir, speed, stayOn
    time.sleep(10)
