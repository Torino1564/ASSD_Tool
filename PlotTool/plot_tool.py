import dearpygui.dearpygui as img
from math import sin


def plot_tool():
        sindatax = []
        sindatay = []

        for i in range(0, 500):
            sindatax.append(i / 1000)
            sindatay.append(0.5 + 0.5 * sin(50 * i / 1000))

        with img.plot(label="Plot tool", height=400, width=400):
            img.add_plot_legend()

            img.add_plot_axis(img.mvXAxis, label="x")
            img.add_plot_axis(img.mvYAxis, label="y", tag="y_axis")

            img.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)", parent="y_axis")
