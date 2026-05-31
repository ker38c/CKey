from __future__ import annotations

from threading import Lock, Timer
from typing import FrozenSet, List, Optional, Tuple

from training.ChordDefinition import ChordType
from training.ChordQuestion import ChordQuestion, generate_question
from training.NoteDebouncer import NoteDebouncer

_CORRECT_DELAY: float = 1.0
_WRONG_DELAY: float = 1.5

_STATE_IDLE = 0
_STATE_WAITING = 1
_STATE_FEEDBACK = 2


def _chord_midi_notes(question: ChordQuestion) -> List[int]:
    """Return MIDI note numbers for the question's chord, anchored to octave 3 (MIDI 60 = C3)."""
    base = 60 + question.root
    return sorted(base + (pc - question.root) % 12 for pc in question.pitch_classes)


class HearingMode:
    """Core logic for Hearing training mode.

    Like ChordPlayMode, but plays the chord via MIDI so the user hears it
    and must identify it by playing back the notes.

    The question label shows ``♪ Listen...`` until feedback is given, at which
    point the chord name is revealed.

    UI targets expected in the dispatcher registry:
    - ``'training_display'``: TrainingDisplay widget
        methods: show_question(display_name), show_listen_prompt(),
                 show_score(correct, total), show_feedback_correct(),
                 show_feedback_wrong(note_names), clear_feedback(),
                 set_listen_again_enabled(enabled)
    - ``'piano_tab'``: PianoTab instance
        methods: highlight_answer_notes(key_names), clear_answer_highlights(key_names)
    """

    def __init__(self, dispatcher, handler, debounce_ms: int = 100) -> None:
        self._dispatcher = dispatcher
        self._handler = handler
        self._debounce_ms = debounce_ms
        self._lock = Lock()
        self._state: int = _STATE_IDLE
        self._current_question: Optional[ChordQuestion] = None
        self._chord_types: List[ChordType] = []
        self._roots: List[int] = []
        self._use_flat: bool = False
        self._correct: int = 0
        self._total: int = 0
        self._debouncer: Optional[NoteDebouncer] = None
        self._feedback_timer: Optional[Timer] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, chord_types: List[ChordType], roots: List[int], use_flat: bool = False) -> None:
        """Start a new training session.

        Resets the score, plays the first chord, and shows the listen prompt.
        Does nothing if a session is already active.
        """
        with self._lock:
            if self._state != _STATE_IDLE:
                return
            if not chord_types or not roots:
                return
            self._chord_types = list(chord_types)
            self._roots = list(roots)
            self._use_flat = use_flat
            self._correct = 0
            self._total = 0
            self._state = _STATE_WAITING
            self._debouncer = NoteDebouncer(self._debounce_ms, self._on_stable)

        self._next_question(None)

    def stop(self) -> None:
        """Stop the current training session and clean up timers and MIDI output."""
        with self._lock:
            self._state = _STATE_IDLE
            if self._debouncer is not None:
                self._debouncer.cancel()
                self._debouncer = None
            if self._feedback_timer is not None:
                self._feedback_timer.cancel()
                self._feedback_timer = None
        self._handler.stop_chord()

    def replay(self) -> None:
        """Replay the current chord (for the Listen Again button)."""
        with self._lock:
            if self._state != _STATE_WAITING:
                return
            question = self._current_question
        if question is not None:
            self._handler.play_chord(_chord_midi_notes(question))

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
        """Generate, play, and display the next question."""
        with self._lock:
            if self._state == _STATE_IDLE:
                return
            question = generate_question(self._chord_types, self._roots, exclude)
            self._current_question = question
            self._state = _STATE_WAITING
            if self._debouncer is not None:
                self._debouncer.reset()

        self._handler.play_chord(_chord_midi_notes(question))
        self._dispatcher.post_to('training_display', 'show_listen_prompt')

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

        chord_name = question.get_display_name(self._use_flat)

        # Reveal chord name and disable Listen Again during feedback
        self._dispatcher.post_to('training_display', 'set_listen_again_enabled', False)
        self._dispatcher.post_to('training_display', 'show_question', chord_name)
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
        self._dispatcher.post_to('training_display', 'set_listen_again_enabled', True)
        if key_names is not None:
            self._dispatcher.post_to('piano_tab', 'clear_answer_highlights', key_names)

        self._next_question(prev_question)
