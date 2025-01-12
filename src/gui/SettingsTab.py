import tkinter
import tkinter.ttk
from config.Setting import Setting

class SettingsTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting):
        self.frame = tkinter.Frame(root)
        self.setting = setting

        self.label_window = tkinter.Label(self.frame, text="Window settings")
        self.label_window.grid(row=0, column=0)

        self.label_width = tkinter.Label(self.frame, text="Window width")
        self.label_width.grid(row=1, column=0)

        self.text_width = tkinter.StringVar()
        self.text_width.set(setting.gui.Width)
        self.entry_width = tkinter.Entry(self.frame, textvariable=self.text_width)
        self.entry_width.grid(row=1, column=1)

        self.label_height = tkinter.Label(self.frame, text="Window height")
        self.label_height.grid(row=2, column=0)

        self.text_height = tkinter.StringVar()
        self.text_height.set(setting.gui.Height)
        self.entry_height = tkinter.Entry(self.frame, textvariable=self.text_height)
        self.entry_height.grid(row=2, column=1)

        self.button_apply = tkinter.Button(self.frame, text="apply", command=self.apply_setting)
        self.button_apply.grid(row=3, column=1)

    def apply_setting(self):
        self.setting.gui.Width = int(self.text_width.get())
        self.setting.gui.Height = int(self.text_height.get())

