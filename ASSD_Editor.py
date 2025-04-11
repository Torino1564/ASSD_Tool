import dearpygui.dearpygui as img
from Tool import *
from Tools.plot_tool import *
from Tools.sample_tool import *
from Tools.fourier_tool import *
from Tools.transfer_tool import *
from Signal import *


class Data:
    def __init__(self, editor, signal):
        self.editor = editor
        self.signal = signal


def select_signal(sender, data, user_data: Data):
    user_data.editor.selected_signal = user_data.signal
    print(f"Copied: {str(user_data.signal.name)}")


class ASSDEditor(object):
    def __init__(self):
        self.signal_array: list[Signal] = []
        print(len(self.signal_array))
        self.selected_signal = None
        self.tool_array: list[Tool] = []
        self.tool_uuid = [0]
        self.tab_bar = None

    def GetNewToolUUID(self):
        self.tool_uuid[0] += 1
        return self.tool_uuid[0]

    def AddSignal(self, signal: Signal):
        tag = img.add_button(label="Copy", tag=str("Copy" + str(signal.name)), parent="SignalWindow", width=40)
        img.set_item_callback(tag, select_signal)
        img.set_item_user_data(tag, Data(editor=self, signal=signal))
        signal.ShowPreview(100, 100)

    def Run(self):
        with img.window(label="Main Window", tag="Main Window", no_title_bar=True, no_resize=False):
            with img.menu_bar():
                with img.menu(label="Tools"):
                    img.add_text("Available Tools")
                    img.add_separator()
                    img.add_menu_item(label="Plot Tool",
                                      callback=lambda: self.tool_array.append(PlotTool(self, self.GetNewToolUUID())))
                    img.add_menu_item(label="Sample Tool",
                                      callback=lambda: self.tool_array.append(SampleTool(self, self.GetNewToolUUID())))
                    img.add_menu_item(label="Fourier Tool",
                                      callback=lambda: self.tool_array.append(FourierTool(self, self.GetNewToolUUID())))
                    img.add_menu_item(label="Transfer Tool",
                                      callback=lambda: self.tool_array.append(TransferTool(self, self.GetNewToolUUID())))

            with img.group(horizontal=True):
                with img.child_window(width=300, resizable_x=True, label="SignalWindow", tag="SignalWindow"):
                    img.add_text("Signals")
                    for signal in self.signal_array:
                        self.AddSignal(signal)

                with img.child_window(autosize_x=True):
                    with img.tab_bar() as self.tab_bar:
                        img.add_tab(label="Default Tab")
