import tkinter
import tkinter.ttk

from training import ChordLibrary
from training.TrainingSettings import TrainingSettings

_DEBOUNCE_MIN = 10
_DEBOUNCE_MAX = 500
_DEBOUNCE_DEFAULT = 100

_ROOT_NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_ROOT_NAMES_FLAT  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

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

# Maps ChordType.name → TrainingSetting attribute name
_CHORD_NAME_TO_ATTR = {
    "Major":           "Major",
    "Minor":           "Minor",
    "Augmented":       "Augmented",
    "Diminished":      "Diminished",
    "sus2":            "Sus2",
    "sus4":            "Sus4",
    "Major 7th":       "Major7th",
    "Minor 7th":       "Minor7th",
    "Dominant 7th":    "Dominant7th",
    "Minor Major 7th": "MinorMajor7th",
    "Half Diminished": "HalfDiminished",
    "Diminished 7th":  "Diminished7th",
}

# Maps root pitch class (0–11) → TrainingSetting attribute name
_ROOT_IDX_TO_ATTR = {
    0:  "RootC",
    1:  "RootCSharp",
    2:  "RootD",
    3:  "RootDSharp",
    4:  "RootE",
    5:  "RootF",
    6:  "RootFSharp",
    7:  "RootG",
    8:  "RootGSharp",
    9:  "RootA",
    10: "RootASharp",
    11: "RootB",
}


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

        # Sharp / Flat notation toggle
        notation_bar = tkinter.Frame(root_frame)
        notation_bar.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 4))
        self._use_flat_var = tkinter.BooleanVar(value=False)
        tkinter.Radiobutton(
            notation_bar, text="#", variable=self._use_flat_var,
            value=False, command=self._on_notation_changed,
        ).pack(side='left')
        tkinter.Radiobutton(
            notation_bar, text="b", variable=self._use_flat_var,
            value=True, command=self._on_notation_changed,
        ).pack(side='left')

        self._root_vars = []
        self._root_checkbuttons = []
        for idx, name in enumerate(_ROOT_NAMES_SHARP):
            var = tkinter.BooleanVar(value=True)
            row, col = divmod(idx, 3)
            cb = tkinter.Checkbutton(root_frame, text=name, variable=var, width=4)
            cb.grid(row=row + 1, column=col, sticky='w')
            self._root_vars.append((var, idx))
            self._root_checkbuttons.append(cb)

        # Debounce entry
        debounce_frame = tkinter.Frame(right)
        debounce_frame.pack(fill='x', pady=(6, 0))

        tkinter.Label(debounce_frame, text="Debounce (ms):").pack(side='left')

        self._debounce_var = tkinter.StringVar(value=str(_DEBOUNCE_DEFAULT))
        self._debounce_entry = tkinter.Entry(
            debounce_frame, textvariable=self._debounce_var, width=6)
        self._debounce_entry.pack(side='left', padx=(6, 0))

        # Save button
        save_frame = tkinter.Frame(self.frame)
        save_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        self._btn_save = tkinter.ttk.Button(save_frame, text="Save", command=self._on_save_clicked)
        self._btn_save.pack()

        self._save_callback = None

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

        return TrainingSettings(
            chord_types=chord_types,
            roots=roots,
            debounce_ms=debounce_ms,
            use_flat=self._use_flat_var.get(),
        )

    def set_save_callback(self, callback) -> None:
        """Register a callback to invoke when the Save button is clicked."""
        self._save_callback = callback

    def load_from_setting(self, training_setting) -> None:
        """Populate the UI checkboxes and debounce field from a persisted TrainingSetting."""
        for var, chord_type in self._triad_vars + self._seventh_vars:
            attr = _CHORD_NAME_TO_ATTR.get(chord_type.name)
            if attr is not None:
                var.set(getattr(training_setting, attr))

        for var, idx in self._root_vars:
            attr = _ROOT_IDX_TO_ATTR.get(idx)
            if attr is not None:
                var.set(getattr(training_setting, attr))

        self._use_flat_var.set(training_setting.UseFlat)
        self._apply_notation_labels()

        self._debounce_var.set(str(training_setting.DebounceMs))

    def save_to_setting(self, training_setting) -> None:
        """Write the current UI state back to a TrainingSetting instance."""
        for var, chord_type in self._triad_vars + self._seventh_vars:
            attr = _CHORD_NAME_TO_ATTR.get(chord_type.name)
            if attr is not None:
                setattr(training_setting, attr, var.get())

        for var, idx in self._root_vars:
            attr = _ROOT_IDX_TO_ATTR.get(idx)
            if attr is not None:
                setattr(training_setting, attr, var.get())

        training_setting.UseFlat = self._use_flat_var.get()

        try:
            training_setting.DebounceMs = int(self._debounce_var.get())
        except Exception:
            training_setting.DebounceMs = _DEBOUNCE_DEFAULT

    def _on_notation_changed(self) -> None:
        """Update checkbox labels when the sharp/flat toggle changes."""
        self._apply_notation_labels()

    def _apply_notation_labels(self) -> None:
        """Set checkbox text to sharp or flat names based on the current toggle."""
        names = _ROOT_NAMES_FLAT if self._use_flat_var.get() else _ROOT_NAMES_SHARP
        for cb, (_, idx) in zip(self._root_checkbuttons, self._root_vars):
            cb.config(text=names[idx])

    def _on_save_clicked(self) -> None:
        if self._save_callback is not None:
            self._save_callback()
