import tkinter
import tkinter.ttk
from typing import Optional, Union
from gui.PianoTab import PianoTab
from gui.SettingsTab import SettingsTab
from gui.MidiTab import MidiTab
from gui.AboutTab import AboutTab
from gui.TrainingTab import TrainingTab
from gui.TrainingDisplay import TrainingDisplay
from config.Setting import Setting
from midi.MidiController import MidiController
from gui.UiDispatcher import UiDispatcher
from training.ChordPlayMode import ChordPlayMode
from training.HearingMode import HearingMode
from training.SessionMode import SessionMode

class MainWindow():
    def __init__(self, root: tkinter.Tk, setting: Setting, midi: MidiController, file_player, dispatcher: UiDispatcher):

        self.setting = setting
        self.file_player = file_player
        self.root = root
        self.dispatcher = dispatcher
        self.midi = midi
        self.root.title("CKey")
        try:
            self.root.geometry(f"{self.setting.gui.Width}x{self.setting.gui.Height}")
        except:
            self.root.geometry("1280x400")
        self.notebook = tkinter.ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # create tabs
        self.piano_tab = PianoTab(self.notebook, setting, midi, file_player, dispatcher=self.dispatcher)
        self.midi_tab = MidiTab(self.notebook, midi)
        self.training_tab = TrainingTab(self.notebook)
        self.training_tab.load_from_setting(self.setting.training)
        self.training_tab.set_save_callback(self._on_training_settings_save)
        self.settings_tab = SettingsTab(self.notebook, setting, self)
        self.about_tab = AboutTab(self.notebook)
        self.notebook.add(self.piano_tab.frame, text="Piano")
        self.notebook.add(self.midi_tab.frame, text="MIDI")
        self.notebook.add(self.training_tab.frame, text="Training")
        self.notebook.add(self.settings_tab.frame, text="Settings")
        self.notebook.add(self.about_tab.frame, text="About")

        # Training mode coordinator
        self._active_mode: Optional[Union[ChordPlayMode, HearingMode]] = None
        self.piano_tab.set_training_callback(self._on_training_button_clicked)

        # Register TrainingDisplay with dispatcher
        self.dispatcher.register('training_display', self.piano_tab._training_display)

        # Apply visibility preferences on startup
        self.update_image_frame_visibility()
        self.update_training_button_visibility()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def start(self):
        self.root.mainloop()

    def apply_window_size(self, width: int, height: int):
        """Apply window size changes to main window and keyboard."""
        self._resize(width, height)
        self.piano_tab.resize_keyboard(width, height)

    def update_midi_file_visibility(self):
        """Update MIDI file controls visibility."""
        self.piano_tab.update_midi_file_visibility()

    def update_image_frame_visibility(self):
        """Update image frame visibility."""
        self.piano_tab.update_image_frame_visibility()

    def update_training_button_visibility(self) -> None:
        """Update Training button visibility; stop training if the button is now hidden."""
        if not self.setting.gui.EnableTraining and self._active_mode is not None and self._active_mode.is_active:
            self.on_stop_training()
        self.piano_tab.update_training_button_visibility()

    def _resize(self, width: int, height: int):
        """Resize the main window."""
        self.root.geometry(f"{width}x{height}")

    def _on_tab_changed(self, event):
        self.root.focus_set()
        try:
            current = self.notebook.nametowidget(self.notebook.select())
            if current is self.piano_tab.frame:
                self.piano_tab.refresh_image()
            else:
                # Stop training when navigating away from Piano tab
                if self._active_mode is not None and self._active_mode.is_active:
                    self.on_stop_training()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Training mode coordination
    # ------------------------------------------------------------------

    def _on_training_button_clicked(self, is_starting: bool) -> None:
        if is_starting:
            self.on_start_training()
        else:
            self.on_stop_training()

    def _on_training_settings_save(self) -> None:
        """Persist current TrainingTab settings to config file."""
        self.training_tab.save_to_setting(self.setting.training)
        self.setting.save_setting()

    def on_start_training(self) -> None:
        """Start a training session (Chord Play or Hearing) based on current settings."""
        settings = self.training_tab.get_settings()
        if not settings.chord_types or not settings.roots:
            return

        # Pause MIDI file playback if active
        if self.file_player is not None and self.file_player.is_playing():
            try:
                self.file_player.pause()
            except Exception:
                pass

        if settings.mode == SessionMode.HEARING:
            mode = HearingMode(self.dispatcher, self.midi.handler, settings.debounce_ms)
            self._active_mode = mode
            # Configure Listen Again button
            self.piano_tab._training_display.set_listen_again_callback(mode.replay)
            self.piano_tab._training_display.set_listen_again_visible(True)
            self.piano_tab._training_display.set_listen_again_enabled(True)
        else:
            mode = ChordPlayMode(self.dispatcher, settings.debounce_ms)
            self._active_mode = mode

        # Register observer with MidiHandler
        try:
            self.midi.handler.set_training_observer(self._active_mode)
        except Exception:
            pass

        # Update Piano tab UI
        self.piano_tab.set_midi_playback_enabled(False)
        self.piano_tab.show_training_display()
        self.piano_tab.set_training_button_mode(True)

        # Start the mode
        self._active_mode.start(settings.chord_types, settings.roots, settings.use_flat)

    def on_stop_training(self) -> None:
        """Stop the current training session."""
        if self._active_mode is not None:
            self._active_mode.stop()

        # Unregister observer
        try:
            self.midi.handler.set_training_observer(None)
        except Exception:
            pass

        # Hide Listen Again button
        self.piano_tab._training_display.set_listen_again_visible(False)

        # Restore Piano tab UI
        self.piano_tab.set_midi_playback_enabled(True)
        self.piano_tab.hide_training_display()
        self.piano_tab.set_training_button_mode(False)
        self.piano_tab._training_display.reset()

        self._active_mode = None
