import tkinter
from config.Setting import Setting
from .Key import Key, WhiteKey, BlackKey
from .CatPawPedalButton import CatPawPedalButton

class KeyBoard(tkinter.Frame):

    WHITE_KEY_NAME = [
        ["A-1", "B-1"],
        ["C0", "D0", "E0", "F0", "G0", "A0", "B0"],
        ["C1", "D1", "E1", "F1", "G1", "A1", "B1"],
        ["C2", "D2", "E2", "F2", "G2", "A2", "B2"],
        ["C3", "D3", "E3", "F3", "G3", "A3", "B3"],
        ["C4", "D4", "E4", "F4", "G4", "A4", "B4"],
        ["C5", "D5", "E5", "F5", "G5", "A5", "B5"],
        ["C6", "D6", "E6", "F6", "G6", "A6", "B6"],
        ["C7"]
    ]
    BLACK_KEY_NAME = [
        ["A#-1", ""],
        ["C#0", "D#0", "", "F#0", "G#0", "A#0", ""],
        ["C#1", "D#1", "", "F#1", "G#1", "A#1", ""],
        ["C#2", "D#2", "", "F#2", "G#2", "A#2", ""],
        ["C#3", "D#3", "", "F#3", "G#3", "A#3", ""],
        ["C#4", "D#4", "", "F#4", "G#4", "A#4", ""],
        ["C#5", "D#5", "", "F#5", "G#5", "A#5", ""],
        ["C#6", "D#6", "", "F#6", "G#6", "A#6", ""],
    ]

    def __init__(self, master=None, setting: Setting=None, midi=None, **kargs):
        super().__init__(master=master, **kargs)

        self.setting = setting
        self.midi = midi

        self.white_keys = [WhiteKey(self, name=key, setting=setting, midi=self.midi) for octabe in self.WHITE_KEY_NAME for key in octabe]
        self.black_keys = [BlackKey(self, name=key, setting=setting, midi=self.midi) for octabe in self.BLACK_KEY_NAME for key in octabe]
        self.keys = self.white_keys + self.black_keys

        self.sustain = CatPawPedalButton(self, setting=setting)

        self.resize_keyboard(self.setting.gui.Width, self.setting.gui.Height)

    def get_white_key_num(self)->int:
        num_white_key = 0
        for i, keys in enumerate(self.WHITE_KEY_NAME):
            num_white_key += len(keys)
        return num_white_key

    def find_key(self, name: str)->Key:
        if name == "":
            return None
        for key in self.keys:
            if name == key.name:
                return key
        print("No such a key")
        return None

    def _safe_configure_key(self, key, state: str, key_name: str = None) -> bool:
        """Safely configure a key state with error handling
        
        Args:
            key: The key widget to configure
            state (str): The state to set
            key_name (str): Optional name for error message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key.config(state=state)
            return True
        except Exception as e:
            if key_name:
                print(f"Error setting {key_name} state: {e}")
            else:
                print(f"Error configuring key state: {e}")
            return False

    def set_key_state(self, name: str, state: str):
        key = self.find_key(name)
        if key is None:
            return
        self._safe_configure_key(key, state, key_name=name)

    def set_sustain(self, pressed: bool):
        state = tkinter.ACTIVE if pressed else tkinter.NORMAL
        self._safe_configure_key(self.sustain, state, key_name="sustain")

    def _calculate_dimensions(self, width: int):
        """Calculate and store key and pedal dimensions based on width."""
        self.setting.gui.Width = width
        self.KEY_WIDTH = int(width / self.get_white_key_num())
        self.KEY_HEIGHT = self.KEY_WIDTH * 5
        self.PEDAL_WIDTH = self.KEY_WIDTH * 3
        self.PEDAL_HEIGHT = self.KEY_WIDTH * 3
        self.BLACK_KEY_WIDTH = self.KEY_WIDTH / 2
        self.BLACK_KEY_HEIGHT = self.KEY_HEIGHT * 0.6
        self.width = width
        self.height = self.KEY_HEIGHT + self.PEDAL_HEIGHT

    def _update_frame_size(self):
        """Apply calculated dimensions to the frame."""
        self.config(width=self.width, height=self.height)

    def _place_keyboard(self):
        # Place white key
        for i, key in enumerate(self.white_keys):
            key.place(x=i * self.KEY_WIDTH, y=0, width=self.KEY_WIDTH, height=self.KEY_HEIGHT)

        # Place black key
        for i, key in enumerate(self.black_keys):
            if key.name == "":
                continue
            key.place(x=i * self.KEY_WIDTH + self.BLACK_KEY_WIDTH * 1.5, y=0, width=self.BLACK_KEY_WIDTH, height=self.BLACK_KEY_HEIGHT)

        # Place sustain pedal
        self.sustain.place(x=self.setting.gui.Width / 2, y=self.KEY_HEIGHT, width=self.PEDAL_WIDTH, height=self.PEDAL_HEIGHT)

    def resize_keyboard(self, width: int, height: int):
        """Resize the keyboard with the given width and height

        Args:
            width (int): The new width of the keyboard (in pixels)
            height (int): The new height of the keyboard (in pixels)
            Note: height is currently unused; dimensions derive from width.
        """
        self._calculate_dimensions(width)
        self._update_frame_size()
        self._place_keyboard()
