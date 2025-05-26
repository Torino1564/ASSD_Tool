from Tool import *
from Instrument import *
import dearpygui.dearpygui as img
import numpy as np
import sounddevice as sd

from utl import Math


class FMInstrument(Instrument):
    def __init__(self, editor, fm_ratio, mod_index):
        super(FMInstrument, self).__init__(editor)
        self.fm_ratio = fm_ratio
        self.mod_index = mod_index
        self.name = 'Sintesis_FM_tool'

    def Play(self, note, velocity, duration):
        class SintesisFMMathExpression(MathExpr):
            def __init__(self, fc, fm_ratio, mod_index, duration):
                self.fc = fc
                self.fm_ratio = fm_ratio
                self.mod_index = mod_index
                self.duration = duration

            def __call__(self, x: float):
                A = np.exp(-3 * x) * (1 - np.exp(-5 * x))  # Envelope
                fm = self.fm_ratio * self.fc
                modulator = np.sin(2 * np.pi * fm * x)
                return A * np.sin(2 * np.pi * self.fc * x * self.mod_index * modulator)

            def EvaluatePoints(self, xValues: list[float]):
                A = np.exp(-3 * xValues) * (1 - np.exp())
                fm = self.fm_ratio * self.fc
                modulator = np.sin(2 * np.pi * fm * xValues)
                return A * np.sin(2 * np.pi * self.fc * xValues * self.mod_index * modulator)

        return Signal(math_expr=
            SintesisFMMathExpression(note, fm_ratio=self.fm_ratio, mod_index=self.mod_index, duration=duration)
        )


def fm_clarinet(fc, duration=2.0, fm_ratio=1.5, mod_index=2.0, fs=44100):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    A = np.exp(-3 * t) * (1 - np.exp(-5 * t))  # Envelope
    fm = fm_ratio * fc
    modulator = np.sin(2 * np.pi * fm * t)
    y = A * np.sin(2 * np.pi * fc * t + mod_index * modulator)
    return t, y

class SintesisFMTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis FM Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)

    def play_fm_callback(self):
        freq = img.get_value("freq_input")
        t, sound = fm_clarinet(freq)
        sd.play(sound, 44100)
        sd.wait()

    def update_plot(self):
        freq = img.get_value("freq_input")
        duration = img.get_value(self.duration_tag)
        fs = 44100
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)

        # Original sine wave
        sine_wave = np.sin(2 * np.pi * freq * t)

        # FM clarinet signal
        _, fm_signal = fm_clarinet(freq, duration)

        # Update both plots
        img.set_value(self.original_line, [t.tolist(), sine_wave.tolist()])
        img.set_value(self.fm_line, [t.tolist(), fm_signal.tolist()])

    def Run(self):
            img.add_slider_float(label="Duración (s)", default_value=1.0, min_value=0.1, max_value=5.0, tag="dur_slider")
            self.duration_tag = "dur_slider"

            self.plot_tag = None
            # Plot 1: Original sine wave
            with img.plot(label="Onda Senoidal (Original)", height=200) as self.original_plot:
                x1 = img.add_plot_axis(img.mvXAxis, label="Tiempo")
                y1 = img.add_plot_axis(img.mvYAxis, label="Amplitud")
                self.original_line = img.add_line_series([], [], parent=y1)

            # Plot 2: FM Clarinet
            with img.plot(label="Señal FM (Clarinet)", height=200) as self.fm_plot:
                x2 = img.add_plot_axis(img.mvXAxis, label="Tiempo")
                y2 = img.add_plot_axis(img.mvYAxis, label="Amplitud")
            self.fm_line = img.add_line_series([], [], parent=y2)            

            self.fm_ratio_tag = img.add_input_float(label="FM Ratio", default_value=1.5)
            self.mod_index_tag = img.add_input_float(label="Mod index", default_value=2.0)


            img.add_button(label="Actualizar Gráficos", callback=self.update_plot)
            img.add_input_float(label="Frecuencia (Hz)", default_value=147.0, tag="freq_input", step=1.0)
            img.add_button(label="Reproducir Sonido", callback=self.play_fm_callback)

            def AddInstrument():
                self.editor.AddInstrument(FMInstrument(self.editor,
                                                       img.get_value(self.fm_ratio_tag),
                                                       mod_index=img.get_value(self.mod_index_tag)))

            img.add_button(label="Add instrument", callback=lambda: AddInstrument())