from Tool import *
import dearpygui.dearpygui as img

class TransferTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="TransferTool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.signal = None

    def Run(self):
        def update_plot1_components(plot_tag, y_axis_tag, x_axis_tag, series_tag):
            self.signal = self.editor.selected_signal
            if self.signal is None:
                raise AssertionError("No signal is copied")

            # Update plot title
            img.set_item_label(plot_tag, self.signal.name)

            # Update axis label
            img.set_item_label(x_axis_tag, self.signal.x_label)
            img.set_item_label(y_axis_tag, self.signal.y_label)

            # Update line series data
            xdata, ydata = self.signal.GetData()
            img.set_value(series_tag, [xdata, ydata])

        with img.plot(label=str(self.name + str(self.toolId)), tag=str("plot1"+self.name + str(self.toolId)), width=-1, height=360, parent=self.tab) as plot_id:
            img.add_plot_legend()
            x_axis = img.add_plot_axis(img.mvXAxis, label="x")
            y_axis = img.add_plot_axis(img.mvYAxis, label="y")
            if self.signal is not None:
                xdata, ydata = self.signal.GetData()
            else:
                xdata = []
                ydata = []
            series = img.add_line_series(xdata, ydata, parent=y_axis)

        img.add_button(label="Paste Signal", tag="PasteSignal"+self.name+str(self.toolId),
                       callback=lambda: update_plot1_components(
                                        plot_tag=plot_id,
                                        y_axis_tag=y_axis,
                                        x_axis_tag=x_axis,
                                        series_tag=series,
                       ))
