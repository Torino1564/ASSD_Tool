from Signal import *

class Instrument():
    def __init__(self, editor):
        self.editor = editor
        self.volumen: float = 10
        self.name = None

    def Play(self, note, velocity, duration):
        return Signal()
