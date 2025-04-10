class Tool(object):
    def __init__(self, name, editor, uuid):
        self.name = name
        self.editor = editor
        self.toolId = uuid

    def Run(self):
        print("Default tool run behaviour")