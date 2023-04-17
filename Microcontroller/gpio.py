import pigpio
from pin_mapping import *

# Set up pins as outputs
def setUpPins():
    # Create pigpio object
    pi = pigpio.pi()

    pi.set_mode(PIN0, pigpio.OUTPUT)
    pi.set_mode(PIN1, pigpio.OUTPUT)
    pi.set_mode(PIN2, pigpio.OUTPUT)
    pi.set_mode(PIN3, pigpio.OUTPUT)
    pi.set_mode(PIN4, pigpio.OUTPUT)
    pi.set_mode(PIN5, pigpio.OUTPUT)
    pi.set_mode(PIN6, pigpio.OUTPUT)
    pi.set_mode(PIN7, pigpio.OUTPUT)
    pi.set_mode(PIN8, pigpio.OUTPUT)
    pi.set_mode(PIN9, pigpio.OUTPUT)
    pi.set_mode(PIN10, pigpio.OUTPUT)
    pi.set_mode(PIN11, pigpio.OUTPUT)

    return pi