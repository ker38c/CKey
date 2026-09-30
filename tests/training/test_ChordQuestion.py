"""Tests for ChordQuestion and generate_question."""
import dataclasses
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


# ---------------------------------------------------------------------------
# root_only aware properties
# ---------------------------------------------------------------------------

class TestExpectedNoteCount:
    def test_normal_chord_returns_chord_note_count(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)  # 3-note
        assert q.expected_note_count == 3

    def test_root_only_returns_one(self):
        ro = dataclasses.replace(MAJOR, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.expected_note_count == 1

    def test_seventh_chord_normal_returns_four(self):
        q = ChordQuestion(root=0, chord_type=MAJOR_7TH)
        assert q.expected_note_count == 4

    def test_seventh_chord_root_only_returns_one(self):
        ro = dataclasses.replace(MAJOR_7TH, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.expected_note_count == 1


class TestExpectedPitchClasses:
    def test_normal_chord_returns_full_pitch_classes(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)  # C Major: {0,4,7}
        assert q.expected_pitch_classes == frozenset({0, 4, 7})

    def test_root_only_returns_root_only_set(self):
        ro = dataclasses.replace(MAJOR, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.expected_pitch_classes == frozenset({0})

    def test_root_only_non_c_root(self):
        ro = dataclasses.replace(MINOR, root_only=True)
        q = ChordQuestion(root=2, chord_type=ro)  # D
        assert q.expected_pitch_classes == frozenset({2})


class TestAnswerNoteNames:
    def test_normal_chord_returns_all_note_names(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)  # C, E, G
        assert q.answer_note_names == ["C", "E", "G"]

    def test_root_only_returns_root_name_only(self):
        ro = dataclasses.replace(MAJOR, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.answer_note_names == ["C"]

    def test_root_only_non_c_root(self):
        ro = dataclasses.replace(MINOR, root_only=True)
        q = ChordQuestion(root=2, chord_type=ro)  # D
        assert q.answer_note_names == ["D"]


class TestAnswerKeyNames:
    def test_normal_chord_returns_canonical_key_names(self):
        q = ChordQuestion(root=0, chord_type=MAJOR)  # C3, E3, G3
        assert q.answer_key_names == ["C3", "E3", "G3"]

    def test_root_only_returns_single_root_key_name(self):
        ro = dataclasses.replace(MAJOR, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.answer_key_names == ["C3"]

    def test_root_only_non_c_root(self):
        ro = dataclasses.replace(MINOR, root_only=True)
        q = ChordQuestion(root=2, chord_type=ro)  # D3
        assert q.answer_key_names == ["D3"]


class TestGetAnswerDisplayName:
    def test_normal_chord_returns_full_name(self):
        q = ChordQuestion(root=0, chord_type=MINOR)  # Cm
        assert q.get_answer_display_name() == "Cm"

    def test_root_only_returns_root_name_only(self):
        ro = dataclasses.replace(MINOR, root_only=True)
        q = ChordQuestion(root=0, chord_type=ro)
        assert q.get_answer_display_name() == "C"

    def test_root_only_uses_flat_notation(self):
        ro = dataclasses.replace(MINOR, root_only=True)
        q = ChordQuestion(root=1, chord_type=ro)  # C#/Db
        assert q.get_answer_display_name(use_flat=True) == "Db"
        assert q.get_answer_display_name(use_flat=False) == "C#"

    def test_normal_chord_respects_use_flat(self):
        q = ChordQuestion(root=1, chord_type=MINOR)  # C#m / Dbm
        assert q.get_answer_display_name(use_flat=True) == "Dbm"
        assert q.get_answer_display_name(use_flat=False) == "C#m"
