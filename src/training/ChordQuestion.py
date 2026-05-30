from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from training.ChordDefinition import ChordType

ROOT_NAMES: List[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROOT_NAMES_FLAT: List[str] = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# MIDI note number to key name used by the KeyBoard component.
# This app uses Yamaha convention: MIDI 60 = C3.
# Formula: octave = midi // 12 - 2, e.g. MIDI 60 -> octave 3 -> "C3"
def _midi_to_key_name(midi: int) -> str:
    octave = midi // 12 - 2
    return f"{ROOT_NAMES[midi % 12]}{octave}"


@dataclass(frozen=True)
class ChordQuestion:
    """An immutable chord question (root + chord type)."""
    root: int           # 0–11 (pitch class of the root note)
    chord_type: ChordType

    @property
    def display_name(self) -> str:
        """Human-readable chord name using sharp notation, e.g. 'C', 'C#m', 'C#M7'."""
        root_name = ROOT_NAMES[self.root]
        if self.chord_type.symbol == "":
            return root_name
        return f"{root_name}{self.chord_type.symbol}"

    def get_display_name(self, use_flat: bool = False) -> str:
        """Human-readable chord name with selectable notation.

        Args:
            use_flat: When True, accidentals are shown as flats (e.g. 'Db').
                      When False (default), accidentals are shown as sharps (e.g. 'C#').
        """
        names = ROOT_NAMES_FLAT if use_flat else ROOT_NAMES
        root_name = names[self.root]
        if self.chord_type.symbol == "":
            return root_name
        return f"{root_name}{self.chord_type.symbol}"

    @property
    def pitch_classes(self) -> frozenset:
        """Set of pitch classes (0–11) that form this chord."""
        return frozenset((self.root + interval) % 12 for interval in self.chord_type.intervals)

    @property
    def note_names(self) -> List[str]:
        """Pitch-class names without octave, e.g. ['C', 'E', 'G']."""
        return [ROOT_NAMES[(self.root + interval) % 12] for interval in self.chord_type.intervals]

    @property
    def canonical_key_names(self) -> List[str]:
        """Key names for keyboard highlight, anchored to octave 3 (MIDI 60 = C3).

        Notes are placed in ascending order starting from the root in octave 3,
        ascending by interval so each successive note is higher than the previous.
        """
        base_midi = 60 + self.root  # root in octave 3
        key_names: List[str] = []
        prev_midi = base_midi - 1
        for interval in self.chord_type.intervals:
            midi = base_midi + interval
            if midi <= prev_midi:
                midi += 12
            key_names.append(_midi_to_key_name(midi))
            prev_midi = midi
        return key_names


def generate_question(
    chord_types: List[ChordType],
    roots: List[int],
    exclude: Optional[ChordQuestion] = None,
) -> ChordQuestion:
    """Return a random ChordQuestion.

    Args:
        chord_types: Pool of chord types to choose from.
        roots: Pool of root pitch-classes (0–11) to choose from.
        exclude: If provided and more than one combination exists, the same
                 (root, chord_type) pair will not be returned consecutively.

    Raises:
        ValueError: If either pool is empty.
    """
    if not chord_types or not roots:
        raise ValueError("chord_types and roots must not be empty")

    candidates = [(r, ct) for r in roots for ct in chord_types]

    if exclude is not None and len(candidates) > 1:
        candidates = [
            (r, ct) for r, ct in candidates
            if not (r == exclude.root and ct == exclude.chord_type)
        ]

    r, ct = random.choice(candidates)
    return ChordQuestion(root=r, chord_type=ct)
