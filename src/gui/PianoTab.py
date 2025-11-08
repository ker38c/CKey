import tkinter
import tkinter.ttk
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController):
        self.frame = tkinter.Frame(root)

        self.keyboard = KeyBoard(master=self.frame, setting=setting, midi=midi)
        self.keyboard.grid(row=0, column=0)
