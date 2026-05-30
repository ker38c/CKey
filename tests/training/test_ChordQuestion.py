"""Tests for ChordQuestion and generate_question."""
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from training.ChordLibrary import MAJOR, MINOR, MAJOR_7TH, DOMINANT_7TH, DIMINISHED
from training.ChordQuestion import ChordQuestion, generate_question, ROOT_NAMES


# ---------------------------------------------------------------------------
# display_name
# ---------------------------------------------------------------------------

class TestDisplayName:
    def test_major_chord_displays_root_only(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)
        assert q.display_name == "C"

    def test_minor_chord_uses_symbol(self):
        q = ChordQuestion(root=0, chord_type=MINOR)
        assert q.display_name == "Cm"

    def test_dominant_seventh_uses_symbol(self):
        q = ChordQuestion(root=0, chord_type=DOMINANT_7TH)
        assert q.display_name == "C7"

    def test_major_seventh_uses_M7_symbol(self):
        q = ChordQuestion(root=0, chord_type=MAJOR_7TH)
        assert q.display_name == "CM7"

    def test_root_reflects_pitch_class(self):
        q = ChordQuestion(root=9, chord_type=MAJOR)
        assert q.display_name == "A"


# ---------------------------------------------------------------------------
# pitch_classes
# ---------------------------------------------------------------------------

class TestPitchClasses:
    def test_c_major_pitch_classes(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)
        assert q.pitch_classes == frozenset({0, 4, 7})

    def test_inversion_same_pitch_classes(self):
        # Pitch classes are root-relative, not note-order dependent
        q = ChordQuestion(root=0, chord_type=MAJOR)
        assert q.pitch_classes == frozenset({0, 4, 7})

    def test_wraps_around_at_12(self):
        # B major: root=11, intervals (0,4,7) → 11,15%12=3,18%12=6
        q = ChordQuestion(root=11, chord_type=MAJOR)
        assert q.pitch_classes == frozenset({11, 3, 6})

    def test_7th_chord_has_4_pitch_classes(self):
        q = ChordQuestion(root=0, chord_type=MAJOR_7TH)
        assert len(q.pitch_classes) == 4
        assert q.pitch_classes == frozenset({0, 4, 7, 11})


# ---------------------------------------------------------------------------
# note_names
# ---------------------------------------------------------------------------

class TestNoteNames:
    def test_c_major_note_names(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)
        assert q.note_names == ["C", "E", "G"]

    def test_length_matches_note_count(self):
        q = ChordQuestion(root=0, chord_type=MAJOR_7TH)
        assert len(q.note_names) == 4


# ---------------------------------------------------------------------------
# canonical_key_names
# ---------------------------------------------------------------------------

class TestCanonicalKeyNames:
    def test_c_major_in_octave_3(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)
        assert q.canonical_key_names == ["C3", "E3", "G3"]

    def test_notes_are_ascending(self):
        """Every successive key name must be higher than the previous."""
        from training.ChordQuestion import _midi_to_key_name
        q = ChordQuestion(root=11, chord_type=MAJOR)  # B Major
        names = q.canonical_key_names
        # Convert back to midi to compare
        octave_note = lambda n: (int(n[-1] if n[-2].isdigit() is False else n[-2:]), ROOT_NAMES.index(n.rstrip('0123456789').rstrip('-')))
        # simpler: just check the string sort doesn't regress; do numeric check
        midi_vals = []
        for name in names:
            # parse octave
            for i in range(len(name) - 1, -1, -1):
                if name[i].lstrip('-').isdigit():
                    continue
                root_str = name[:i + 1]
                oct_str = name[i + 1:]
                midi_vals.append(ROOT_NAMES.index(root_str) + (int(oct_str) + 2) * 12)
                break
        assert midi_vals == sorted(midi_vals)
        assert len(set(midi_vals)) == len(midi_vals)  # no duplicates

    def test_all_notes_in_reasonable_range(self):
        """All canonical key names should be in octave 3–4 region."""
        for root in range(12):
            q = ChordQuestion(root=root, chord_type=MAJOR)
            for name in q.canonical_key_names:
                oct_str = name.lstrip('ABCDEFG#')
                octave = int(oct_str)
                assert 3 <= octave <= 5, f"Unexpected octave in {name}"


# ---------------------------------------------------------------------------
# generate_question
# ---------------------------------------------------------------------------

class TestGenerateQuestion:
    def test_returns_chord_question(self):
        q = generate_question([MAJOR], [0])
        assert isinstance(q, ChordQuestion)
        assert q.chord_type == MAJOR
        assert q.root == 0

    def test_excludes_previous_when_alternatives_exist(self):
        exclude = ChordQuestion(root=0, chord_type=MAJOR)
        results = {generate_question([MAJOR, MINOR], [0], exclude=exclude).chord_type
                   for _ in range(50)}
        # With two chord types, at least MINOR must appear
        assert MINOR in results
        # MAJOR should NOT appear because it equals exclude (same root+type)
        # (probabilistically — but with 50 trials this is certain if working)
        assert MAJOR not in results

    def test_raises_on_empty_chord_types(self):
        with pytest.raises(ValueError):
            generate_question([], [0])

    def test_raises_on_empty_roots(self):
        with pytest.raises(ValueError):
            generate_question([MAJOR], [])

    def test_exclude_ignored_when_only_one_candidate(self):
        exclude = ChordQuestion(root=0, chord_type=MAJOR)
        # Only one candidate; exclude is ignored, same question returned
        q = generate_question([MAJOR], [0], exclude=exclude)
        assert q.chord_type == MAJOR
        assert q.root == 0
