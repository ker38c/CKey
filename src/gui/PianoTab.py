import tkinter
import tkinter.ttk
from gui.piano.KeyBoard import KeyBoard
from config.Setting import Setting
from midi.MidiController import MidiController

class PianoTab():
    def __init__(self, root: tkinter.ttk.Notebook, setting: Setting, midi: MidiController):
        self.frame = tkinter.Frame(root)
        self.midi = midi
        self.midi_in_name_list = self.get_midi_in_list()
        self.midi_out_name_list = self.get_midi_out_list()

        self.label_midiin = tkinter.Label(self.frame, text="MIDI input")
        self.label_midiin.grid(row=0, column=0)

        self.midi_in_name = tkinter.StringVar(self.frame)
        self.combo_midiin = tkinter.ttk.Combobox(self.frame, height=3, values=self.midi_in_name_list, state="readonly", textvariable=self.midi_in_name)
        self.combo_midiin.grid(row=0, column=1)

        self.label_midiout = tkinter.Label(self.frame, text="MIDI output")
        self.label_midiout.grid(row=1, column=0)

        self.midi_out_name = tkinter.StringVar(self.frame)
        self.combo_midiout = tkinter.ttk.Combobox(self.frame, height=3, values=self.midi_out_name_list, state="readonly", textvariable=self.midi_out_name)
        self.combo_midiout.grid(row=1, column=1)

        self.button_connect = tkinter.Button(self.frame, text="connect", command=self.connect_midi)
        self.button_connect.grid(row=2, column=0)

        self.keyboard = KeyBoard(master=self.frame, setting=setting)
        self.keyboard.grid(row=3, column=0, columnspan=16)

    def get_midi_in_list(self) -> list[str]:
        midi_in_name_list = []
        for i, dev in enumerate(self.midi.midi_in_info):
            midi_in_name_list.append(dev[1])
        return midi_in_name_list

    def get_midi_out_list(self) -> list[str]:
        midi_out_name_list = []
        for i, dev in enumerate(self.midi.midi_out_info):
            midi_out_name_list.append(dev[1])
        return midi_out_name_list

    def connect_midi(self):
        self.midi.midi_in_id = self.get_midi_id_from_info(self.midi_in_name.get())
        self.midi.midi_out_id = self.get_midi_id_from_info(self.midi_out_name.get())
        self.midi.connect()
        self.button_connect.config(state="disabled")

    def get_midi_id_from_info(self, name: str):
        for i, info in enumerate(self.midi.midi_info):
            if name == info[1].decode("utf-8"):
                return i
        return -1
