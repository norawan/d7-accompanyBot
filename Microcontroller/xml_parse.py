from music21 import *
from gpio import *
from macros import *

class Note:
    def __init__(self, pitch, octave, isTie):
        self.pitch = pitch
        self.octave = octave
        self.isTie = isTie

def createNoteObject(music21Note):
    pitch = music21Note.name
    octave = music21Note.octave
    isTie = (music21Note.tie == "start") or (music21Note.tie == "continue")

    return Note(pitch, octave, isTie)

def addNoteToValue(thisNote, offset, value):
    noteObject = createNoteObject(thisNote)
        
    if noteObject.pitch not in setOfPitchNames:
        print("ERROR: Bad note parsed. Invalid pitch name")
    
    notesScheduled = value.get(offset, "none")
    if (notesScheduled == "none"):
        notesScheduled = set()

    notesScheduled.add(noteObject) # Use noteObject.pitch for readability when debugging

    value[offset] = notesScheduled

def schedule(xmlFile, scheduledPiece):
    s = converter.parseFile(xmlFile)
    s.show('text')

    flattened = s.flatten()
    flattened.show('text')

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
    for tempoMark in flattened.getElementsByClass(tempo.MetronomeMark):
        beatType = tempoMark.referent.quarterLength
        tempoValue = tempoMark.number
    if (tempoValue == -1):
        print("ERROR: No Tempo detected. Using 60BPM as default\n")
        tempoValue = 60
    if (beatType == -1):
        print("ERROR: No beatType detected. Using quarter note as default\n")
        beatType = 1

    # (60,000,000,000 / tempo * beatType) = duration of a quarter note in ns
    # i.e. In a song with 120 bpm and 1 beat is 1 quarter note, a quarter note 
    #      will be (60,000 / (120 * 1)) = 500 ms long
    quarterLength_ns = 60000000000 / (tempoValue * beatType)
    measureDuration_ns = int(quarterLength_ns * beatType * beatCount)

    print("Beat Duration: " + str(beatDuration) + "\n")
    print("Beat Count: " + str(beatCount) + "\n")
    print("Beat Type: " + str(beatType) + "\n")
    print("Tempo Value: " + str(tempoValue) + "\n")
    print("Duration of a measure in nanoseconds: " + str(measureDuration_ns))

    # Mapping for notes to scheduledNotes dictionary
    # Key is measure number, value is a 

    for thisChord in flattened.getElementsByClass(chord.Chord):
        print("Measure number " + str(thisChord.offset))
        print(thisChord.pitchNames)
        print(thisChord.duration.quarterLength)
        
        measureNumber = int(thisChord.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()
        
        for thisNote in thisChord.notes:
            offset = (thisChord.offset % (beatCount * beatDuration)) / (beatCount * beatDuration)
            print("offset: " + str(offset))

            addNoteToValue(thisNote, offset, value)
        
        scheduledPiece[measureNumber] = value
        
    for thisNote in flattened.getElementsByClass(note.Note):
        print(thisNote.offset)
        print(thisNote.name)
        print(thisNote.duration.quarterLength)
        
        measureNumber = int(thisNote.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()
        
        offset = (thisNote.offset % (beatCount * beatDuration)) / (beatCount * beatDuration)
        print("offset: " + str(offset))

        addNoteToValue(thisNote, offset, value)
        
        scheduledPiece[measureNumber] = value
    
    for thisRest in flattened.getElementsByClass(note.Rest):
        measureNumber = int(thisRest.measureNumber)
        value = scheduledPiece.get(measureNumber, "none")
        if (value == "none"):
            value = dict()

        offset = (thisRest.offset % (beatCount * beatDuration)) / (beatCount * beatDuration)
        value[offset] = {}

        scheduledPiece[measureNumber] = value

    return (measureDuration_ns, totalMeasures, scheduledPiece)

scheduledPiece = dict()
schedule("Microcontroller/fiveNoteTest.xml", scheduledPiece)
print(scheduledPiece)