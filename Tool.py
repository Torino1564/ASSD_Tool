import dearpygui.dearpygui as img

class Tool(object):
    def __init__(self, name, editor, uuid):
        self.name = name
        self.editor = editor
        self.toolId = uuid
        self.tab = None

    def Init(self, run):
        with img.tab(label=self.name, tag=str(self.name + str(self.toolId)), parent=self.editor.tab_bar) as self.tab:
            run()
