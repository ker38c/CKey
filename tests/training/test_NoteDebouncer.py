"""Tests for NoteDebouncer."""
import sys
import os
import time
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from training.NoteDebouncer import NoteDebouncer


def _wait_for(condition, timeout=2.0, interval=0.01):
    """Poll *condition* until True or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class TestNoteDebouncer:
    def test_fires_after_silence(self):
        """Callback is called once after no new events for debounce period."""
        results = []
        d = NoteDebouncer(debounce_ms=50, callback=lambda pcs: results.append(pcs))

        d.note_on(60)
        assert _wait_for(lambda: len(results) == 1, timeout=1.0)
        assert results[0] == frozenset({0})   # 60 % 12 == 0 (C)

    def test_multiple_note_ons_single_fire(self):
        """Rapid note-ons produce only one callback."""
        results = []
        d = NoteDebouncer(debounce_ms=100, callback=lambda pcs: results.append(pcs))

        d.note_on(60)  # C
        d.note_on(64)  # E
        d.note_on(67)  # G

        assert _wait_for(lambda: len(results) == 1, timeout=1.5)
        time.sleep(0.05)  # extra wait to confirm no second call
        assert len(results) == 1
        assert results[0] == frozenset({0, 4, 7})

    def test_resets_timer_on_note_off(self):
        """note_off during debounce window resets the timer."""
        call_times = []
        d = NoteDebouncer(debounce_ms=150, callback=lambda pcs: call_times.append(time.monotonic()))

        start = time.monotonic()
        d.note_on(60)
        time.sleep(0.08)  # 80 ms — timer should reset
        d.note_off(60)    # reset timer
        # callback should NOT fire before ~150 ms from note_off
        assert _wait_for(lambda: len(call_times) == 1, timeout=1.5)
        elapsed = call_times[0] - start
        assert elapsed >= 0.08 + 0.10, f"Callback fired too early: {elapsed:.3f}s"

    def test_cancel_prevents_callback(self):
        """cancel() stops the timer and suppresses the callback."""
        results = []
        d = NoteDebouncer(debounce_ms=100, callback=lambda pcs: results.append(pcs))

        d.note_on(60)
        d.cancel()
        time.sleep(0.2)  # wait longer than debounce
        assert results == []

    def test_reset_clears_pressed_notes_and_timer(self):
        """reset() clears notes and suppresses any pending callback."""
        results = []
        d = NoteDebouncer(debounce_ms=100, callback=lambda pcs: results.append(pcs))

        d.note_on(60)
        d.note_on(64)
        d.reset()
        time.sleep(0.2)
        assert results == []

    def test_pitch_class_reduction(self):
        """Notes are reduced to pitch classes (note % 12)."""
        results = []
        d = NoteDebouncer(debounce_ms=50, callback=lambda pcs: results.append(pcs))

        d.note_on(60)   # C3 (0)
        d.note_on(72)   # C4 (0) — same pitch class
        d.note_on(64)   # E3 (4)

        assert _wait_for(lambda: len(results) == 1, timeout=1.0)
        assert results[0] == frozenset({0, 4})   # C appears once

    def test_note_off_removes_note(self):
        """Releasing a note removes it from the snapshot passed to callback."""
        results = []
        d = NoteDebouncer(debounce_ms=80, callback=lambda pcs: results.append(pcs))

        d.note_on(60)
        d.note_on(64)
        d.note_off(60)  # release C; snapshot should only contain E

        assert _wait_for(lambda: len(results) == 1, timeout=1.0)
        assert results[0] == frozenset({4})
