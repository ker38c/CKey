import tkinter
import tkinter.ttk

from training import ChordLibrary
from training.TrainingSettings import TrainingSettings

_DEBOUNCE_MIN = 10
_DEBOUNCE_MAX = 500
_DEBOUNCE_DEFAULT = 100

_ROOT_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Mapping: display name → ChordType object
_TRIADS = [
    ("Major",      ChordLibrary.MAJOR),
    ("Minor",      ChordLibrary.MINOR),
    ("Augmented",  ChordLibrary.AUGMENTED),
    ("Diminished", ChordLibrary.DIMINISHED),
    ("sus2",       ChordLibrary.SUS2),
    ("sus4",       ChordLibrary.SUS4),
]

_SEVENTH_CHORDS = [
    ("Major 7th",       ChordLibrary.MAJOR_7TH),
    ("Minor 7th",       ChordLibrary.MINOR_7TH),
    ("Dominant 7th",    ChordLibrary.DOMINANT_7TH),
    ("Minor Major 7th", ChordLibrary.MINOR_MAJOR_7TH),
    ("Half Diminished", ChordLibrary.HALF_DIMINISHED),
    ("Diminished 7th",  ChordLibrary.DIMINISHED_7TH),
]


class TrainingTab:
    """Settings-only tab for Training Mode.

    Provides chord-type / root-note / debounce configuration.
    Does NOT start or stop training — those controls live in PianoTab.
    """

    def __init__(self, root: tkinter.ttk.Notebook) -> None:
        self.frame = tkinter.Frame(root)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # ---- Left column: chord type frames ----
        left = tkinter.Frame(self.frame)
        left.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)

        # 3-note chords
        triad_frame = tkinter.LabelFrame(left, text="Chord Types (3-note)", padx=10, pady=6)
        triad_frame.pack(fill='x', pady=(0, 6))

        self._triad_vars = []
        for label, chord_type in _TRIADS:
            var = tkinter.BooleanVar(value=True)
            cb = tkinter.Checkbutton(triad_frame, text=label, variable=var)
            cb.pack(anchor='w')
            self._triad_vars.append((var, chord_type))

        # 4-note chords
        seventh_frame = tkinter.LabelFrame(left, text="Chord Types (4-note)", padx=10, pady=6)
        seventh_frame.pack(fill='x')

        self._seventh_vars = []
        for label, chord_type in _SEVENTH_CHORDS:
            var = tkinter.BooleanVar(value=False)
            cb = tkinter.Checkbutton(seventh_frame, text=label, variable=var)
            cb.pack(anchor='w')
            self._seventh_vars.append((var, chord_type))

        # ---- Right column: root notes + debounce ----
        right = tkinter.Frame(self.frame)
        right.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)

        root_frame = tkinter.LabelFrame(right, text="Root Notes", padx=10, pady=6)
        root_frame.pack(fill='x', pady=(0, 6))

        self._root_vars = []
        for idx, name in enumerate(_ROOT_NAMES):
            var = tkinter.BooleanVar(value=True)
            row, col = divmod(idx, 3)
            cb = tkinter.Checkbutton(root_frame, text=name, variable=var, width=4)
            cb.grid(row=row, column=col, sticky='w')
            self._root_vars.append((var, idx))

        # Debounce entry
        debounce_frame = tkinter.Frame(right)
        debounce_frame.pack(fill='x', pady=(6, 0))

        tkinter.Label(debounce_frame, text="Debounce (ms):").pack(side='left')

        self._debounce_var = tkinter.StringVar(value=str(_DEBOUNCE_DEFAULT))
        self._debounce_entry = tkinter.Entry(
            debounce_frame, textvariable=self._debounce_var, width=6)
        self._debounce_entry.pack(side='left', padx=(6, 0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_settings(self) -> TrainingSettings:
        """Read the current UI settings and return a TrainingSettings instance.

        Falls back to safe defaults when no chord types or roots are selected,
        or when the debounce value is out of range.
        """
        chord_types = [ct for var, ct in self._triad_vars if var.get()]
        chord_types += [ct for var, ct in self._seventh_vars if var.get()]

        roots = [idx for var, idx in self._root_vars if var.get()]

        # Debounce validation
        try:
            debounce_ms = int(self._debounce_var.get())
            if not (_DEBOUNCE_MIN <= debounce_ms <= _DEBOUNCE_MAX):
                debounce_ms = _DEBOUNCE_DEFAULT
        except (ValueError, TypeError):
            debounce_ms = _DEBOUNCE_DEFAULT

        return TrainingSettings(chord_types=chord_types, roots=roots, debounce_ms=debounce_ms)
