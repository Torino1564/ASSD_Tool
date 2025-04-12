from scipy import signal as sg
import numpy as np
import dearpygui.dearpygui as img
from Tool import *


class TransferTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="TransferTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.Init(self.Run)

    def Run(self):
        # Inputs y botón bien organizados verticalmente
        with img.group(horizontal=False, parent=self.tab):
            self.fc = img.add_input_float(label="Cutoff Frequency [Hz]", default_value=1000, min_value=1, callback=self.apply_filter)
            self.order = img.add_input_int(label="Order", default_value=2, min_value=1, callback=self.apply_filter)
            tipos = ["butter", "bessel", "cheby1", "cheby2", "ellip"]
            self.tipo_filtro = img.add_combo(tipos, label="Filter Type", default_value="butter", callback=self.apply_filter)

            img.add_button(label="Pegar Señal", callback=self.paste_signal)

        # Gráficos
        with img.plot(label="Señal Original", width=-1, height=200, parent=self.tab) as plot_orig:
            img.add_plot_legend()
            x1 = img.add_plot_axis(img.mvXAxis)
            y1 = img.add_plot_axis(img.mvYAxis)
            self.serie_orig = img.add_line_series([], [], parent=y1)

        with img.plot(label="Filtro en Frecuencia H(f) [dB]", width=-1, height=200, parent=self.tab) as plot_hf:
            img.add_plot_legend()
            self.x2 = img.add_plot_axis(img.mvXAxis, label="Freq [Hz]", log_scale=True)
            self.y2 = img.add_plot_axis(img.mvYAxis, label="Magnitude [dB]")
            self.serie_hf = img.add_line_series([], [], parent=self.y2)

        with img.plot(label="Señal Filtrada", width=-1, height=200, parent=self.tab) as plot_filt:
            img.add_plot_legend()
            x3 = img.add_plot_axis(img.mvXAxis)
            y3 = img.add_plot_axis(img.mvYAxis)
            self.serie_filt = img.add_line_series([], [], parent=y3)

        with img.plot(label="FFT Señal Filtrada", width=-1, height=200, parent=self.tab) as plot_fft:
            img.add_plot_legend()
            x4 = img.add_plot_axis(img.mvXAxis, label="Freq [Hz]")
            y4 = img.add_plot_axis(img.mvYAxis, label="Amplitude")
            self.serie_fft = img.add_line_series([], [], parent=y4)

    def paste_signal(self):
        self.signal = self.editor.selected_signal
        if self.signal is None:
            raise AssertionError("No signal copied")

        x, y = self.signal.GetData()
        img.set_value(self.serie_orig, [list(x), list(y)])
        self.apply_filter()

    def apply_filter(self, sender=None, app_data=None, user_data=None):
        if self.signal is None:
            return

        x, y = self.signal.GetData()
        fs = 1 / (x[1] - x[0])
        N = len(y)
        freq = np.fft.fftfreq(N, d=1/fs)

        tipo = img.get_value(self.tipo_filtro)
        orden = img.get_value(self.order)
        fcorte = img.get_value(self.fc)

        if tipo == "butter":
            b, a = sg.butter(orden, 2 * np.pi * fcorte, btype='low', analog=True)
        elif tipo == "bessel":
            b, a = sg.bessel(orden, 2 * np.pi * fcorte, btype='low', analog=True, norm='phase')
        elif tipo == "cheby1":
            b, a = sg.cheby1(orden, 1, 2 * np.pi * fcorte, btype='low', analog=True)
        elif tipo == "cheby2":
            b, a = sg.cheby2(orden, 20, 2 * np.pi * fcorte, btype='low', analog=True)
        elif tipo == "ellip":
            b, a = sg.ellip(orden, 1, 20, 2 * np.pi * fcorte, btype='low', analog=True)

        # H(f)
        freq_pos = np.logspace(np.log10(1), np.log10(100 * fcorte), 2000)
        w, h = sg.freqs(b, a, worN=2 * np.pi * freq_pos)
        mag_db = 20 * np.log10(np.abs(h))

        img.set_value(self.serie_hf, [list(w / (2 * np.pi)), list(mag_db)])
        img.set_axis_limits(self.x2, 0.1 * fcorte, 10 * fcorte)
        img.set_axis_limits(self.y2, -50, 1)

        # Filtrado en frecuencia
        Xf = np.fft.fft(y)
        Hf_interp = np.interp(np.abs(freq), w / (2 * np.pi), np.abs(h))
        Yf = Xf * Hf_interp
        yt = np.fft.ifft(Yf).real

        # FFT centrada
        freq_full = np.fft.fftshift(np.fft.fftfreq(N, d=1/fs))
        Yf_shifted = np.fft.fftshift(Yf)

        img.set_value(self.serie_filt, [list(x), list(yt)])
        img.set_value(self.serie_fft, [list(freq_full), list(np.abs(Yf_shifted))])