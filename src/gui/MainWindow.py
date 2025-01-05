import tkinter
import tkinter.ttk
from gui.PianoTab import PianoTab
from config.Setting import Setting
from midi.MidiController import MidiController
class MainWindow():
    def __init__(self, setting: Setting, midi: MidiController):
        self.setting = setting
        self.root = tkinter.Tk()
        self.root.title("CKey")
        self.root.geometry(f"{self.setting.gui.Width}x{self.setting.gui.Height}")
        self.notebook = tkinter.ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # create tabs
        self.piano_tab = PianoTab(self.notebook, setting, midi)
        self.notebook.add(self.piano_tab.frame, text="Piano")

    def start(self):
        self.root.mainloop()