import dearpygui.dearpygui as img
import ASSD_Editor as editor
import dearpygui.demo
from Signal import *
import PlotTool.plot_tool as plt_tool
from math import sin
from math import sqrt

def save_callback():
    print("Save Clicked")


img.create_context()
img.create_viewport()
img.setup_dearpygui()

editor = editor.ASSDEditor()

sindatax = []
sindatay = []

for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

editor.signal_array.append(Signal(name="Test Signal", index=len(editor.signal_array), Xdata=sindatax, Ydata=sindatay))

sqrtdatax = []
sqrtdatay = []

for i in range(0, 500):
    sqrtdatax.append(i / 1000)
    sqrtdatay.append(0.5 + 0.5 * sqrt(50 * i / 1000))

editor.signal_array.append(Signal(name="Test Signal 2", index=len(editor.signal_array), Xdata=sqrtdatax, Ydata=sqrtdatay))


editor.Run()

#dearpygui.demo.show_demo()

def update_plot_size(sender, data):
    # Get dimensions of the window
    width, height = img.get_item_rect_size("SignalWindow")

    for signal in editor.signal_array:
        # Apply the dimensions to the plot
        img.set_item_width(signal.name, width)
        img.set_item_height(signal.name, width * 0.6)

    img.set_frame_callback(img.get_frame_count() + 10, update_plot_size)


img.set_frame_callback(img.get_frame_count() + 1, update_plot_size)
img.set_primary_window("Main Window", True)
img.show_viewport()
img.start_dearpygui()
img.destroy_context()