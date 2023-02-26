# Useful Macros

POSSIBLE_PINS = 0xC432E6C

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

# Assign Pin Masks to Pins
pinToPinMaskDict = {
    PIN0 : PIN0_MASK,
    PIN1 : PIN1_MASK,
    PIN2 : PIN2_MASK,
    PIN3 : PIN3_MASK,
    PIN4 : PIN4_MASK,
    PIN5 : PIN5_MASK,
    PIN6 : PIN6_MASK,
    PIN7 : PIN7_MASK,
    PIN8 : PIN8_MASK,
    PIN9 : PIN9_MASK,
    PIN10 : PIN10_MASK,
    PIN11 : PIN11_MASK,
}

# Assign Notes to Pins
noteToPinDict = {
    "C" : PIN0,
    "C#" : PIN1,
    "D" : PIN2,
    "D#" : PIN3,
    "E" : PIN4,
    "F" : PIN5,
    "F#" : PIN6,
    "G" : PIN7,
    "G#" : PIN8,
    "A" : PIN9,
    "A#" : PIN10,
    "B" : PIN11
}