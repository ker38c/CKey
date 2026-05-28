import configparser
import os

MIN_WIDTH = 400
MAX_WIDTH = 4000
DEFAULT_WIDTH = 1280

MIN_HEIGHT = 200
MAX_HEIGHT = 4000
DEFAULT_HEIGHT = 600

DEFAULT_KEY_PUSHED_COLOR = "lightblue"
DEFAULT_ENABLE_MIDI_FILE = True
DEFAULT_SHOW_IMAGE_FRAME = True
DEFAULT_ENABLE_TRAINING = True

# Training section defaults
DEFAULT_TRAINING_DEBOUNCE_MS = 100
TRAINING_DEBOUNCE_MIN = 10
TRAINING_DEBOUNCE_MAX = 500

def round(value, min_value, max_value):
    return max(min_value, min(value, max_value))

class GuiSetting():
    def __init__(self):
        self._width = DEFAULT_WIDTH
        self._height = DEFAULT_HEIGHT
        self._key_pushed_color = DEFAULT_KEY_PUSHED_COLOR
        self._enable_midi_file = DEFAULT_ENABLE_MIDI_FILE
        self._image_path = ""
        self._show_image_frame = DEFAULT_SHOW_IMAGE_FRAME
        self._enable_training = DEFAULT_ENABLE_TRAINING

    @property
    def Width(self):
        return self._width

    @Width.setter
    def Width(self, value):
        try:
            v = int(value)
        except Exception:
            v = DEFAULT_WIDTH

        # round to allowed range
        v = round(v, MIN_WIDTH, MAX_WIDTH)

        self._width = v

    @property
    def Height(self):
        return self._height

    @Height.setter
    def Height(self, value):
        try:
            v = int(value)
        except Exception:
            v = DEFAULT_HEIGHT

        # round to allowed range
        v = round(v, MIN_HEIGHT, MAX_HEIGHT)

        self._height = v

    @property
    def KeyPushedColor(self):
        return self._key_pushed_color

    @KeyPushedColor.setter
    def KeyPushedColor(self, value):
        # no rule yet
        self._key_pushed_color = value

    @property
    def EnableMidiFile(self):
        return self._enable_midi_file

    @EnableMidiFile.setter
    def EnableMidiFile(self, value):
        if isinstance(value, bool):
            self._enable_midi_file = value
        elif isinstance(value, str):
            self._enable_midi_file = value.lower() in ('true', '1', 'yes')
        else:
            self._enable_midi_file = bool(value)

    @property
    def ShowImageFrame(self):
        return self._show_image_frame

    @ShowImageFrame.setter
    def ShowImageFrame(self, value):
        if isinstance(value, bool):
            self._show_image_frame = value
        elif isinstance(value, str):
            self._show_image_frame = value.lower() in ('true', '1', 'yes')
        else:
            self._show_image_frame = bool(value)

    @property
    def EnableTraining(self):
        return self._enable_training

    @EnableTraining.setter
    def EnableTraining(self, value):
        if isinstance(value, bool):
            self._enable_training = value
        elif isinstance(value, str):
            self._enable_training = value.lower() in ('true', '1', 'yes')
        else:
            self._enable_training = bool(value)

    @property
    def ImagePath(self):
        return self._image_path

    @ImagePath.setter
    def ImagePath(self, value):
        if value is None:
            self._image_path = ""
            return

        if isinstance(value, bytes):
            self._image_path = self._decode_path(value)
        else:
            self._image_path = str(value)

    def _decode_path(self, value: bytes) -> str:
        """Decode bytes path from UTF-8, Shift-JIS (cp932), or fallback.

        Args:
            value (bytes): Path bytes to decode

        Returns:
            str: Decoded path string, empty string on complete failure
        """
        # Try UTF-8 first
        try:
            return value.decode('utf-8')
        except Exception:
            pass

        # Try Shift-JIS (cp932) on Windows
        try:
            return value.decode('cp932')
        except Exception:
            pass

        # Fallback: ignore problematic bytes
        try:
            return value.decode(errors='ignore')
        except Exception:
            pass

        # Complete failure: return empty string
        return ""


class TrainingSetting():
    """Holds persisted settings for the Training Mode tab."""

    def __init__(self):
        # 3-note chord toggles (triads default ON)
        self.Major: bool = True
        self.Minor: bool = True
        self.Augmented: bool = True
        self.Diminished: bool = True
        self.Sus2: bool = True
        self.Sus4: bool = True
        # 4-note chord toggles (seventh chords default OFF)
        self.Major7th: bool = False
        self.Minor7th: bool = False
        self.Dominant7th: bool = False
        self.MinorMajor7th: bool = False
        self.HalfDiminished: bool = False
        self.Diminished7th: bool = False
        # Root note toggles (all default ON)
        self.RootC: bool = True
        self.RootCSharp: bool = True
        self.RootD: bool = True
        self.RootDSharp: bool = True
        self.RootE: bool = True
        self.RootF: bool = True
        self.RootFSharp: bool = True
        self.RootG: bool = True
        self.RootGSharp: bool = True
        self.RootA: bool = True
        self.RootASharp: bool = True
        self.RootB: bool = True

        self._debounce_ms: int = DEFAULT_TRAINING_DEBOUNCE_MS

    @property
    def DebounceMs(self) -> int:
        return self._debounce_ms

    @DebounceMs.setter
    def DebounceMs(self, value):
        try:
            v = int(value)
            v = max(TRAINING_DEBOUNCE_MIN, min(v, TRAINING_DEBOUNCE_MAX))
        except Exception:
            v = DEFAULT_TRAINING_DEBOUNCE_MS
        self._debounce_ms = v


class Setting():
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

    def __init__(self):
        self.gui = GuiSetting()
        self.training = TrainingSetting()

        self.parser = configparser.ConfigParser()
        if not os.path.exists(self.CONFIG_FILE):
            self.create_default_setting()

        self.load_setting()

    def create_default_setting(self):
        self.parser["GUI"] = {
            "Width": str(DEFAULT_WIDTH),
            "Height": str(DEFAULT_HEIGHT),
            "KeyPushedColor": str(DEFAULT_KEY_PUSHED_COLOR),
            "EnableMidiFile": str(DEFAULT_ENABLE_MIDI_FILE),
            "ImagePath": "",
            "ShowImageFrame": str(DEFAULT_SHOW_IMAGE_FRAME),
            "EnableTraining": str(DEFAULT_ENABLE_TRAINING)
        }
        self.parser["Training"] = {
            "DebounceMs": str(DEFAULT_TRAINING_DEBOUNCE_MS),
        }
        self.parser["Training.ChordType"] = {
            "Major": str(True),
            "Minor": str(True),
            "Augmented": str(True),
            "Diminished": str(True),
            "Sus2": str(True),
            "Sus4": str(True),
            "Major7th": str(False),
            "Minor7th": str(False),
            "Dominant7th": str(False),
            "MinorMajor7th": str(False),
            "HalfDiminished": str(False),
            "Diminished7th": str(False),
        }
        self.parser["Training.Roots"] = {
            "C": str(True),
            "CSharp": str(True),
            "D": str(True),
            "DSharp": str(True),
            "E": str(True),
            "F": str(True),
            "FSharp": str(True),
            "G": str(True),
            "GSharp": str(True),
            "A": str(True),
            "ASharp": str(True),
            "B": str(True),
        }

        with open(self.CONFIG_FILE, mode="w", encoding="utf-8") as file:
            self.parser.write(file)

    def load_setting(self):
        self.parser.read(self.CONFIG_FILE, encoding="utf-8")
        # use properties (they will round if needed)
        self.gui.Width = self.parser["GUI"]["Width"]
        self.gui.Height = self.parser["GUI"]["Height"]
        self.gui.KeyPushedColor = self.parser["GUI"]["KeyPushedColor"]
        self.gui.EnableMidiFile = self.parser["GUI"].get("EnableMidiFile", str(DEFAULT_ENABLE_MIDI_FILE))
        self.gui.ImagePath = self.parser["GUI"].get("ImagePath", "")
        self.gui.ShowImageFrame = self.parser["GUI"].get("ShowImageFrame", str(DEFAULT_SHOW_IMAGE_FRAME))
        self.gui.EnableTraining = self.parser["GUI"].get("EnableTraining", str(DEFAULT_ENABLE_TRAINING))
        if self.parser.has_section("Training"):
            self.training.DebounceMs = self.parser["Training"].get("DebounceMs", str(DEFAULT_TRAINING_DEBOUNCE_MS))
        if self.parser.has_section("Training.ChordType"):
            ct = self.parser["Training.ChordType"]
            self.training.Major = ct.getboolean("Major", True)
            self.training.Minor = ct.getboolean("Minor", True)
            self.training.Augmented = ct.getboolean("Augmented", True)
            self.training.Diminished = ct.getboolean("Diminished", True)
            self.training.Sus2 = ct.getboolean("Sus2", True)
            self.training.Sus4 = ct.getboolean("Sus4", True)
            self.training.Major7th = ct.getboolean("Major7th", False)
            self.training.Minor7th = ct.getboolean("Minor7th", False)
            self.training.Dominant7th = ct.getboolean("Dominant7th", False)
            self.training.MinorMajor7th = ct.getboolean("MinorMajor7th", False)
            self.training.HalfDiminished = ct.getboolean("HalfDiminished", False)
            self.training.Diminished7th = ct.getboolean("Diminished7th", False)
        if self.parser.has_section("Training.Roots"):
            r = self.parser["Training.Roots"]
            self.training.RootC = r.getboolean("C", True)
            self.training.RootCSharp = r.getboolean("CSharp", True)
            self.training.RootD = r.getboolean("D", True)
            self.training.RootDSharp = r.getboolean("DSharp", True)
            self.training.RootE = r.getboolean("E", True)
            self.training.RootF = r.getboolean("F", True)
            self.training.RootFSharp = r.getboolean("FSharp", True)
            self.training.RootG = r.getboolean("G", True)
            self.training.RootGSharp = r.getboolean("GSharp", True)
            self.training.RootA = r.getboolean("A", True)
            self.training.RootASharp = r.getboolean("ASharp", True)
            self.training.RootB = r.getboolean("B", True)

    def save_setting(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as file:
            self.parser["GUI"]["Width"] = str(self.gui.Width)
            self.parser["GUI"]["Height"] = str(self.gui.Height)
            self.parser["GUI"]["KeyPushedColor"] = str(self.gui.KeyPushedColor)
            self.parser["GUI"]["EnableMidiFile"] = str(self.gui.EnableMidiFile)
            self.parser["GUI"]["ImagePath"] = self.gui.ImagePath
            self.parser["GUI"]["ShowImageFrame"] = str(self.gui.ShowImageFrame)
            self.parser["GUI"]["EnableTraining"] = str(self.gui.EnableTraining)
            if not self.parser.has_section("Training"):
                self.parser.add_section("Training")
            self.parser["Training"]["DebounceMs"] = str(self.training.DebounceMs)
            if not self.parser.has_section("Training.ChordType"):
                self.parser.add_section("Training.ChordType")
            self.parser["Training.ChordType"]["Major"] = str(self.training.Major)
            self.parser["Training.ChordType"]["Minor"] = str(self.training.Minor)
            self.parser["Training.ChordType"]["Augmented"] = str(self.training.Augmented)
            self.parser["Training.ChordType"]["Diminished"] = str(self.training.Diminished)
            self.parser["Training.ChordType"]["Sus2"] = str(self.training.Sus2)
            self.parser["Training.ChordType"]["Sus4"] = str(self.training.Sus4)
            self.parser["Training.ChordType"]["Major7th"] = str(self.training.Major7th)
            self.parser["Training.ChordType"]["Minor7th"] = str(self.training.Minor7th)
            self.parser["Training.ChordType"]["Dominant7th"] = str(self.training.Dominant7th)
            self.parser["Training.ChordType"]["MinorMajor7th"] = str(self.training.MinorMajor7th)
            self.parser["Training.ChordType"]["HalfDiminished"] = str(self.training.HalfDiminished)
            self.parser["Training.ChordType"]["Diminished7th"] = str(self.training.Diminished7th)
            if not self.parser.has_section("Training.Roots"):
                self.parser.add_section("Training.Roots")
            self.parser["Training.Roots"]["C"] = str(self.training.RootC)
            self.parser["Training.Roots"]["CSharp"] = str(self.training.RootCSharp)
            self.parser["Training.Roots"]["D"] = str(self.training.RootD)
            self.parser["Training.Roots"]["DSharp"] = str(self.training.RootDSharp)
            self.parser["Training.Roots"]["E"] = str(self.training.RootE)
            self.parser["Training.Roots"]["F"] = str(self.training.RootF)
            self.parser["Training.Roots"]["FSharp"] = str(self.training.RootFSharp)
            self.parser["Training.Roots"]["G"] = str(self.training.RootG)
            self.parser["Training.Roots"]["GSharp"] = str(self.training.RootGSharp)
            self.parser["Training.Roots"]["A"] = str(self.training.RootA)
            self.parser["Training.Roots"]["ASharp"] = str(self.training.RootASharp)
            self.parser["Training.Roots"]["B"] = str(self.training.RootB)
            self.parser.write(file)
