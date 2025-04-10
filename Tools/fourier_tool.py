from Tool import *

class FourierTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="SampleTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.sampled_signal = None

        self.Init(self.Run)

    def Run(self):
        print("Fourier Tool Run")
