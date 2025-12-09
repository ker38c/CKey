import tkinter
import tkinter.ttk
from config.Setting import Setting

class SettingsTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, keyboard, piano_tab):
        self.frame = tkinter.Frame(root)
        self.setting = setting
        self.keyboard = keyboard
        self.piano_tab = piano_tab

        self.label_window = tkinter.Label(self.frame, text="Window settings")
        self.label_window.grid(row=0, column=0)

        # window width
        self.label_width = tkinter.Label(self.frame, text="Window width")
        self.label_width.grid(row=1, column=0)

        self.text_width = tkinter.StringVar()
        self.text_width.set(str(setting.gui.Width))
        self.entry_width = tkinter.Entry(self.frame, textvariable=self.text_width)
        self.entry_width.grid(row=1, column=1)
        self.entry_width.bind("<FocusOut>", self._on_width_key)

        # window height
        self.label_height = tkinter.Label(self.frame, text="Window height")
        self.label_height.grid(row=2, column=0)

        self.text_height = tkinter.StringVar()
        self.text_height.set(str(setting.gui.Height))
        self.entry_height = tkinter.Entry(self.frame, textvariable=self.text_height)
        self.entry_height.grid(row=2, column=1)
        self.entry_height.bind("<FocusOut>", self._on_height_key)

        # key pushed color
        self.label_key_pushed_coler = tkinter.Label(self.frame, text="Key pushed color")
        self.label_key_pushed_coler.grid(row=3, column=0)

        self.text_key_pushed_color = tkinter.StringVar()
        self.text_key_pushed_color.set(setting.gui.KeyPushedColor)
        self.entry_key_pushed_color = tkinter.Entry(self.frame, textvariable=self.text_key_pushed_color)
        self.entry_key_pushed_color.bind("<FocusOut>", self.on_color_updated)
        self.entry_key_pushed_color.grid(row=3, column=1)

        # color indicator
        self.label_color_box = tkinter.Label(self.frame, width=2, bg=setting.gui.KeyPushedColor)
        self.label_color_box.grid(row=3, column=2)

        # MIDI file player toggle
        self.label_midi_file = tkinter.Label(self.frame, text="Enable MIDI file player")
        self.label_midi_file.grid(row=4, column=0)

        self.var_enable_midi_file = tkinter.BooleanVar()
        self.var_enable_midi_file.set(setting.gui.EnableMidiFile)
        self.check_midi_file = tkinter.Checkbutton(self.frame, variable=self.var_enable_midi_file, command=self._on_enable_midi_file_changed)
        self.check_midi_file.grid(row=4, column=1)

        self.button_apply = tkinter.Button(self.frame, text="Save", command=self._on_save_button_click)
        self.button_apply.grid(row=5, column=1)

    def _on_save_button_click(self):
        self.entry_width.event_generate("<FocusOut>")
        self.entry_height.event_generate("<FocusOut>")
        self.entry_key_pushed_color.event_generate("<FocusOut>")

        self.apply_setting()

    def apply_setting(self):
        self.setting.save_setting()
        # Apply keyboard size changes if keyboard is available
        self.keyboard.resize_keyboard(self.setting.gui.Width, self.setting.gui.Height)
        # Update MIDI file controls visibility
        self.piano_tab._update_midi_file_visibility()


    def _on_width_key(self, event):
        try:
            self.setting.gui.Width = self.text_width.get()
            # Set the rounded value from Setting to text_width
            self.text_width.set(str(self.setting.gui.Width))
        except:
            pass

    def _on_height_key(self, event):
        try:
            self.setting.gui.Height = self.text_height.get()
            # Set the rounded value from Setting to text_height
            self.text_height.set(str(self.setting.gui.Height))
        except:
            pass

    def on_color_updated(self, event):
        try:
            self.setting.gui.KeyPushedColor = self.text_key_pushed_color.get()
            self.label_color_box.config(bg=self.text_key_pushed_color.get())
        except:
            pass

    def _on_enable_midi_file_changed(self):
        try:
            self.setting.gui.EnableMidiFile = self.var_enable_midi_file.get()
        except:
            pass