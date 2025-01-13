import configparser
import os

class GuiSetting():
    def __init__(self):
        self.Width = 0
        self.Height = 0
        self.KeyPushedColor = ""

class Setting():
    CONFIG_FILE = "config.ini"

    def __init__(self):
        self.gui = GuiSetting()

        self.parser = configparser.ConfigParser()
        if not os.path.exists(self.CONFIG_FILE):
            self.create_default_setting()

        self.load_setting()

    def create_default_setting(self):
        self.parser["GUI"] = {
            "Width": "1280",
            "Height": "400",
            "KeyPushedColor": "yellow"
        }

        with open(self.CONFIG_FILE, mode="w") as file:
            self.parser.write(file)

    def load_setting(self):
        self.parser.read(self.CONFIG_FILE, encoding="utf-8")
        self.gui.Width = int(self.parser["GUI"]["Width"])
        self.gui.Height = int(self.parser["GUI"]["Height"])
        self.gui.KeyPushedColor = self.parser["GUI"]["KeyPushedColor"]

    def save_setting(self):
        with open(self.CONFIG_FILE, 'w') as file:
            self.parser["GUI"]["Width"] = str(self.gui.Width)
            self.parser["GUI"]["Height"] = str(self.gui.Height)
            self.parser["GUI"]["KeyPushedColor"] = str(self.gui.KeyPushedColor)
            self.parser.write(file)
