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
    def __init__(self, setting: Setting, midi: MidiController, file_player=None):
        self.setting = setting
        self.file_player = file_player
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
        self.piano_tab = PianoTab(self.notebook, setting, midi, file_player, dispatcher=self.dispatcher)
        self.midi_tab = MidiTab(self.notebook, midi)
        self.settings_tab = SettingsTab(self.notebook, setting, self)
        self.about_tab = AboutTab(self.notebook)
        self.notebook.add(self.piano_tab.frame, text="Piano")
        self.notebook.add(self.midi_tab.frame, text="MIDI")
        self.notebook.add(self.settings_tab.frame, text="Settings")
        self.notebook.add(self.about_tab.frame, text="About")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def resize(self, width: int, height: int):
        """Resize the main window."""
        self.root.geometry(f"{width}x{height}")

    def apply_window_size(self, width: int, height: int):
        """Apply window size changes to main window and keyboard."""
        self.resize(width, height)
        self.piano_tab.resize_keyboard(width, height)

    def update_midi_file_visibility(self):
        """Update MIDI file controls visibility."""
        self.piano_tab.update_midi_file_visibility()

    def start(self):
        self.root.mainloop()

    def on_tab_changed(self, event):
        self.root.focus_set()
        try:
            current = self.notebook.nametowidget(self.notebook.select())
            if current is self.piano_tab.frame:
                self.piano_tab.refresh_image()
        except Exception:
            pass
