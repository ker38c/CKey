from __future__ import annotations

from threading import Lock, Timer
from typing import FrozenSet, List, Optional, Tuple

from training.ChordDefinition import ChordType
from training.ChordQuestion import ChordQuestion, generate_question
from training.NoteDebouncer import NoteDebouncer

_CORRECT_DELAY: float = 1.0   # seconds before moving to next question on correct
_WRONG_DELAY: float = 1.5     # seconds before moving to next question on wrong

_STATE_IDLE = 0
_STATE_WAITING = 1
_STATE_FEEDBACK = 2


class ChordPlayMode:
    """Core logic for Chord Play training mode.

    Runs entirely in background threads; communicates with the UI exclusively
    through *dispatcher.post_to(name, method, *args)*.

    UI targets expected in the dispatcher registry:
    - ``'training_display'``: TrainingDisplay widget
        methods: show_question(display_name), show_score(correct, total),
                 show_feedback_correct(), show_feedback_wrong(note_names),
                 clear_feedback()
    - ``'piano_tab'``: PianoTab instance
        methods: highlight_answer_notes(key_names), clear_answer_highlights(key_names)
    """

    def __init__(self, dispatcher, debounce_ms: int = 100) -> None:
        self._dispatcher = dispatcher
        self._debounce_ms = debounce_ms
        self._lock = Lock()
        self._state: int = _STATE_IDLE
        self._current_question: Optional[ChordQuestion] = None
        self._chord_types: List[ChordType] = []
        self._roots: List[int] = []
        self._correct: int = 0
        self._total: int = 0
        self._debouncer: Optional[NoteDebouncer] = None
        self._feedback_timer: Optional[Timer] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, chord_types: List[ChordType], roots: List[int]) -> None:
        """Start a new training session with the given settings.

        Resets the score and generates the first question.
        Does nothing if a session is already active.
        """
        with self._lock:
            if self._state != _STATE_IDLE:
                return
            if not chord_types or not roots:
                return
            self._chord_types = list(chord_types)
            self._roots = list(roots)
            self._correct = 0
            self._total = 0
            self._state = _STATE_WAITING
            self._debouncer = NoteDebouncer(self._debounce_ms, self._on_stable)

        self._next_question(None)

    def stop(self) -> None:
        """Stop the current training session and clean up timers."""
        with self._lock:
            self._state = _STATE_IDLE
            if self._debouncer is not None:
                self._debouncer.cancel()
                self._debouncer = None
            if self._feedback_timer is not None:
                self._feedback_timer.cancel()
                self._feedback_timer = None

    def on_note_on(self, note: int) -> None:
        """Notify the mode that a MIDI note-on event was received."""
        with self._lock:
            if self._state != _STATE_WAITING or self._debouncer is None:
                return
            debouncer = self._debouncer
        debouncer.note_on(note)

    def on_note_off(self, note: int) -> None:
        """Notify the mode that a MIDI note-off event was received."""
        with self._lock:
            if self._state != _STATE_WAITING or self._debouncer is None:
                return
            debouncer = self._debouncer
        debouncer.note_off(note)

    @property
    def is_active(self) -> bool:
        """True while a training session is running."""
        with self._lock:
            return self._state != _STATE_IDLE

    @property
    def score(self) -> Tuple[int, int]:
        """Current score as (correct_count, total_count)."""
        with self._lock:
            return (self._correct, self._total)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_question(self, exclude: Optional[ChordQuestion]) -> None:
        """Generate and display the next question."""
        with self._lock:
            if self._state == _STATE_IDLE:
                return
            question = generate_question(self._chord_types, self._roots, exclude)
            self._current_question = question
            self._state = _STATE_WAITING
            if self._debouncer is not None:
                self._debouncer.reset()

        self._dispatcher.post_to('training_display', 'show_question', question.display_name)

    def _on_stable(self, pressed_pitch_classes: FrozenSet[int]) -> None:
        """Called by NoteDebouncer when the pressed set has been stable for debounce_ms."""
        with self._lock:
            if self._state != _STATE_WAITING:
                return
            question = self._current_question
            if question is None:
                return
            if len(pressed_pitch_classes) < question.chord_type.note_count:
                return  # Not enough notes yet; keep waiting.

            is_correct = (pressed_pitch_classes == question.pitch_classes)
            self._state = _STATE_FEEDBACK
            if is_correct:
                self._correct += 1
            self._total += 1
            correct_count = self._correct
            total_count = self._total
            key_names: Optional[List[str]] = None if is_correct else question.canonical_key_names
            note_names: Optional[List[str]] = None if is_correct else question.note_names

        # Post score update (always)
        self._dispatcher.post_to('training_display', 'show_score', correct_count, total_count)

        if is_correct:
            self._dispatcher.post_to('training_display', 'show_feedback_correct')
            delay = _CORRECT_DELAY
        else:
            self._dispatcher.post_to('training_display', 'show_feedback_wrong', note_names)
            self._dispatcher.post_to('piano_tab', 'highlight_answer_notes', key_names)
            delay = _WRONG_DELAY

        with self._lock:
            t = Timer(delay, self._on_feedback_timeout, args=(question, key_names))
            self._feedback_timer = t
        t.start()

    def _on_feedback_timeout(
        self, prev_question: ChordQuestion, key_names: Optional[List[str]]
    ) -> None:
        """Called after the feedback display period ends."""
        with self._lock:
            self._feedback_timer = None
            if self._state != _STATE_FEEDBACK:
                return

        self._dispatcher.post_to('training_display', 'clear_feedback')
        if key_names is not None:
            self._dispatcher.post_to('piano_tab', 'clear_answer_highlights', key_names)

        self._next_question(prev_question)
