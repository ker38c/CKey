import tkinter
import pygame.midi
import time
from gui.piano.KeyBoard import KeyBoard

class MidiController():
    def __init__(self):
        pygame.midi.init()
        self.start = False
        self.end = False

        self.midi_in_id = pygame.midi.get_default_input_id()
        self.midi_out_id = pygame.midi.get_default_output_id()

        midi_count = pygame.midi.get_count()
        self.midi_info = []
        for i in range(midi_count):
            info = pygame.midi.get_device_info(i)
            self.midi_info.append(info)

        self.NOTE_NAME = [
            "C-2","C#-2","D-2","D#-2","E-1","F-1","F#-1","G-2","G#-2","A-2","A#-2","B-2",
            "C-1","C#-1","D-1","D#-1","E-1","F-1","F#-1","G-1","G#-1",
            # 88-key piano begin
            "A-1", "A#-1", "B-1",
            "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
            "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
            "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
            "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
            "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
            "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
            "C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
            "C7",
            # 88-key piano end
            "C#7", "D7", "D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7",
            "C8", "C#8", "D8", "D#8", "E8", "F8", "F#8", "G8"
        ]

    def init_keyboard(self, keyboard: KeyBoard):
        self.keyboard = keyboard

    def connect(self)->bool:

        try:
            self.midiin = pygame.midi.Input(self.midi_in_id)
            self.midiout = pygame.midi.Output(self.midi_out_id)
            self.start = True
            return True
        except:
            return False

    def receive(self):
        print("waiting for midi device connection.")
        self.wait_connect()
        print("midi device ready.")
        while self.end == False:
            if(self.midiin.poll()):
                recv = self.midiin.read(1)
                self.handler(recv[0])
            time.sleep(0.001)

    def wait_connect(self):
        while True:
            if self.start == True or self.end == True:
                return
            time.sleep(0.1)

    def handler(self, recv: list):
        [status, data1, data2, _], _ = recv

        # Note Off
        if (status & 0xF0) == 0x80:
            key = self.keyboard.find_key(self.get_key_name(data1))
            if key == None:
                return
            key.config(state=tkinter.NORMAL)
            self.midiout.note_off(note=data1)

        # Note On
        elif (status & 0xF0) == 0x90:
            key = self.keyboard.find_key(self.get_key_name(data1))
            if key == None:
                return
            key.config(state=tkinter.ACTIVE)
            self.midiout.note_on(note=data1, velocity=data2)

        # Control Change
        elif (status & 0xF0) == 0xB0:
            # Sustain On/Off
            if data1 == 0x40:
                self.midiout.write_short(0xB0, data1, data2)
                if data2 > 0:
                    self.keyboard.sustain.config(state=tkinter.ACTIVE)
                else:
                    self.keyboard.sustain.config(state=tkinter.NORMAL)

    def get_key_name(self, key_num: int)->str:
        if (key_num < 0) or (key_num >= 128):
            return ""
        return self.NOTE_NAME[key_num]