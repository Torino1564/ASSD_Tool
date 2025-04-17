import numpy as np
import dearpygui.dearpygui as img
from Tool import *

class FourierTool(Tool):
    def __init__(self, editor, uuid, tab: bool = True):
        Tool.__init__(self, name="FourierTool", editor=editor, uuid=uuid)
        self.ppp_tag = None
        self.signal = None
        self.xf = None
        self.yf = None
        self.serie_fft = None

        if tab:
            self.Init(self.Run)

    def Run(self):
        self.ppp_tag = img.add_input_float(label="Points per period", min_value=0, default_value=1000, step=100)

        with img.plot(label="Señal en el Tiempo", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            xt = img.add_plot_axis(img.mvXAxis)
            yt = img.add_plot_axis(img.mvYAxis)
            self.serie_time = img.add_line_series([], [], parent=yt)

        with img.plot(label="FFT centrada", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            self.xf = img.add_plot_axis(img.mvXAxis, label="Frecuencia [Hz]", log_scale=True)
            self.yf = img.add_plot_axis(img.mvYAxis, label="Amplitud")
            self.serie_fft = img.add_stem_series([], [], parent=self.yf)

            img.add_button(label="Pegar Señal", callback=self.paste_signal, parent=self.tab)


    def paste_signal(self):
        self.signal = self.editor.selected_signal
        if self.signal is None:
            raise AssertionError("No signal copied")

        x, y = self.signal.GetData(img.get_value(self.ppp_tag))
        img.set_value(self.serie_time, [list(x), list(y)])
        self.Kernel()

    def Kernel(self):
        if self.signal is None:
            return

        x, y = self.signal.GetData(img.get_value(self.ppp_tag))
        fs = 1 / (x[1] - x[0])

        Xf = np.fft.fft(y)
        freq = np.fft.fftfreq(len(y), d=1/fs)

        mag = 20 * np.log10(np.abs(Xf))

        # Detectar la frecuencia de mayor magnitud
        idx_max = np.argmax(mag)
        Fmax = np.abs(freq[idx_max])

        # Limitar entre -10*Fmax y 10*Fmax
        img.set_axis_limits(self.xf, Fmax/10, 100 * Fmax)

        img.set_value(self.serie_fft, [list(freq), list(mag)])
