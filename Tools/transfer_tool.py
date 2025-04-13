from scipy import signal as sg
from sympy import *
import numpy as np
import dearpygui.dearpygui as img
from Tool import *



class TransferTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="TransferTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.transfer_function = None
        self.plot_function = None
        self.Init(self.Run)

    def Run(self):

        self.points_per_period_tag = img.add_input_float(label="Points Per Period", min_value=0, default_value=1000)

        filter_button_tag = None
        tf_button_tag = None

        # Themes for active/inactive
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

        def UpdateMode(selected):
            if selected == "filter":
                img.show_item(filter_group_tag)
                img.hide_item(tf_group_tag)
                img.bind_item_theme(filter_button_tag, active_theme)
                img.bind_item_theme(tf_button_tag, default_theme)
            else:
                img.hide_item(filter_group_tag)
                img.show_item(tf_group_tag)
                img.bind_item_theme(tf_button_tag, active_theme)
                img.bind_item_theme(filter_button_tag, default_theme)

        # Inputs y botón bien organizados verticalmente
        with img.group(horizontal=True) as mode_selector_tag:
            filter_button_tag = img.add_button(label="Filter Mode", callback=lambda: UpdateMode("filter"))
            tf_button_tag = img.add_button(label="Transfer Function Mode", callback=lambda: UpdateMode("tf"))

        img.bind_item_theme(tf_button_tag, active_theme)
        img.bind_item_theme(filter_button_tag, default_theme)

        with img.group(horizontal=False, parent=self.tab,show=False) as filter_group_tag:
            self.fc = img.add_input_float(label="Cutoff Frequency [Hz]", default_value=1000, min_value=1, callback=lambda: self.CalculateFilter())
            self.order = img.add_input_int(label="Order", default_value=2, min_value=1, callback=lambda: self.CalculateFilter())
            tipos = ["butter", "bessel", "cheby1", "cheby2", "ellip"]
            self.tipo_filtro = img.add_combo(tipos, label="Filter Type", default_value="butter", callback=lambda: self.CalculateFilter())

        def CalculateTransference():
            s = symbols("s")
            num_expr = simplify(img.get_value(numerator_tag), locals={"s": s})
            den_expr = simplify(img.get_value(denominator_tag), locals={"s": s})

            num = Poly(num_expr, s)
            den = Poly(den_expr, s)

            num_coeffs = [float(c) for c in num.all_coeffs()]
            den_coeffs = [float(c) for c in den.all_coeffs()]

            self.transfer_function = sg.TransferFunction(num_coeffs, den_coeffs)

            self.ShowTransfer()
            self.ApplyTransference()


        with img.group(horizontal=False, parent=self.tab) as tf_group_tag:
            numerator_tag = img.add_input_text(label="Numerator")
            denominator_tag = img.add_input_text(label="Denominator")
            img.add_button(label="Calculate Transference", callback=lambda: CalculateTransference())

        img.add_button(label="Paste Signal", callback=self.paste_signal)

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
            x4 = img.add_plot_axis(img.mvXAxis, label="Freq [Hz]", log_scale=True)
            y4 = img.add_plot_axis(img.mvYAxis, label="Amplitude")
            self.serie_fft = img.add_line_series([], [], parent=y4)

        self.CalculateFilter()

    def paste_signal(self):
        self.signal = self.editor.selected_signal
        if self.signal is None:
            raise AssertionError("No signal copied")

        x, y = self.signal.GetData()
        img.set_value(self.serie_orig, [list(x), list(y)])
        self.ApplyTransference()

    def CalculateFilter(self):

        tipo = img.get_value(self.tipo_filtro)
        orden = img.get_value(self.order)
        fcorte = img.get_value(self.fc)
        b = None
        a = None
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

        self.transfer_function = sg.TransferFunction(b, a)

        self.ShowTransfer()
        self.ApplyTransference()


    def ShowTransfer(self):
        # H(f)
        freq_pos = np.logspace(np.log10(1), np.log10(1000000), 20000)
        w, h = sg.freqs(self.transfer_function.num, self.transfer_function.den, worN=2 * np.pi * freq_pos)
        mag_db = 20 * np.log10(np.abs(h))

        img.set_value(self.serie_hf, [list(w / (2 * np.pi)), list(mag_db)])


    def ApplyTransference(self, sender=None, app_data=None, user_data=None):
        if self.signal is None:
            return

        x, y = self.signal.GetData(img.get_value(self.points_per_period_tag))
        fs = 1 / (x[1] - x[0])
        N = len(y)
        freq = np.fft.fftfreq(N, d=1/fs)

        freq_pos = np.logspace(np.log10(1), np.log10(1000000), 20000)
        w, h = sg.freqs(self.transfer_function.num, self.transfer_function.den, worN=2 * np.pi * freq_pos)

        # Filtrado en frecuencia
        Xf = np.fft.fft(y)
        Hf_interp = np.interp(np.abs(freq), w / (2 * np.pi), np.abs(h))
        Yf = Xf * Hf_interp
        yt = np.fft.ifft(Yf).real

        # FFT
        freq_full = np.fft.fftfreq(N, d=1/fs)

        img.set_value(self.serie_filt, [list(x), list(yt)])
        magdB = []
        for y in np.abs(Yf):
            if y != 0:
                magdB.append(20 * np.log10(y))
            else:
                magdB.append(0)


        img.set_value(self.serie_fft, [list(freq_full), magdB])