import configparser
import os

MIN_WIDTH = 400
MAX_WIDTH = 4000
DEFAULT_WIDTH = 1280

MIN_HEIGHT = 200
MAX_HEIGHT = 4000
DEFAULT_HEIGHT = 400

DEFAULT_KEY_PUSHED_COLOR = "lightblue"
DEFAULT_ENABLE_MIDI_FILE = True
DEFAULT_SHOW_IMAGE_FRAME = True

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

class Setting():
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")

    def __init__(self):
        self.gui = GuiSetting()

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
            "ShowImageFrame": str(DEFAULT_SHOW_IMAGE_FRAME)
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

    def save_setting(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as file:
            self.parser["GUI"]["Width"] = str(self.gui.Width)
            self.parser["GUI"]["Height"] = str(self.gui.Height)
            self.parser["GUI"]["KeyPushedColor"] = str(self.gui.KeyPushedColor)
            self.parser["GUI"]["EnableMidiFile"] = str(self.gui.EnableMidiFile)
            self.parser["GUI"]["ImagePath"] = self.gui.ImagePath
            self.parser["GUI"]["ShowImageFrame"] = str(self.gui.ShowImageFrame)
            self.parser.write(file)
