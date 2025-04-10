import dearpygui.dearpygui as img
from Tool import *
from Signal import *
import copy
import math

class SampleTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="SampleTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.sampled_signal = None
        self.Init(self.Run)

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

        points_per_period = img.add_input_float(label="Points per period", min_value=0, default_value=1000, step=100)

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

        img.add_button(label="Paste Signal", tag="PasteSignal"+self.name+str(self.toolId), callback=lambda: update_plot1_components(
            plot_tag=plot_id,
            y_axis_tag=y_axis,
            x_axis_tag=x_axis,
            series_tag=series,
        ))

        items = ("Ideal", "Natural", "Instant")
        sample_type = img.add_combo(items, label="Sample Type", default_value=items[1])

        sample_freq = img.add_input_double(label="Sample Frequency [Fs]", default_value=10000, min_value=0)
        duty_cycle = img.add_input_float(label="Duty Cycle", default_value=50, min_value=0, max_value=100)

        def sample_signal(sample_type_tag, sample_freq_tag, duty_cycle_tag, plot_tag, y_axis_tag, x_axis_tag, series_tag):
            # sample logic
            sample_type = img.get_value(sample_type_tag)
            sample_freq = img.get_value(sample_freq_tag)
            duty_cycle = img.get_value(duty_cycle_tag)

            self.sampled_signal = copy.copy(self.signal)

            if self.signal.has_math_expr:
                if sample_type == "Ideal":
                    def ideal_sample_math_expr(x: float):
                        period = 1/sample_freq
                        delta_width = period * 0.05
                        nearest_sample_point = round(x / period)
                        if abs(nearest_sample_point * period - x) < delta_width:
                            # the point is in sample range
                            return self.signal.math_expr(x)
                        else:
                            return 0

                    self.sampled_signal.math_expr = ideal_sample_math_expr

                if sample_type == "Instant":
                    class InstantSampleMathExpr(MathExpr):
                        def __init__(self, math_expr: MathExpr, signal, duty_cycle_percentage: float, sample_freq):
                            super().__init__(math_expr)
                            self.signal = signal
                            self.previous_value = None
                            self.previous_value_time_point = None
                            self.duty_cycle_percentage = duty_cycle_percentage
                            self.sample_freq = sample_freq

                        def __call__(self, x: float):
                            period = 1 / self.sample_freq
                            # check if its on a positive or negative clock phase
                            current_period = math.trunc(x / period)
                            period_offset = x - current_period * period

                            if period_offset < (period * self.duty_cycle_percentage):
                                # the point is in sample range
                                if self.previous_value is None or x - self.previous_value_time_point >= period:
                                    self.previous_value = self.math_expression(x)
                                    self.previous_value_time_point = x
                                return self.previous_value
                            else:
                                self.previous_value = None
                                return 0

                    self.sampled_signal.math_expr = InstantSampleMathExpr(math_expr=self.signal.math_expr.Get(),
                                                                          signal=self.sampled_signal,
                                                                          duty_cycle_percentage=duty_cycle/100,
                                                                          sample_freq=sample_freq)

                if sample_type == "Natural":
                    class NaturalSampleMathExpr(MathExpr):
                        def __init__(self, math_expr: MathExpr, signal, duty_cycle_percentage: float, sample_freq):
                            super().__init__(math_expr)
                            self.signal = signal
                            self.previous_value_time_point = None
                            self.duty_cycle_percentage = duty_cycle_percentage
                            self.sample_freq = sample_freq

                        def __call__(self, x: float):
                            period = 1 / self.sample_freq
                            # check if its on a positive or negative clock phase
                            current_period = math.trunc(x / period)
                            period_offset = x - current_period * period

                            if period_offset < (period * self.duty_cycle_percentage):
                                return self.math_expression(x)
                            else:
                                return 0

                    self.sampled_signal.math_expr = NaturalSampleMathExpr(math_expr=self.signal.math_expr.Get(),
                                                                          signal=self.sampled_signal,
                                                                          duty_cycle_percentage=duty_cycle/100,
                                                                          sample_freq=sample_freq)
                update_plot2_components(plot_tag, y_axis_tag, x_axis_tag, series_tag, points_per_period)

            ppp = img.get_value(points_per_period)
            if ppp <= sample_freq/10:
                img.configure_item(warning_tag, show=True)
            else:
                img.configure_item(warning_tag, show=False)

        def update_plot2_components(plot_tag, y_axis_tag, x_axis_tag, series_tag, points_per_period_tag):
            signal = self.sampled_signal
            if self.signal is None:
                raise AssertionError("No signal is copied")

            # Update plot title
            img.set_item_label(plot_tag, signal.name)

            # Update axis label
            img.set_item_label(x_axis_tag, signal.x_label)
            img.set_item_label(y_axis_tag, signal.y_label)

            # Update line series data
            xdata, ydata = signal.GetData(img.get_value(points_per_period_tag))
            img.set_value(series_tag, [xdata, ydata])


        img.add_text("Sampled Signal")

        with img.plot(tag=str("plot2"+self.name + str(self.toolId)), width=-1, height=360, parent=self.tab) as sampled_id:
            img.add_plot_legend()
            x_axis2 = img.add_plot_axis(img.mvXAxis, label="x")
            y_axis2 = img.add_plot_axis(img.mvYAxis, label="y")
            if self.signal is not None:
                xdata2, ydata2 = self.signal.GetData(img.get_value(points_per_period_tag))
            else:
                xdata2 = []
                ydata2 = []
            stem = img.add_stem_series(xdata2, ydata2, parent=y_axis2)

        img.add_button(label="Sample", tag="Sample" + self.name + str(self.toolId), callback=lambda: sample_signal(
            sample_type_tag=sample_type,
            sample_freq_tag=sample_freq,
            duty_cycle_tag=duty_cycle,
            plot_tag=sampled_id,
            x_axis_tag=x_axis2,
            y_axis_tag=y_axis2,
            series_tag=stem
        ))

        warning_tag = img.add_text("Warning: The sample period is similar to the input signal data interval. Please consider increasing the points per period", color=(255, 165, 0), show=False)