from music21 import *
from gpio import *
from pin_mapping import *

# Solenoids can only play four notes a second (250ms to go down and up), so a 
# note cannot be longer than 125ms
MINIMUM_NOTE_DURATION_NS = 125000000 
NUM_NS_IN_ONE_MINUTE = 60000000000

class Note:
    def __init__(self, pitch, octave, state):
        self.pitch = pitch
        self.octave = octave
        self.state = state # 1 for pressing down, 0 for lifting up
    
class TempoObject:
    def __init__(self, tempoValue, beatType, beatCount, beatDuration, maxTempo):
        self.tempoValue = tempoValue
        self.beatType = beatType
        self.beatCount = beatCount
        self.beatDuration = beatDuration
        self.maxTempo = maxTempo
    
    def getMeasureDuration_ns(self):
        quarterLength_ns = NUM_NS_IN_ONE_MINUTE / (self.tempoValue * self.beatType)
        measureDuration = self.beatCount * self.beatDuration 
        return int(quarterLength_ns *  measureDuration)

def addNoteToValue(thisNote, offset, value, measureDuration):
    pitch = thisNote.name
    octave = thisNote.octave
    duration = thisNote.duration.quarterLength
    if (thisNote.tie != None):
        tieType = (thisNote.tie.type)
        isTie = ((tieType == "start") or (tieType == "continue"))
    else: isTie = False

    if pitch not in setOfPitchNames:
        print("ERROR: Bad note parsed. Invalid pitch name")

    downNotesScheduled = value.get(offset, "none")
    if (downNotesScheduled == "none"):
        downNotesScheduled = set()

    # Press note down at offset
    downNote = Note(pitch, octave, 1)
    downNotesScheduled.add(downNote) # Use note.pitch for readability when debugging
    value[offset] = downNotesScheduled

    # Lift note up at offset + duration
    if (not isTie):
        liftTime = offset + (0.75) * duration / measureDuration

        upNotesScheduled = value.get(liftTime, "none")
        if (upNotesScheduled == "none"):
            upNotesScheduled = set()

        upNote = Note(pitch, octave, 0)
        upNotesScheduled.add(upNote)
        value[liftTime] = upNotesScheduled
    
    return duration

def schedule(xmlFile, scheduledPiece):
    s = converter.parseFile(xmlFile)
    s.show('text')

    flattened = s.flatten()
    # flattened.show('text')

    totalMeasures = flattened.notes[-1].measureNumber
    
    # Durations are in terms of quarterLength (A quarter note is worth 1.0 unit)

    # Get Time Signature Info
    beatDuration = -1
    beatCount = -1
    for ts in flattened.getElementsByClass(meter.TimeSignature):
        beatDuration = ts.beatLengthToQuarterLengthRatio
        beatCount = ts.beatCount
    if (beatDuration == -1):
        print("ERROR: No Time Signature detected\n")
        beatDuration = 1
    if (beatCount == -1):
        print("ERROR: No beat count found. Using 4 beats per measure as default\n")
        beatCount = 4

    # Get Tempo Info
    beatType = -1
    tempoValue = -1

    # Uses the format for badly parsed tempos (Tempos show up as "J=" or "J:")
    for textBox in flattened.getElementsByClass(text.TextBox):
        string = textBox.content
        # print(string)
        if ("J=" in string):
            arr = string.split("J=")
            tempoValue = int(arr[1])
        if ("J:" in string):
            arr = string.split("J:")
            tempoValue = int(arr[1])
    print("Tempo: " + str(tempoValue))

    # Actual tempo data structure in music21
    for tempoMark in flattened.getElementsByClass(tempo.MetronomeMark):
        beatType = tempoMark.referent.quarterLength
        tempoValue = tempoMark.number
    if (tempoValue == -1):
        print("ERROR: No Tempo detected. Using 120BPM as default\n")
        tempoValue = 120
    if (beatType == -1):
        print("ERROR: No beatType detected. Using quarter note as default\n")
        beatType = 1

    # (60,000,000,000 / tempo * beatType) = duration of a quarter note in ns
    # i.e. In a song with 120 bpm and 1 beat is 1 quarter note, a quarter note 
    #      will be (60,000 / (120 * 1)) = 500 ms long
    measureDuration = beatCount * beatDuration 

    smallestDuration = -1

    # print("Beat Duration: " + str(beatDuration) + "\n")
    # print("Beat Count: " + str(beatCount) + "\n")
    # print("Beat Type: " + str(beatType) + "\n")
    # print("Tempo Value: " + str(tempoValue) + "\n")
    # print("Duration of a measure in nanoseconds: " + str(measureDuration_ns))

    # Mapping for notes to scheduledNotes dictionary

    for thisChord in flattened.getElementsByClass(chord.Chord):
        # print("Measure number " + str(thisChord.offset))
        # print(thisChord.pitchNames)
        # print(thisChord.duration.quarterLength)
        # print(thisChord.tie)
        
        measureNumber = int(thisChord.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()
        
        for thisNote in thisChord.notes:
            offset = (thisChord.offset % (measureDuration)) / (measureDuration)
            # print("offset: " + str(offset))

            noteDuration = addNoteToValue(thisNote, offset, value, measureDuration)
            if (smallestDuration == -1):
                smallestDuration = noteDuration
            else:
                if (noteDuration < smallestDuration):
                    smallestDuration = noteDuration

        scheduledPiece[measureNumber] = value
        
    for thisNote in flattened.getElementsByClass(note.Note):
        # print(thisNote.offset)
        # print(thisNote.name)
        # print(thisNote.duration.quarterLength)
        
        measureNumber = int(thisNote.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()
        
        offset = (thisNote.offset % (measureDuration)) / (measureDuration)
        # print("offset: " + str(offset))

        noteDuration = addNoteToValue(thisNote, offset, value, measureDuration)
        if (smallestDuration == -1):
            smallestDuration = noteDuration
        else:
            if (noteDuration < smallestDuration):
                smallestDuration = noteDuration

        scheduledPiece[measureNumber] = value
    
    for thisRest in flattened.getElementsByClass(note.Rest):
        measureNumber = int(thisRest.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()

        offset = (thisRest.offset % (measureDuration)) / (measureDuration)
        value[offset] = {}

        scheduledPiece[measureNumber] = value

        restDuration = thisRest.duration
        if (smallestDuration == -1):
            smallestDuration = restDuration
        else:
            if (noteDuration < smallestDuration):
                smallestDuration = restDuration

    print("Smallest duration: " + str(smallestDuration))

    maxTempo = (NUM_NS_IN_ONE_MINUTE / MINIMUM_NOTE_DURATION_NS) * (smallestDuration / beatType)

    tempoInfo = TempoObject(tempoValue, beatType, beatCount, beatDuration, maxTempo)

    return (tempoInfo, totalMeasures, scheduledPiece)
