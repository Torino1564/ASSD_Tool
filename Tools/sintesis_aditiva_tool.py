from Tool import *
from Instrument import *


class InstrumentoAditivo(Instrument):
    def __init__(self):
        self.attack = None
        self.sustain = None
        self.decay = None
        self.release = None


    def Play(self, frequency: float):

        return 0

class SintesisAditivaTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis Aditiva Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)

    def Run(self):
        img.add_child_window()