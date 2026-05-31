from __future__ import annotations

from training.ChordQuestion import ChordQuestion
from training.TrainingMode import TrainingMode


class ChordPlayMode(TrainingMode):
    """Training mode where the user reads a chord name and plays it on the keyboard."""

    def _on_question_ready(self, question: ChordQuestion) -> None:
        self._dispatcher.post_to(
            'training_display', 'show_question', question.get_display_name(self._use_flat)
        )

