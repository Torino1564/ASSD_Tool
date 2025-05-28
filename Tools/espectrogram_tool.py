from Tool import *
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import dearpygui.dearpygui as img
from scipy.signal import spectrogram
import os
import sys
import subprocess

class EspectrogramTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Espectrogram Tool", editor=editor, uuid=uuid)
        self.window_type_tag = None
        self.nperseg_tag = None
        self.fs = 44100
        self.duration = 1.0
        self.signal = None
        self.signal_x = None
        self.signal_y = None
        self.current_freqs = []
        self.pending_plot = False
        self.Init(self.Run)

    def generate_multitonal_signal(self, label):
        t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        if label == "Señal A":
            freqs = [500, 1000, 2000, 4000, 8000]
        elif label == "Señal B":
            freqs = [600, 1200, 2400, 4800, 9600]
        elif label == "Señal C":
            freqs = [750, 1500, 3000, 6000, 9000]
        else:
            freqs = [1000]

        y = np.zeros_like(t)
        for f in freqs:
            y += np.sin(2 * np.pi * f * t)

        y /= len(freqs)
        self.signal_x = t.copy()
        self.signal_y = y.copy()
        self.current_freqs = freqs
        self.pending_plot = True

    def paste_signal(self):
        sig = self.editor.selected_signal
        self.signal = sig
        if sig is None:
            print("⚠️ No hay señal copiada desde otra herramienta.")
            return
        try:
            x = []
            y = []
            if sig.period is not None:
                x, y = sig.GetData(pointsPerPeriod=img.get_value(self.ppp_tag), numPeriods=img.get_value(self.num_periods_tag))
            else:
                x, y = sig.GetData(total_samples=img.get_value(self.total_samples_tag))
            self.signal_x = x
            self.signal_y = y
            self.current_freqs = []
            self.pending_plot = True
        except Exception as e:
            print(f"⚠️ Error al obtener datos de la señal pegada: {e}")

    def Run(self):
        def update_duration(sender, app_data):
            self.duration = app_data

        print("Running Espectrogram Tool")

        with img.collapsing_header(label="Señales con 5 frecuencias", default_open=False):
            for label in ["Señal A", "Señal B", "Señal C"]:
                img.add_button(label=label, callback=self._generate_callback(label))
        self.ppp_tag = img.add_slider_float(label="Points per period", default_value=1000, min_value=0, max_value=10000)
        self.num_periods_tag = img.add_slider_float(label="Periods to show", default_value=4, min_value=0, max_value=10)
        self.total_samples_tag = img.add_slider_float(label="Total samples (not periodic)", default_value=10000, min_value=100, max_value=100000)
        img.add_button(label="Pegar señal copiada", callback=self.paste_signal)
        img.add_button(label="Mostrar Espectrograma", callback=self.mostrar_espectrograma)
        img.add_separator()

        img.add_slider_float(
            label="Duración de la señal [s]",
            default_value=1.0,
            min_value=0.5,
            max_value=10.0,
            format="%.2f",
            callback=update_duration
        )

        self.window_type_tag = img.add_combo(
            items=["hann", "hamming", "blackman", "bartlett"],
            label="Tipo de Ventana",
            default_value="hann"
        )

        self.nperseg_tag = img.add_slider_int(
            label="Tamaño ventana (nperseg)",
            default_value=1024,
            min_value=128,
            max_value=8192
        )

    def _generate_callback(self, label):
        def callback(sender, app_data):
            self.generate_multitonal_signal(label)
            self.mostrar_espectrograma()
        return callback

    def mostrar_espectrograma(self):
        if not self.pending_plot:
            print("ℹ️ No hay nueva señal para mostrar.")
            return

        try:
            xdata = self.signal_x
            ydata = self.signal_y

            if xdata is None or ydata is None or len(xdata) < 2:
                print("⚠️ Señal inválida o insuficiente.")
                return

            fs = 1 / (xdata[1] - xdata[0])
            window_type = img.get_value(self.window_type_tag)
            nperseg = img.get_value(self.nperseg_tag)

            ydata = np.array(ydata, dtype=np.float64)

            if nperseg > len(ydata):
                nperseg = len(ydata)

            f, t, Sxx = spectrogram(ydata, fs=fs, window=window_type, nperseg=nperseg, noverlap=nperseg // 2)

            plt.figure(figsize=(12, 6))
            plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
            plt.ylabel("Frecuencia [Hz]")
            fmax = max(self.current_freqs) if self.current_freqs else 1000
            ymax = fmax + 1000 if fmax < 19000 else 20000
            plt.ylim(0, ymax)
            plt.xlabel("Tiempo [s]")
            plt.title("Espectrograma")
            plt.colorbar(label="Intensidad [dB]")

            
            # Etiquetas de frecuencias
            for freq in self.current_freqs:
                plt.text(x=t[len(t)//2], y=freq + 100, s=f"{freq} Hz", color='white', ha='center', fontsize=8, backgroundcolor='black')

            plt.tight_layout()
            plt.savefig("espectrograma.png", bbox_inches='tight')
            plt.close()

            if sys.platform.startswith('darwin'):
                subprocess.call(('open', 'espectrograma.png'))
            elif os.name == 'nt':
                os.startfile('espectrograma.png')
            elif os.name == 'posix':
                subprocess.call(('xdg-open', 'espectrograma.png'))

            self.pending_plot = False

        except Exception as e:
            print(f"⚠️ Error al generar espectrograma: {e}")
