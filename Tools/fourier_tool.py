import numpy as np
import dearpygui.dearpygui as img
from Tool import *

class FourierTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="FourierTool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.signal = None

    def Run(self):

        with img.plot(label="Señal en el Tiempo", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            xt = img.add_plot_axis(img.mvXAxis)
            yt = img.add_plot_axis(img.mvYAxis)
            self.serie_time = img.add_line_series([], [], parent=yt)

        with img.plot(label="FFT centrada", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            self.xf = img.add_plot_axis(img.mvXAxis, label="Frecuencia [Hz]")
            self.yf = img.add_plot_axis(img.mvYAxis, label="Amplitud")
            self.serie_fft = img.add_line_series([], [], parent=self.yf)

            img.add_button(label="Pegar Señal", callback=self.paste_signal, parent=self.tab)


    def paste_signal(self):
        self.signal = self.editor.selected_signal
        if self.signal is None:
            raise AssertionError("No signal copied")

        x, y = self.signal.GetData()
        img.set_value(self.serie_time, [list(x), list(y)])
        self.apply_fft()

    def apply_fft(self):
        if self.signal is None:
            return

        x, y = self.signal.GetData()
        fs = 1 / (x[1] - x[0])
        Nfft = 2**18

        Xf = np.fft.fft(y, Nfft)
        freq = np.fft.fftfreq(Nfft, d=1/fs)
        Xf = np.fft.fftshift(Xf)
        freq = np.fft.fftshift(freq)

        mag = np.abs(Xf)

        # Detectar la frecuencia de mayor magnitud
        idx_max = np.argmax(mag)
        Fmax = np.abs(freq[idx_max])

        # Limitar entre -10*Fmax y 10*Fmax
        img.set_axis_limits(self.xf, -10 * Fmax, 10 * Fmax)

        img.set_value(self.serie_fft, [list(freq), list(mag)])
