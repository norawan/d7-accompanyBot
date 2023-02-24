import pigpio

# Create pigpio object
pi = pigpio.pi()

# Pin Macros
PIN0 = 2
PIN1 = 3
PIN2 = 17
PIN3 = 27
PIN4 = 22
PIN5 = 10
PIN6 = 9
PIN7 = 11
PIN8 = 5
PIN9 = 6
PIN10 = 13
PIN11 = 16
PIN12 = 26

# Corresponding bit masks
PIN0_MASK = 1 << PIN0
PIN1_MASK = 1 << PIN1
PIN2_MASK = 1 << PIN2
PIN3_MASK = 1 << PIN3
PIN4_MASK = 1 << PIN4
PIN5_MASK = 1 << PIN5
PIN6_MASK = 1 << PIN6
PIN7_MASK = 1 << PIN7
PIN8_MASK = 1 << PIN8
PIN9_MASK = 1 << PIN9
PIN10_MASK = 1 << PIN10
PIN11_MASK = 1 << PIN11
PIN12_MASK = 1 << PIN12

# Set up pins as outputs
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
pi.set_mode(PIN12, pigpio.OUTPUT)