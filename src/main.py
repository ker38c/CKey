from gui.MainWindow import MainWindow
from config.Setting import Setting

def main():
    setting = Setting()
    window = MainWindow(setting)
    window.start()


if __name__ == "__main__":
    main()