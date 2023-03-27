# Useful Macros

# Pin Macros
PIN0 = 17
PIN1 = 27
PIN2 = 22
PIN3 = 23
PIN4 = 24
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

POSSIBLE_PINS = PIN0_MASK | PIN1_MASK | PIN2_MASK | PIN3_MASK | PIN4_MASK | PIN5_MASK | PIN6_MASK | PIN7_MASK | PIN8_MASK | PIN9_MASK | PIN10_MASK | PIN11_MASK | PIN12_MASK

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
    PIN12 : PIN12_MASK
}

# Assign Notes to Pins
# Defaults to start on C scale
noteToPinDict = {
    "C" : PIN0,
    "C#" : PIN1,
    "D-" : PIN1,
    "D" : PIN2,
    "D#" : PIN3,
    "E-" : PIN3,
    "E" : PIN4,
    # space between E/F is not mapped
    "F" : PIN6,
    "F#" : PIN7,
    "G-" : PIN7,
    "G" : PIN8,
    "G#" : PIN9,
    "A-" : PIN9,
    "A" : PIN10,
    "A#" : PIN11,
    "B-" : PIN11,
    "B" : PIN12
    # space between B/C is not mapped
}

# Set of possible starting notes
startingNoteToOffset = {
    "C" : 0,
    "D" : 1,
    "E" : 2,
    "F" : 3,
    "G" : 4,
    "A" : 5,
    "B" : 6
}

NUM_PINS = 13

noteToIndex = {
    "C" : 0,
    "C#" : 1,
    "D-" : 1,
    "D" : 2,
    "D#" : 3,
    "E-" : 3,
    "E" : 4,
    # space between E/F is not mapped
    "F" : 6,
    "F#" : 7,
    "G-" : 7,
    "G" : 8,
    "G#" : 9,
    "A-" : 9,
    "A" : 10,
    "A#" : 11,
    "B-" : 11,
    "B" : 12
    # space between B/C is not mapped
}