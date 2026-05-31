"""Tests for HearingMode."""
import sys
import os
import time
import threading
import types

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from training.ChordLibrary import MAJOR, MINOR
from training.ChordQuestion import ChordQuestion


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------

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


class FakeMidiHandler:
    """Records play_chord / stop_chord calls."""

    def __init__(self):
        self.play_calls = []
        self.stop_chord_count = 0
        self._lock = threading.Lock()

    def play_chord(self, midi_notes, velocity=80, duration_s=0.5):
        with self._lock:
            self.play_calls.append(list(midi_notes))

    def stop_chord(self):
        with self._lock:
            self.stop_chord_count += 1


def _wait_for(condition, timeout=3.0, interval=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


from training.HearingMode import HearingMode


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHearingModeLifecycle:
    def test_not_active_before_start(self):
        mode = HearingMode(FakeDispatcher(), FakeMidiHandler(), debounce_ms=50)
        assert not mode.is_active

    def test_active_after_start(self):
        mode = HearingMode(FakeDispatcher(), FakeMidiHandler(), debounce_ms=50)
        mode.start([MAJOR], list(range(12)))
        assert mode.is_active
        mode.stop()

    def test_not_active_after_stop(self):
        mode = HearingMode(FakeDispatcher(), FakeMidiHandler(), debounce_ms=50)
        mode.start([MAJOR], [0])
        mode.stop()
        assert not mode.is_active

    def test_start_plays_chord(self):
        handler = FakeMidiHandler()
        mode = HearingMode(FakeDispatcher(), handler, debounce_ms=50)
        mode.start([MAJOR], [0])
        assert _wait_for(lambda: len(handler.play_calls) > 0)
        mode.stop()

    def test_start_dispatches_show_listen_prompt(self):
        dispatcher = FakeDispatcher()
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=50)
        mode.start([MAJOR], [0])
        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))
        mode.stop()

    def test_score_zero_at_start(self):
        mode = HearingMode(FakeDispatcher(), FakeMidiHandler(), debounce_ms=50)
        mode.start([MAJOR], [0])
        assert mode.score == (0, 0)
        mode.stop()

    def test_stop_calls_stop_chord(self):
        handler = FakeMidiHandler()
        mode = HearingMode(FakeDispatcher(), handler, debounce_ms=50)
        mode.start([MAJOR], [0])
        mode.stop()
        assert handler.stop_chord_count >= 1

    def test_second_start_ignored_while_active(self):
        dispatcher = FakeDispatcher()
        handler = FakeMidiHandler()
        mode = HearingMode(dispatcher, handler, debounce_ms=50)
        mode.start([MAJOR], [0])
        dispatcher.clear()
        mode.start([MINOR], [0])
        time.sleep(0.05)
        assert mode.is_active
        mode.stop()


class TestHearingModeReplay:
    def test_replay_plays_chord_in_waiting_state(self):
        handler = FakeMidiHandler()
        mode = HearingMode(FakeDispatcher(), handler, debounce_ms=50)
        mode.start([MAJOR], [0])
        assert _wait_for(lambda: len(handler.play_calls) >= 1)
        count_before = len(handler.play_calls)
        mode.replay()
        assert _wait_for(lambda: len(handler.play_calls) > count_before)
        mode.stop()

    def test_replay_does_nothing_when_idle(self):
        handler = FakeMidiHandler()
        mode = HearingMode(FakeDispatcher(), handler, debounce_ms=50)
        mode.replay()
        time.sleep(0.05)
        assert len(handler.play_calls) == 0


class TestHearingModeEvaluation:
    def test_correct_answer_increments_score(self):
        dispatcher = FakeDispatcher()
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=30)
        mode.start([MAJOR], [0])  # C Major: pitch classes {0, 4, 7}

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))

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
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=30)
        mode.start([MAJOR], [0])  # C Major: {0, 4, 7}

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))

        # Play wrong chord (C, E, G# = Augmented)
        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(68)

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_feedback_wrong'),
                         timeout=2.0)
        assert mode.score == (0, 1)
        mode.stop()

    def test_correct_answer_reveals_chord_name(self):
        dispatcher = FakeDispatcher()
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=30)
        mode.start([MAJOR], [0])  # C Major

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))

        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(67)

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_question'),
                         timeout=2.0)
        mode.stop()

    def test_feedback_disables_listen_again(self):
        dispatcher = FakeDispatcher()
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=30)
        mode.start([MAJOR], [0])

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))

        mode.on_note_on(60)
        mode.on_note_on(64)
        mode.on_note_on(67)

        assert _wait_for(
            lambda: any(
                c[0] == 'training_display' and c[1] == 'set_listen_again_enabled' and c[2] is False
                for c in dispatcher.get_calls()
            ),
            timeout=2.0,
        )
        mode.stop()

    def test_insufficient_notes_not_evaluated(self):
        dispatcher = FakeDispatcher()
        mode = HearingMode(dispatcher, FakeMidiHandler(), debounce_ms=50)
        mode.start([MAJOR], [0])  # needs 3 notes

        assert _wait_for(lambda: dispatcher.has_call('training_display', 'show_listen_prompt'))

        # Only 2 notes
        mode.on_note_on(60)
        mode.on_note_on(64)

        time.sleep(0.2)
        assert not dispatcher.has_call('training_display', 'show_feedback_correct')
        assert not dispatcher.has_call('training_display', 'show_feedback_wrong')
        mode.stop()
