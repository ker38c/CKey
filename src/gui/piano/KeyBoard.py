import tkinter
from tkinter import Canvas
from config.Setting import Setting
class Key(tkinter.Button):
    def __init__(self, master=None, name: str="", setting: Setting=None, midi=None, **kargs):
        super().__init__(master=master, **kargs)
        self.config(activebackground=setting.gui.KeyPushedColor)
        self.name = name
        self.midi = midi
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)

    def on_press(self, event):
        if self.midi:
            self.midi.add_key_event(self.name, True)

    def on_release(self, event):
        if self.midi:
            self.midi.add_key_event(self.name, False)

class WhiteKey(Key):
    def __init__(self, master=None, name: str="", setting: Setting=None, midi=None, **kargs):
        super().__init__(master=master, name=name, setting=setting, midi=midi, **kargs)
        self.config(background="white")

class BlackKey(Key):
    def __init__(self, master=None, name: str="", setting: Setting=None, midi=None, **kargs):
        super().__init__(master=master, name=name, setting=setting, midi=midi, **kargs)
        self.config(background="black")

class CatPawPedalButton(tkinter.Frame):
    """Sustain pedal button shaped like a cat paw print"""
    def __init__(self, master=None, setting: Setting=None, **kargs):
        super().__init__(master=master, **kargs)
        self.setting = setting
        self.is_pressed = False

        # Draw paw print with canvas
        self.canvas = Canvas(self)
        self.canvas.config(highlightthickness=1)
        self.canvas.config(highlightbackground="black")
        self.canvas.config(bg="white")
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Configure>', self.on_configure)

        self._draw_paw()

    def _draw_paw(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            width = 100
            height = 100

        # Determine the color of paw print
        color = self.setting.gui.KeyPushedColor if self.is_pressed else "white"
        outline_color = "black"

        # Large paw pad (Center)
        pad_size = min(width, height) / 3
        pad_rad = pad_size / 2
        center_x = width / 2
        center_y = height / 2

        self.canvas.create_oval(
            center_x - pad_rad,
            center_y - pad_rad,
            center_x + pad_rad,
            center_y + pad_rad,
            fill=color,
            outline=None,
            width=0
        )
        self.canvas.create_oval(
            center_x + pad_size,
            center_y + pad_size,
            center_x,
            center_y,
            fill=color,
            outline=None,
            width=0
        )
        self.canvas.create_oval(
            center_x,
            center_y + pad_size,
            center_x - pad_size,
            center_y,
            fill=color,
            outline=None,
            width=0
        )


        # Small paw pad (Left)
        self.canvas.create_oval(
            pad_rad,
            pad_size,
            0,
            center_y + pad_rad,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Left Top)
        self.canvas.create_oval(
            center_x - pad_rad / 2,
            0,
            pad_rad * 1.5,
            pad_size,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Right Top)
        self.canvas.create_oval(
            center_x + 1.5 * pad_rad,
            0,
            center_x + pad_rad / 2,
            pad_size,
            fill=color,
            outline=outline_color,
            width=0
        )

        # Small paw pad (Right)
        self.canvas.create_oval(
            center_x + pad_size * 1.5,
            pad_size,
            center_x + pad_size,
            center_y + pad_rad,
            fill=color,
            outline=outline_color,
            width=0
        )

    def on_press(self, event):
        self.is_pressed = True
        self._draw_paw()

    def on_release(self, event):
        self.is_pressed = False
        self._draw_paw()

    def on_configure(self, event):
        """Redraw paw print when resizing button"""
        self._draw_paw()

    def config(self, **kwargs):
        """Override config to handle state changes"""
        if 'state' in kwargs:
            state = kwargs.pop('state')
            self.is_pressed = (state == tkinter.ACTIVE)
            self._draw_paw()
        super().config(**kwargs)

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

        # Resize frame to total keyboard width
        self.setting = setting
        self.midi = midi

        self.KEY_WIDTH = int(self.setting.gui.Width / self.get_white_key_num())
        self.KEY_HEIGHT = self.KEY_WIDTH * 5
        self.PEDAL_WIDTH = self.KEY_WIDTH * 3
        self.PEDAL_HEIGHT = self.KEY_WIDTH * 3
        self.BLACK_KEY_WIDTH = self.KEY_WIDTH / 2
        self.BLACK_KEY_HEIGHT = self.KEY_HEIGHT * 0.6

        self.config(width=self.KEY_WIDTH * self.get_white_key_num(), height=self.KEY_HEIGHT + self.PEDAL_HEIGHT)

        self.white_keys = [WhiteKey(self, name=key, setting=setting, midi=self.midi) for octabe in self.WHITE_KEY_NAME for key in octabe]
        self.black_keys = [BlackKey(self, name=key, setting=setting, midi=self.midi) for octabe in self.BLACK_KEY_NAME for key in octabe]
        self.keys = self.white_keys + self.black_keys

        self.sustain = CatPawPedalButton(self, setting=setting)

        self.place_keyboard()

    def get_white_key_num(self)->int:
        num_white_key = 0
        for i, keys in enumerate(self.WHITE_KEY_NAME):
            num_white_key += len(keys)
        return num_white_key

    def place_keyboard(self):
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

    def find_key(self, name: str)->Key:
        if name == "":
            return None
        for key in self.keys:
            if name == key.name:
                return key
        print("No such a key")
        return None

    def set_key_state(self, name: str, state: str):
        key = self.find_key(name)
        if key is None:
            return
        try:
            key.config(state=state)
        except Exception as e:
            print(f"Error setting key state for {name}: {e}")

    def set_sustain(self, pressed: bool):
        try:
            state = tkinter.ACTIVE if pressed else tkinter.NORMAL
            self.sustain.config(state=state)
        except Exception as e:
            print(f"Error setting sustain state: {e}")
