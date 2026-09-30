"""Tests for TrainingTab.get_settings (Root Only handling)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gui.TrainingTab import TrainingTab
from training.ChordLibrary import MAJOR, MINOR, MAJOR_7TH
from training.SessionMode import SessionMode


class FakeVar:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def _make_tab(mode: SessionMode, root_only: bool) -> TrainingTab:
    """Build a TrainingTab without creating Tk widgets."""
    tab = object.__new__(TrainingTab)
    tab._root_only_var = FakeVar(root_only)
    tab._mode_var = FakeVar(mode.value)
    tab._triad_vars = [(FakeVar(True), MAJOR), (FakeVar(False), MINOR)]
    tab._seventh_vars = [(FakeVar(True), MAJOR_7TH)]
    tab._root_vars = [(FakeVar(True), 0)]
    tab._debounce_var = FakeVar("300")
    tab._use_flat_var = FakeVar(False)
    return tab


class TestGetSettingsRootOnly:
    def test_hearing_with_root_only_marks_chord_types(self):
        settings = _make_tab(SessionMode.HEARING, True).get_settings()

        assert len(settings.chord_types) == 2
        assert all(ct.root_only for ct in settings.chord_types)

    def test_hearing_without_root_only_keeps_chord_types(self):
        settings = _make_tab(SessionMode.HEARING, False).get_settings()

        assert settings.chord_types == [MAJOR, MAJOR_7TH]

    def test_chord_play_ignores_root_only(self):
        settings = _make_tab(SessionMode.CHORD_PLAY, True).get_settings()

        assert settings.chord_types == [MAJOR, MAJOR_7TH]
        assert not any(ct.root_only for ct in settings.chord_types)
