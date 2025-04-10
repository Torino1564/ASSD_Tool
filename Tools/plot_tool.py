from Tool import *


class PlotTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="PlotTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.Init(self.Run)

    def Run(self):
        def update_plot_components(plot_tag, y_axis_tag, x_axis_tag, series_tag):
            signal = self.editor.selected_signal
            if signal is None:
                raise AssertionError("No signal is copied")

            # Update plot title
            img.set_item_label(plot_tag, signal.name)

            # Update axis label
            img.set_item_label(x_axis_tag, signal.x_label)
            img.set_item_label(y_axis_tag, signal.y_label)

            # Update line series data
            xdata, ydata = signal.GetData()
            img.set_value(series_tag, [xdata, ydata])

        with img.plot(label=str(self.name + str(self.toolId)), width=400, height=240) as plot_id:
            img.add_plot_legend()
            x_axis = img.add_plot_axis(img.mvXAxis, label="x")
            y_axis = img.add_plot_axis(img.mvYAxis, label="y")
            series = img.add_line_series([] if self.signal == None else self.signal.Xdata(),
                                         [] if self.signal == None else self.signal.Ydata(),
                                         parent=y_axis)

        img.add_button(label="Update Plot", tag="UpdatePlot"+self.name+str(self.toolId), callback=lambda: update_plot_components(
            plot_tag=plot_id,
            y_axis_tag=y_axis,
            x_axis_tag=x_axis,
            series_tag=series,
        ))
