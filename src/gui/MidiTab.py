import tkinter
import tkinter.ttk
from midi.MidiController import MidiController
from midi.MidiController import MidiDeviceInfo

class MidiTab():
    def __init__(self, root: tkinter.ttk.Notebook, midi: MidiController):
        self.frame = tkinter.Frame(root)
        self.midi = midi

        self.midi_in_name_list, self.default_midi_in_name = self._get_midi_in_list_and_default()
        self.midi_out_name_list, self.default_midi_out_name = self._get_midi_out_list_and_default()

        # MIDI settings group
        self.midi_settings_frame = tkinter.LabelFrame(self.frame, text="MIDI settings", padx=10, pady=10)
        self.midi_settings_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # MIDI input device
        self.label_midiin = tkinter.Label(self.midi_settings_frame, text="MIDI input")
        self.label_midiin.grid(row=0, column=0, sticky='w')

        self.midi_in_name = tkinter.StringVar(self.frame)
        self.combo_midiin = tkinter.ttk.Combobox(self.midi_settings_frame, height=3, values=self.midi_in_name_list, state="readonly", textvariable=self.midi_in_name)
        self.combo_midiin.set(self.default_midi_in_name)
        self.combo_midiin.bind("<<ComboboxSelected>>", self._on_combobox_selected)
        self.combo_midiin.grid(row=0, column=1)

        # MIDI output device
        self.label_midiout = tkinter.Label(self.midi_settings_frame, text="MIDI output")
        self.label_midiout.grid(row=1, column=0, sticky='w')

        self.midi_out_name = tkinter.StringVar(self.frame)
        self.combo_midiout = tkinter.ttk.Combobox(self.midi_settings_frame, height=3, values=self.midi_out_name_list, state="readonly", textvariable=self.midi_out_name)
        self.combo_midiout.set(self.default_midi_out_name)
        self.combo_midiout.bind("<<ComboboxSelected>>", self._on_combobox_selected)
        self.combo_midiout.grid(row=1, column=1)

        # Apply
        self.button_apply = tkinter.Button(self.frame, text="Apply", command=self._connect_midi)
        self.button_apply.grid(row=1, column=0, columnspan=2, pady=10)

    def _get_midi_in_list_and_default(self) -> tuple[list[str], str]:
        midi_in_name_list = ["---"]
        default_midi_in_name = "---"
        for i, info in enumerate(self.midi.midi_info):
            if info[MidiDeviceInfo.INPUT] == 1:
                if i == self.midi.midi_in_id:
                    default_midi_in_name = info[MidiDeviceInfo.NAME]
                midi_in_name_list.append(info[MidiDeviceInfo.NAME])

        return midi_in_name_list, default_midi_in_name

    def _get_midi_out_list_and_default(self) -> tuple[list[str], str]:
        midi_out_name_list = ["---"]
        default_midi_out_name = "---"
        for i, info in enumerate(self.midi.midi_info):
            if info[MidiDeviceInfo.OUTPUT] == 1:
                if i == self.midi.midi_out_id:
                    default_midi_out_name = info[MidiDeviceInfo.NAME]
                midi_out_name_list.append(info[MidiDeviceInfo.NAME])
        return midi_out_name_list, default_midi_out_name

    def _connect_midi(self):
        self.midi.midi_in_id = self._get_midi_id_from_name(self.midi_in_name.get())
        self.midi.midi_out_id = self._get_midi_id_from_name(self.midi_out_name.get())
        self.midi.connect()

    def _get_midi_id_from_name(self, name: str):
        for i, info in enumerate(self.midi.midi_info):
            if name == info[MidiDeviceInfo.NAME].decode("utf-8"):
                return i
        return -1

    def _on_combobox_selected(self, event):
        self.frame.focus_set()
