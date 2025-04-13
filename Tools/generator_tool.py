from Signal import Signal, MathExpr
from utl.Math import *
import numpy as np
from Tool import *
import dearpygui.dearpygui as img


class GeneratorTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Generator Tool", uuid=uuid, editor=editor)
        self.Init(self.Run)
        self.generated_signal = None

    def Run(self):
        print("Generator Tool running")
        name_tag = img.add_input_text(label="Name")
        frequency_tag = img.add_input_float(label="Frequency [Hz]", min_value=0, default_value=1000)
        amplitude_tag = img.add_input_float(label="Amplitude Pk2Pk [Hz]", min_value=0, default_value=1)

        functions = ["sin", "square", "triangular", "sinc", "exp", "arb"]
        function_tag = img.add_combo(functions, label="Function Type", default_value=functions[0])

        symetry_tag = img.add_slider_float(label="Symetry/Duty Cycle", min_value=0, max_value=1, default_value=0.5)

        img.add_text(label="Offset Setting")

        offset_mode_tag = None
        levels_mode_tag = None
        offset_tag = None
        low_level_tag = None
        high_level_tag = None

        offset_mode = "offset"

        with img.theme() as default_theme:
            with img.theme_component(img.mvButton):
                img.add_theme_color(img.mvThemeCol_Button, (70, 70, 70))  # dark gray
                img.add_theme_color(img.mvThemeCol_ButtonHovered, (90, 90, 90))
                img.add_theme_color(img.mvThemeCol_ButtonActive, (110, 110, 110))

        with img.theme() as active_theme:
            with img.theme_component(img.mvButton):
                img.add_theme_color(img.mvThemeCol_Button, (200, 120, 0))  # orange
                img.add_theme_color(img.mvThemeCol_ButtonHovered, (220, 140, 30))
                img.add_theme_color(img.mvThemeCol_ButtonActive, (255, 160, 50))

        def UpdateMode(
                selected,
                offset_mode_tag,
                levels_mode_tag,
                offset_tag,
                low_level_tag,
                high_level_tag
        ):
            if selected == "offset":
                img.bind_item_theme(offset_mode_tag, active_theme)
                img.bind_item_theme(levels_mode_tag, default_theme)
                img.show_item(offset_tag)
                img.hide_item(low_level_tag)
                img.hide_item(high_level_tag)
                offset_mode = "offset"

            if selected == "levels":
                img.bind_item_theme(levels_mode_tag, active_theme)
                img.bind_item_theme(offset_mode_tag, default_theme)
                img.hide_item(offset_tag)
                img.show_item(low_level_tag)
                img.show_item(high_level_tag)
                offset_mode = "levels"


        with img.group(horizontal=True):
            offset_mode_tag = img.add_button(label="Offset Mode",
                                             callback=lambda: UpdateMode(
                                                 "offset",
                                                 offset_mode_tag,
                                                 levels_mode_tag,
                                                 offset_tag,
                                                 low_level_tag,
                                                 high_level_tag))
            levels_mode_tag = img.add_button(label="Levels Mode",
                                             callback=lambda: UpdateMode(
                                                 "levels",
                                                 offset_mode_tag,
                                                 levels_mode_tag,
                                                 offset_tag,
                                                 low_level_tag,
                                                 high_level_tag))

        img.bind_item_theme(offset_mode_tag, active_theme)
        img.bind_item_theme(levels_mode_tag, default_theme)

        offset_tag = img.add_input_float(label="Offset")
        low_level_tag = img.add_input_float(label="Low Level", show=False)
        high_level_tag = img.add_input_float(label="High Level", show=False)

        def UpdateGeneratedGraph(plot_tag, y_axis_tag, x_axis_tag, series_tag):
            signal = self.generated_signal
            # Update plot title
            img.set_item_label(plot_tag, signal.name)

            # Update axis label
            img.set_item_label(x_axis_tag, signal.x_label)
            img.set_item_label(y_axis_tag, signal.y_label)

            # Update line series data
            xdata, ydata = signal.GetData(1000)
            img.set_value(series_tag, [xdata, ydata])

        def GenerateSignal():
            base_expr = None
            # every base expression is normalized to a period and amplitude of 1
            match img.get_value(function_tag):
                case "sin":
                    base_expr = norm_sin
                case "square":
                    base_expr = norm_sqr
                case "triangular":
                    base_expr = norm_triang

            # denormalize:
            offset = img.get_value(offset_tag)
            freq = img.get_value(frequency_tag)
            amplitude = img.get_value(amplitude_tag)
            symetry = img.get_value(symetry_tag)
            period = 1/freq
            def DenormalizedExpr(x):
                if x < period * symetry:
                    x = 0.5 * (x / symetry)
                else:
                    x = period/2 + 0.5 * ((x - period * symetry)/(1 - symetry))

                return offset + amplitude * base_expr(freq*x)

            self.generated_signal = Signal(img.get_value(name_tag), math_expr=MathExpr(DenormalizedExpr), period=period)
            UpdateGeneratedGraph(plot_tag, y_axis_tag, x_axis_tag, series_tag)

        generate_tag = img.add_button(label="Generate", callback= lambda: GenerateSignal())
        plot_tag = None
        series_tag = None
        with img.plot(label="Generated Signal", width=-1, height=300, show=True) as plot_tag:
            x_axis_tag = img.add_plot_axis(img.mvXAxis, label="x")
            y_axis_tag = img.add_plot_axis(img.mvYAxis, label="y")

            series_tag = img.add_line_series([], [] , parent=y_axis_tag)

        img.add_button(label="Save Generated Signal", callback=lambda: self.editor.AddSignal(self.generated_signal))