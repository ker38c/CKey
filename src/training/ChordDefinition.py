from dataclasses import dataclass


@dataclass(frozen=True)
class ChordType:
    """Immutable definition of a chord type."""
    name: str        # Descriptive name used in settings UI labels, e.g. "Major"
    symbol: str      # Symbol appended to root note name; empty string displays as root name only, e.g. "" for Major → "C", "m" for Minor → "Cm"
    intervals: tuple # Semitone intervals from root in ascending order, e.g. (0, 4, 7)
    note_count: int  # Number of distinct pitch classes (= len(intervals))
