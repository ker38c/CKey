import tkinter
import tkinter.ttk
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController, dispatcher=None):
        self.frame = tkinter.Frame(root)

        self.keyboard = KeyBoard(master=self.frame, setting=setting, midi=midi)
        self.keyboard.grid(row=0, column=0)
        # Register keyboard with dispatcher for name-based calls
        if dispatcher is not None:
            try:
                dispatcher.register('keyboard', self.keyboard)
            except Exception:
                pass
