from Tool import *

class SystemTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self,"System Tool", editor, uuid)

        self.Init(self.Run)

    def AddLink(self):
        print("Adding Node")

    def RemoveLink(self):
        print("Removing Node")

    def Run(self):
        print("Running SystemTool")


    def Kernel(self):
        print("Kernel")