from music21 import *
from gpio import *
from macros import *

def schedule(xmlFile, smallestNote, notesDict, liftsDict):
    s = converter.parseFile(xmlFile)
    s.show('text')

    flattened = s.flatten()
    flattened.show('text')
    
    # Get Time Signature Info
    beatDuration = -1
    for ts in flattened.getElementsByClass(meter.TimeSignature):
        beatDuration = ts.beatLengthToQuarterLengthRatio
    if (beatDuration == -1):
        print("Error: No Time Signature detected\n")

    # Get Tempo Info
    beatType = -1
    tempoValue = -1
    for tempoMark in flattened.getElementsByClass(tempo.MetronomeMark):
        beatType = tempoMark.referent.quarterLength
        tempoValue = tempoMark.number
    if (tempoValue == -1):
        print("Error: No Tempo detected. Using 60BPM as default\n")
        tempoValue = 60
    if (beatType == -1):
        print("Error: No beatType detected. Using 1 as default\n")
        beatType = 1

    # (60,000 / tempo * beatType) = duration of a quarter note in ms
    # i.e. In a song with 120 bpm and 1 beat is 1 quarter note, a quarter note 
    #      will be (60,000 / 120 * 1) = 500 ms long
    quarterLengthInMiliseconds = 60000 / (tempoValue * beatType)
    durationOfSmallestNote = quarterLengthInMiliseconds * 4 / smallestNote

    print(beatDuration)
    print(beatType)
    print(tempoValue)
    print(durationOfSmallestNote)

    # Mapping for notes to timestamps
    previousOffset = -1
    noteCounter = 0 # keeps track of whether there are more than five notes in a chord
    for thisChord in flattened.getElementsByClass(chord.Chord):
        print(thisChord.offset)
        print(thisChord.pitchNames)
        print(thisChord.duration.quarterLength)
        
        offset = thisChord.offset
        
        for thisNote in thisChord.notes:
            noteValue = thisNote.name
            noteDuration = thisNote.duration.quarterLength

            pin = noteToPinDict.get(noteValue, "NO PIN")
            if (pin == "NO PIN"):
                print("Error: Bad note parsed\n")
                return
            pinMask = pinToPinMaskDict.get(pin)
            
            timestamp = offset * (smallestNote / 4)
            
            value = notesDict.get(timestamp, "none")
            if (value == "none"):
                notesDict[timestamp] = pinMask
            else:
                notesDict[timestamp] |= pinMask

            # Schedule when to lift up the note
            laterTimestamp = timestamp + noteDuration * (smallestNote / 4)
            liftList = liftsDict.get(laterTimestamp, "none")
            if (liftList == "none"):
                liftsDict[laterTimestamp] = list([pin])
            else:
                liftsDict[laterTimestamp].append(pin)
        
    for thisNote in flattened.getElementsByClass(note.Note):
        print(thisNote.offset)
        print(thisNote.name)
        print(thisNote.duration.quarterLength)
        
        offset = thisNote.offset
        
        noteValue = thisNote.name
        noteDuration = thisNote.duration.quarterLength

        pin = noteToPinDict.get(noteValue, "NO PIN")
        if (pin == "NO PIN"):
            print("Error: Bad note parsed\n")
            return
        pinMask = pinToPinMaskDict.get(pin)
        
        timestamp =  thisNote.offset * (smallestNote / 4)
        
        value = notesDict.get(timestamp, "none")
        if (value == "none"):
            notesDict[timestamp] = pinMask
        else:
            notesDict[timestamp] |= pinMask

        # Schedule when to lift up the note
        laterTimestamp = timestamp + noteDuration * (smallestNote / 4)
        liftList = liftsDict.get(laterTimestamp, "none")
        if (liftList == "none"):
            liftsDict[laterTimestamp] = list([pin])
        else:
            liftsDict[laterTimestamp].append(pin)
    
    for thisRest in flattened.getElementsByClass(note.Rest):
        timestamp = thisRest.offset * (smallestNote / 4)
        notesDict[timestamp] = 0 # For rests, no notes should be played

    return (durationOfSmallestNote, notesDict)
