import dearpygui.dearpygui as img
import ASSD_Editor as editor
import dearpygui.demo
from Signal import *
import Tools.plot_tool as plt_tool
from math import sin
from math import sqrt
from math import exp
import numpy as np


def save_callback():
    print("Save Clicked")


img.create_context()
img.create_viewport(title="ASSD Tool", width=800, height=600, x_pos=0, y_pos=0)
img.setup_dearpygui()
img.maximize_viewport()

editor = editor.ASSDEditor()
editor.Run()

img.set_primary_window("Main Window", True)
img.show_viewport()
img.start_dearpygui()
img.destroy_context()
