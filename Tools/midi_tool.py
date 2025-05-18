from Tool import *

class MidiTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Midi Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)

    def Run(self):
        img.add_child_window()