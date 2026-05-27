from dataclasses import dataclass
from typing import List

from training.ChordDefinition import ChordType


@dataclass
class TrainingSettings:
    """Settings collected from TrainingTab when starting a session."""
    chord_types: List[ChordType]
    roots: List[int]
    debounce_ms: int
