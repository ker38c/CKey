import tkinter
import tkinter.ttk
from gui.PianoTab import PianoTab

class MainWindow():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("CKey")
        self.root.geometry("1280x400")
        self.notebook = tkinter.ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # create tabs
        self.piano_tab = PianoTab(self.notebook)
        self.notebook.add(self.piano_tab.frame, text="Piano")

    def start(self):
        self.root.mainloop()