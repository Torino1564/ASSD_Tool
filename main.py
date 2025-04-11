import dearpygui.dearpygui as img
import ASSD_Editor as editor
import math
import dearpygui.demo
import numpy as np
from Signal import *
import PlotTool.plot_tool as plt_tool
from scipy.signal import ellip, filtfilt


def save_callback():
    print("Save Clicked")


#SIGNAL 1

freq = 400
fs = 200*freq  # Hz
N = 50
t = np.linspace(0, N*(1/freq), math.floor(N*(fs/freq)), endpoint=False)
signal1 = 0.5 + 0.5 * np.sin(2 * np.pi * freq * t)

#FAAs

# Filter specs
cutoff = 200   # Hz
rp = 1         # passband ripple (dB)
rs = 40        # stopband attenuation (dB)
order = 5

# Design digital filter using actual frequency (not normalized)
b, a = ellip(order, rp, rs, cutoff, btype='low', fs=fs)

filtered_signal = filtfilt(b, a, signal1).copy()

# Start GUI
img.create_context()
img.create_viewport(title='Signal Viewer', width=800, height=600)

def update_y_scale(sender, app_data, user_data):
    """Callback to update Y-axis scale based on slider value"""
    y_axis = user_data
    scale = app_data
    img.set_axis_limits(y_axis, 0, scale)

def update_x_scale(sender, app_data, user_data):
    """Callback to update X-axis scale based on slider value"""
    x_axis = user_data
    scale = app_data
    img.set_axis_limits(x_axis, 0, scale)

#Change

with img.window(label="Signal Display", width=780, height=580):
    with img.plot(label="Signal Plot", height=400, width=750):
        img.add_plot_axis(img.mvXAxis, label="Time (s)")
        x_axis = img.add_plot_axis(img.mvXAxis, label="Time")
        y_axis = img.add_plot_axis(img.mvYAxis, label="Amplitude")

        img.add_line_series(t, signal1, label="Original Signal", parent=y_axis)
        img.add_line_series(t, filtered_signal, label="Filtered Signal", parent=y_axis)

    img.add_slider_float(label="Y-Axis Scale", default_value=1.0, min_value=0.1, max_value=2.0,
                         callback=update_y_scale, user_data=y_axis)
    img.add_slider_float(label="X-Axis Scale", default_value=1.0, min_value=(1/freq), max_value=(N/freq),
                         callback=update_x_scale, user_data=x_axis)



img.setup_dearpygui()
img.show_viewport()
img.start_dearpygui()
img.destroy_context()