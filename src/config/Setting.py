import configparser
import os

MIN_WIDTH = 400
MAX_WIDTH = 4000
DEFAULT_WIDTH = 1280

MIN_HEIGHT = 200
MAX_HEIGHT = 4000
DEFAULT_HEIGHT = 400

DEFAULT_KEY_PUSHED_COLOR = "yellow"

def round(value, min_value, max_value):
    return max(min_value, min(value, max_value))

class GuiSetting():
    def __init__(self):
        self._width = 0
        self._height = 0
        self._key_pushed_color = ""

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
            "KeyPushedColor": str(DEFAULT_KEY_PUSHED_COLOR)
        }

        with open(self.CONFIG_FILE, mode="w") as file:
            self.parser.write(file)

    def load_setting(self):
        self.parser.read(self.CONFIG_FILE, encoding="utf-8")
        # use properties (they will round if needed)
        self.gui.Width = self.parser["GUI"]["Width"]
        self.gui.Height = self.parser["GUI"]["Height"]
        self.gui.KeyPushedColor = self.parser["GUI"]["KeyPushedColor"]

    def save_setting(self):
        with open(self.CONFIG_FILE, 'w') as file:
            self.parser["GUI"]["Width"] = str(self.gui.Width)
            self.parser["GUI"]["Height"] = str(self.gui.Height)
            self.parser["GUI"]["KeyPushedColor"] = str(self.gui.KeyPushedColor)
            self.parser.write(file)
