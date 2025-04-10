import dearpygui.dearpygui as img
from Tool import *
from PlotTool.plot_tool import *
from Signal import *

class ASSDEditor(object):
    def __init__(self):
        self.signal_array: list[Signal] = []
        print(len(self.signal_array))
        self.selected_signal_index = -1
        self.tool_array: list[Tool] = []
        self.tool_uuid = [0]

    def GetNewToolUUID(self):
        self.tool_uuid[0] += 1
        return self.tool_uuid[0]

    def select_signal(self, idx):
        self.selected_signal_index = idx
        print(f"Copied: {str(idx)}")

    def Run(self):
        with img.window(label="Main Window", tag="Main Window", no_title_bar=True, no_resize=False):
            with img.menu_bar():
                with img.menu(label="Tools"):
                    img.add_text("Available Tools")
                    img.add_separator()
                    if img.add_menu_item(label="Plot Tool"):
                        self.tool_array.append(PlotTool(self, self.GetNewToolUUID()))

            with img.group(horizontal=True):
                with img.child_window(width=300, resizable_x=True, label="SignalWindow", tag="SignalWindow"):
                    img.add_text("Signals")
                    for signal in self.signal_array:
                        img.add_button(
                            label="Copy",
                            callback=self.select_signal,
                            user_data=[self, signal.index],
                            width=40
                        )
                        signal.ShowPreview(100, 100)

                with img.child_window(autosize_x=True):
                    with img.tab_bar():
                        for tool in self.tool_array:
                            with img.tab(label=tool.name):
                                tool.Run()