# Useful Macros

# Pin Numbers --> Static
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
PIN11 = 12

NUM_PINS = 12

# Corresponding bit masks --> Static
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

POSSIBLE_PINS = PIN0_MASK | PIN1_MASK | PIN2_MASK | PIN3_MASK | PIN4_MASK | PIN5_MASK | PIN6_MASK | PIN7_MASK | PIN8_MASK | PIN9_MASK | PIN10_MASK | PIN11_MASK

# Assign Pin Masks to Pins --> Static
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
    PIN11 : PIN11_MASK
}

# Notes to Pin mapping --> Dynamic
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
    "F" : PIN5,
    "F#" : PIN6,
    "G-" : PIN6,
    "G" : PIN7,
    "G#" : PIN8,
    "A-" : PIN8,
    "A" : PIN9,
    "A#" : PIN10,
    "B-" : PIN10,
    "B" : PIN11,
    "C-" : PIN11
    # space between B/C is not mapped
}

# Note to pin index
noteToPinIndex = {
    "C" : 0,
    "C#" : 1,
    "D-" : 1,
    "D" : 2,
    "D#" : 3,
    "E-" : 3,
    "E" : 4,
    # space between E/F is not mapped
    "F" : 5,
    "F#" : 6,
    "G-" : 6,
    "G" : 7,
    "G#" : 8,
    "A-" : 8,
    "A" : 9,
    "A#" : 10,
    "B-" : 10,
    "B" : 11,
    "C-" : 11
    # space between B/C is not mapped
}

setOfPitchNames = { "C-", "C", "C#", "D-", "D", "D#", "E-", "E", "F", "F#",  "G-",
                    "G", "G#", "A-", "A", "A#", "B-", "B" }