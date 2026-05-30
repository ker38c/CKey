from __future__ import annotations

from threading import Lock, Timer
from typing import Callable, FrozenSet, Optional


class NoteDebouncer:
    """Debounces a stream of note-on / note-off events.

    After *debounce_ms* milliseconds of silence (no note-on or note-off),
    the *callback* is invoked with a frozenset of the currently pressed
    pitch classes (note % 12).

    All public methods are thread-safe.
    """

    def __init__(self, debounce_ms: int, callback: Callable[[FrozenSet[int]], None]) -> None:
        self._debounce_s: float = max(1, debounce_ms) / 1000.0
        self._callback = callback
        self._lock = Lock()
        self._pressed: set = set()
        self._timer: Optional[Timer] = None

    def note_on(self, note: int) -> None:
        """Register a note-on event and restart the debounce timer."""
        with self._lock:
            self._pressed.add(note)
            self._reset_timer()

    def note_off(self, note: int) -> None:
        """Register a note-off event and restart the debounce timer."""
        with self._lock:
            self._pressed.discard(note)
            self._reset_timer()

    def cancel(self) -> None:
        """Cancel the pending timer without firing the callback."""
        with self._lock:
            self._cancel_timer()

    def reset(self) -> None:
        """Clear pressed notes and cancel the pending timer."""
        with self._lock:
            self._pressed.clear()
            self._cancel_timer()

    # ------------------------------------------------------------------
    # Internal helpers (must be called while holding self._lock)
    # ------------------------------------------------------------------

    def _reset_timer(self) -> None:
        self._cancel_timer()
        snapshot: FrozenSet[int] = frozenset(p % 12 for p in self._pressed)
        t = Timer(self._debounce_s, self._on_timeout, args=(snapshot,))
        self._timer = t
        t.start()

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _on_timeout(self, snapshot: FrozenSet[int]) -> None:
        with self._lock:
            self._timer = None
        self._callback(snapshot)
