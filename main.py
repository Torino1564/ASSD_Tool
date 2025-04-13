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

sindatax = []
sindatay = []

for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

editor.AddSignal(Signal(name="Test Signal", Xdata=sindatax, Ydata=sindatay))

sqrtdatax = []
sqrtdatay = []

for i in range(0, 500):
    sqrtdatax.append(i / 1000)
    sqrtdatay.append(0.5 + 0.5 * sqrt(50 * i / 1000))

editor.AddSignal(
    Signal(name="Test Signal 2", Xdata=sqrtdatax, Ydata=sqrtdatay))

editor.AddSignal(Signal(name="Test Signal 3", math_expr=MathExpr(lambda x: sin(2*np.pi*x)), periodic=True, period=1, x_label="t", y_label="V"))

img.set_primary_window("Main Window", True)
img.show_viewport()
img.start_dearpygui()
img.destroy_context()
