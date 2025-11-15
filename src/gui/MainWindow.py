import tkinter
import tkinter.ttk
from gui.PianoTab import PianoTab
from gui.SettingsTab import SettingsTab
from gui.MidiTab import MidiTab
from gui.AboutTab import AboutTab
from config.Setting import Setting
from midi.MidiController import MidiController
from gui.UiDispatcher import UiDispatcher

class MainWindow():
    def __init__(self, setting: Setting, midi: MidiController):
        self.setting = setting
        self.root = tkinter.Tk()
        self.root.title("CKey")
        try:
            self.root.geometry(f"{self.setting.gui.Width}x{self.setting.gui.Height}")
        except:
            self.root.geometry("1280x400")
        self.notebook = tkinter.ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # create UI dispatcher
        self.dispatcher = UiDispatcher(self.root)
        self.dispatcher.start()

        # create tabs
        self.piano_tab = PianoTab(self.notebook, setting, midi, dispatcher=self.dispatcher)
        self.midi_tab = MidiTab(self.notebook, midi)
        self.settings_tab = SettingsTab(self.notebook, setting)
        self.about_tab = AboutTab(self.notebook)
        self.notebook.add(self.piano_tab.frame, text="Piano")
        self.notebook.add(self.midi_tab.frame, text="MIDI")
        self.notebook.add(self.settings_tab.frame, text="Settings")
        self.notebook.add(self.about_tab.frame, text="About")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def start(self):
        self.root.mainloop()

    def on_tab_changed(self, event):
        self.root.focus_set()
