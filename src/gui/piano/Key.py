import tkinter
from config.Setting import Setting


class Key(tkinter.Button):
    def __init__(self, master=None, name: str="", setting: Setting=None, midi=None, **kargs):
        super().__init__(master=master, **kargs)
        self.config(activebackground=setting.gui.KeyPushedColor)
        self.name = name
        self.midi = midi
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_press(self, event):
        if self.midi:
            self.midi.add_key_event(self.name, True)

    def _on_release(self, event):
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
