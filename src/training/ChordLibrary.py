from training.ChordDefinition import ChordType

# --- 3-note chords ---
MAJOR = ChordType("Major", "", (0, 4, 7), 3)
MINOR = ChordType("Minor", "m", (0, 3, 7), 3)
AUGMENTED = ChordType("Augmented", "aug", (0, 4, 8), 3)
DIMINISHED = ChordType("Diminished", "dim", (0, 3, 6), 3)
SUS2 = ChordType("sus2", "sus2", (0, 2, 7), 3)
SUS4 = ChordType("sus4", "sus4", (0, 5, 7), 3)

# --- 4-note chords ---
MAJOR_7TH = ChordType("Major 7th", "M7", (0, 4, 7, 11), 4)
MINOR_7TH = ChordType("Minor 7th", "m7", (0, 3, 7, 10), 4)
DOMINANT_7TH = ChordType("Dominant 7th", "7", (0, 4, 7, 10), 4)
MINOR_MAJOR_7TH = ChordType("Minor Major 7th", "mM7", (0, 3, 7, 11), 4)
HALF_DIMINISHED = ChordType("Half Diminished", "m7(b5)", (0, 3, 6, 10), 4)
DIMINISHED_7TH = ChordType("Diminished 7th", "dim7", (0, 3, 6, 9), 4)

TRIADS = [MAJOR, MINOR, AUGMENTED, DIMINISHED, SUS2, SUS4]
SEVENTH_CHORDS = [MAJOR_7TH, MINOR_7TH, DOMINANT_7TH, MINOR_MAJOR_7TH, HALF_DIMINISHED, DIMINISHED_7TH]
ALL_CHORDS = TRIADS + SEVENTH_CHORDS
