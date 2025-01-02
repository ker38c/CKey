import tkinter
import tkinter.ttk
from gui.piano.KeyBoard import KeyBoard

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook):
        self.frame = tkinter.Frame(root)

        self.keyboard = KeyBoard(self.frame)
        self.keyboard.grid(row=0, column=0, columnspan=4)
