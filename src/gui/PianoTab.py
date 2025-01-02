import tkinter
import tkinter.ttk
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting):
        self.frame = tkinter.Frame(root)

        self.keyboard = KeyBoard(master=self.frame, setting=setting)
        self.keyboard.grid(row=0, column=0, columnspan=4)
