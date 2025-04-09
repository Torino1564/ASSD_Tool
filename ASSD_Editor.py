import dearpygui.dearpygui as img
import PlotTool.plot_tool as plt_tool
from Signal import *

class ASSDEditor(object):
    def __init__(self):
        self.signal_array: list[Signal] = []
        self.selected_signal_index = -1

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
                        print("Plot tool")

            with img.group(horizontal=True):
                with img.child_window(width=300, resizable_x=True, label="SignalWindow", tag="SignalWindow"):
                    img.add_text("Signals")
                    for signal in self.signal_array:
                        img.add_button(
                            label="Copy",
                            callback=lambda i=signal.index: self.select_signal(i),
                            width=40
                        )
                        signal.ShowPreview(100, 100)

                with img.child_window(autosize_x=True):
                    with img.tab_bar():
                        with (img.tab(label="Plot Tool")):
                            plt_tool.plot_tool()

                        if (img.add_tab(label="Filter Tool")):
                            print("Plot tool")

                        if (img.add_tab(label="FFT Tool")):
                            print("Plot tool")

                        if (img.add_tab(label="Sampler Tool")):
                            print("Plot tool")