import dearpygui.dearpygui as img
from Tool import *


class PlotTool(Tool):
        def __init__(self, editor, uuid, signal=None):
                super().__init__("PlotTool", editor, uuid)
                self.Tool = Tool("PlotTool", editor, uuid)
                self.signal = signal
        def Run(self):
                def update_plot_components(plot_tag, y_axis_tag, x_axis_tag, series_tag):
                        selected_signal_index = self.Tool.editor.selected_signal_index

                        if selected_signal_index == -1:
                                raise AssertionError("No signal is copied")

                        signal = self.Tool.editor.signal_array[self.Tool.editor.selected_signal_index]
                        # Update plot title
                        img.set_item_label(plot_tag, signal.name)

                        # Update axis label
                        img.set_item_label(x_axis_tag, signal.x_label)
                        img.set_item_label(y_axis_tag, signal.y_label)

                        # Update line series data
                        img.set_value(series_tag, [signal.GetXData(), signal.GetYData()])

                with img.plot(label=str(self.name + str(self.Tool.toolId)), width=400, height=240) as plot_id:
                        img.add_plot_legend()
                        x_axis = img.add_plot_axis(img.mvXAxis, label="x")
                        y_axis = img.add_plot_axis(img.mvYAxis, label="y")
                        series = img.add_line_series( [] if self.signal == None else self.signal.Xdata(),
                                             [] if self.signal == None else self.signal.Ydata(),
                                             parent=y_axis)

                img.add_button(label="Update Plot", callback=lambda: update_plot_components(
                        plot_tag=plot_id,
                        y_axis_tag=y_axis,
                        x_axis_tag=x_axis,
                        series_tag=series,
                ))
