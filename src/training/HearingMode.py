from __future__ import annotations

from typing import List

from training.ChordQuestion import ChordQuestion
from training.TrainingMode import TrainingMode, _STATE_WAITING


def _chord_midi_notes(question: ChordQuestion) -> List[int]:
    """Return MIDI note numbers for the question's chord, anchored to octave 3 (MIDI 60 = C3)."""
    base = 60 + question.root
    return sorted(base + (pc - question.root) % 12 for pc in question.pitch_classes)


class HearingMode(TrainingMode):
    """Training mode where the user hears a chord and must identify it by playing back the notes.

    Extends TrainingMode with chord playback via MIDI and a Listen Again button.

    Additional UI contract on ``'training_display'``:
        show_listen_prompt(), set_listen_again_enabled(enabled)
    """

    def __init__(self, dispatcher, handler, debounce_ms: int = 100) -> None:
        super().__init__(dispatcher, debounce_ms)
        self._handler = handler

    # ------------------------------------------------------------------
    # Public API (extension)
    # ------------------------------------------------------------------

    def replay(self) -> None:
        """Replay the current chord (for the Listen Again button)."""
        with self._lock:
            if self._state != _STATE_WAITING:
                return
            question = self._current_question
        if question is not None:
            self._handler.play_chord(_chord_midi_notes(question))

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def _on_question_ready(self, question: ChordQuestion) -> None:
        self._handler.play_chord(_chord_midi_notes(question))
        self._dispatcher.post_to('training_display', 'show_listen_prompt')

    def _on_stop(self) -> None:
        self._handler.stop_chord()

    def _before_feedback(self, is_correct: bool, question: ChordQuestion) -> None:
        chord_name = question.get_display_name(self._use_flat)
        self._dispatcher.post_to('training_display', 'set_listen_again_enabled', False)
        self._dispatcher.post_to('training_display', 'show_question', chord_name)

    def _after_feedback_clear(self) -> None:
        self._dispatcher.post_to('training_display', 'set_listen_again_enabled', True)

