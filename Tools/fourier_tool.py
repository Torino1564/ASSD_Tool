from Tool import *
from numpy.fft import fft, fftfreq
import numpy as np

class FourierTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="FourierTool", editor=editor, uuid=uuid)
        self.signal = signal
        self.sampled_signal = None
        self.FFTs_freqs = []
        self.FFTs_magnitudes = []
        self.fft_mag_label = ""

        self.Init(self.Run)

    def Run(self):
        def update_plot_components(plot_tag, y_axis_tag, x_axis_tag, series_tag):
            signal = self.editor.selected_signal
            if signal is None:
                raise AssertionError("No signal is copied")
            
            # Update plot title
            img.set_item_label(plot_tag, signal.name)
            
            # Update axis label
            img.set_item_label(x_axis_tag, "rad/s")
            img.set_item_label(y_axis_tag, "V.s")
            
            self.calculate_FFT()    # Actualizo valores de la FFT (Magnitudes y dominio de frecuencia)
            
            # Update line series data
            xdata, ydata = self.FFTs_freqs, self.FFTs_magnitudes
            img.set_value(series_tag, [xdata, ydata])
        
        if self.signal != None:
            self.calculate_FFT()

        with img.plot(label=str(self.name + str(self.toolId)), width=400, height=240) as plot_id:
            img.add_plot_legend()
            x_axis = img.add_plot_axis(img.mvXAxis, label="rad/s")
            y_axis = img.add_plot_axis(img.mvYAxis, label="V.s")
            series = img.add_line_series([] if self.signal == None else self.FFTs_freqs,
                                         [] if self.signal == None else self.FFTs_magnitudes,
                                         parent=y_axis)

        img.add_button(label="Update Plot", tag="UpdatePlot"+self.name+str(self.toolId), callback=lambda: update_plot_components(
            plot_tag=plot_id,
            y_axis_tag=y_axis,
            x_axis_tag=x_axis,
            series_tag=series,
        ))
        
    def calculate_FFT(self):
        signal = self.editor.selected_signal
        if signal is None:
            raise AssertionError("No signal is copied")
        
        # ------------------ DFT ------------------
        
        X_dft = self.DFT()
        
        # ------------------ FFT ------------------
        x_data, y_data = signal.GetData()
        dx = np.diff(x_data)
        
        # Dominio temporal
        dt = dx[0]
        N = len(x_data)
        t = x_data
        f_t = y_data
        
        X_fft = fft(y_data)

        # Frecuencia en Hz (omega = 2πf)
        freqs = fftfreq(N, d=dt)
        omega_dft = 2 * np.pi * freqs

        # Sólo mitad positiva para DFT/FFT
        half = N // 2
        omega_dft_pos = omega_dft[:half]
        X_dft_mag = np.abs(X_dft[:half]) * dt
        X_fft_mag = np.abs(X_fft[:half]) * dt / N   # Normalización
        
        self.FFTs_freqs = omega_dft_pos
        self.FFTs_magnitudes = X_fft_mag
        #self.fft_mag_label = signal.x_label + " . " + signal.y_label
        
        
    def DFT(self):
        signal = self.editor.selected_signal
        x_data, y_data = signal.GetData()
        N = len(x_data)
        X = np.zeros(N, dtype=complex)
        for k in range(N):
            for n in range(N):
                X[k] += y_data[n] * np.exp(-2j * np.pi * k * n / N)
        return X