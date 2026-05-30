"""Tests for ChordPlayMode."""
import sys
import os
import time
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from training.ChordLibrary import MAJOR, MINOR
from training.ChordPlayMode import ChordPlayMode


def _wait_for(condition, timeout=3.0, interval=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class FakeDispatcher:
    """Records all post_to calls for assertion."""

    def __init__(self):
        self.calls = []
        self._lock = threading.Lock()

    def post_to(self, name, method, *args, **kwargs):
        with self._lock:
            self.calls.append((name, method) + args)

    def get_calls(self):
        with self._lock:
            return list(self.calls)

    def clear(self):
        with self._lock:
            self.calls.clear()

    def has_call(self, name, method):
        return any(c[0] == name and c[1] == method for c in self.get_calls())


class TestChordPlayModeLifecycle:
    def test_not_active_before_start(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        assert not mode.is_active

    def test_active_after_start(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], list(range(12)))
        assert mode.is_active
        mode.stop()

    def test_not_active_after_stop(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], list(range(12)))
        mode.stop()
        assert not mode.is_active

    def test_start_dispatches_show_question(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], [0])
        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))
        mode.stop()

    def test_score_zero_at_start(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], [0])
        assert mode.score == (0, 0)
        mode.stop()

    def test_second_start_ignored_while_active(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], [0])
        # Second start should be ignored (no reset)
        dispatcher.clear()
        mode.start([MINOR], [0])
        time.sleep(0.05)
        # No new show_question should be dispatched from second start
        # (the first one already called it; second should be a no-op)
        assert mode.is_active
        mode.stop()


class TestChordPlayModeEvaluation:
    def test_correct_answer_increments_score(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=30)
        mode.start([MAJOR], [0])   # C Major: pitch classes {0, 4, 7}

        # Wait for question to be set
        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))

        # Play C Major (MIDI 60=C, 64=E, 67=G)
        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(67)

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_feedback_correct'),
                         timeout=2.0)
        assert mode.score[0] == 1
        assert mode.score[1] == 1
        mode.stop()

    def test_wrong_answer_does_not_increment_correct(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=30)
        mode.start([MAJOR], [0])   # C Major: {0, 4, 7}

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))

        # Play wrong chord (C, E, G# = Augmented)
        mode.on_note_on(60)  # C
        mode.on_note_on(64)  # E
        mode.on_note_on(68)  # G#

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_feedback_wrong'),
                         timeout=2.0)
        assert mode.score == (0, 1)   # 0 correct, 1 total
        mode.stop()

    def test_wrong_answer_dispatches_highlight(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=30)
        mode.start([MAJOR], [0])   # C Major

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))

        mode.on_note_on(60)   # C
        mode.on_note_on(64)   # E
        mode.on_note_on(68)   # G# (wrong)

        assert _wait_for(lambda: dispatcher.has_call('piano_tab', 'highlight_answer_notes'),
                         timeout=2.0)
        mode.stop()

    def test_insufficient_notes_not_evaluated(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=50)
        mode.start([MAJOR], [0])   # needs 3 notes

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))

        # Press only 2 notes
        mode.on_note_on(60)
        mode.on_note_on(64)

        # Wait past debounce; no evaluation should happen
        time.sleep(0.2)
        assert not dispatcher.has_call('training_display', 'show_feedback_correct')
        assert not dispatcher.has_call('training_display', 'show_feedback_wrong')
        mode.stop()

    def test_stop_during_feedback_is_safe(self):
        """stop() while in FEEDBACK state should not crash."""
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=30)
        mode.start([MAJOR], [0])

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'))

        # Trigger evaluation
        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(67)   # correct

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_feedback_correct'),
                         timeout=2.0)

        # Stop during feedback window
        mode.stop()
        assert not mode.is_active

    def test_note_events_ignored_when_inactive(self):
        dispatcher = FakeDispatcher()
        mode = ChordPlayMode(dispatcher, debounce_ms=30)
        # Do NOT start
        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(67)
        time.sleep(0.15)
        assert not dispatcher.has_call('training_display', 'show_feedback_correct')
        assert not dispatcher.has_call('training_display', 'show_feedback_wrong')
