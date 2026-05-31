from dataclasses import dataclass, field
from typing import List

from training.ChordDefinition import ChordType
from training.TrainingMode import TrainingMode


@dataclass
class TrainingSettings:
    """Settings collected from TrainingTab when starting a session."""
    chord_types: List[ChordType]
    roots: List[int]
    debounce_ms: int
    use_flat: bool = False
    mode: TrainingMode = TrainingMode.CHORD_PLAY
