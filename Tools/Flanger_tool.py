from Tool import *
from Instrument import *
from Signal import Signal, MathExpr
import dearpygui.dearpygui as img
import numpy as np
from scipy.signal import butter, lfilter
from numba import *


def _calculate_lowpass_gains(wc, Q):
    K = np.tan(np.pi * (wc))
    norm = 1 / (1 + K / Q + K * K)
    b0 = K * K * norm
    b1 = 2 * b0
    b2 = b0
    a1 = 2 * (K * K - 1) * norm
    a2 = (1 - K / Q + K * K) * norm
    return (b0, b1, b2, a1, a2)

def _calculate_bandpass_gains(wc, Q):
    K = np.tan(np.pi * (wc))
    norm = 1 / (1 + K / Q + K * K)
    b0 = K / Q * norm
    b1 = 0
    b2 = -b0
    a1 = 2 * (K * K - 1) * norm
    a2 = (1 - K / Q + K * K) * norm
    return (b0, b1, b2, a1, a2)

class FlangerPreset:
    def __init__(self, name, params=None):
        self.name = name
        self.params = {
            "tau0": params.get("tau0", 0),
            "delta_tau": params.get("delta_tau", 0),
            "f_LFO": params.get("f_LFO", 0),
            "fs": params.get("fs", 0),
            "depth_factor": params.get("depth_factor", 0),  
        }
    
    def allpass_filter(self, x, f_c, Q):
        w0 = 2 * np.pi * f_c / self.params["fs"]
        alpha = np.sin(w0) / (2 * Q)
        b = [1 - alpha, -2 * np.cos(w0), 1 + alpha]
        a = [1 + alpha, -2 * np.cos(w0), 1 - alpha]
        return lfilter(b, a, x)
        
    
    def apply(self, signal):
        if signal.duration is not None:
            t, x = signal.GetData(total_samples=int(self.params["fs"] * signal.duration))
        else:
            t, x = signal.GetData()
        N = len(x)
        t = np.asarray(t)
        tau_t = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * self.params["f_LFO"] * t)
            
        if self.name == "Vibrato":
            delay = (tau_t * self.params["fs"]).astype(int)
            y = np.zeros_like(x)
            for i in range(len(x)):
                d = delay[i] if i - delay[i] >= 0 else 0
                y[i] = x[i - d] if d > 0 else x[i]
            return y, t
        
        elif self.name == "Chorus":
            y = x.copy()
            voices = 3      # Número de voces para el efecto chorus
            alpha = self.params["depth_factor"]
            for i in range(voices):
                f_lfo_i = self.params["f_LFO"] + 0.2 * i
                tau_i = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * f_lfo_i * t)
                delay = (tau_i * self.params["fs"]).astype(int)
                for j in range(len(x)):
                    d = delay[j] if j - delay[j] >= 0 else 0
                    y[j] += (alpha / (voices + i)) * x[j - d] if d > 0 else 0
            y += x
            return y, t
            
        elif self.name == "Phaser":    
            y = x.copy()
            f_center = 800
            delta_f = 600
            f_mod = f_center + delta_f * np.sin(2 * np.pi * self.params["f_LFO"] * t)
            for i in range(3):
                y = self.allpass_filter(y, f_mod[i], Q=0.5)
            return x + self.params["depth_factor"] * y, t
        
        elif self.name == "Wah-wah":
            f_center = self.params["fs"] / 2
            delta_f = self.params["fs"] / 2
            Q = 6
            mixer = 0.2
            f_mod = f_center + delta_f * np.sin(2 * np.pi * self.params["f_LFO"] * t)
            f_mod = np.clip(f_mod, 0.001, self.params["fs"] / 2 - 0.1)
            if np.isscalar(x):
                x = np.array([x], dtype=np.float32)


            if np.isscalar(f_mod):
                f_mod = np.array([f_mod] * len(x), dtype=np.float32)


            ys = np.zeros(len(x), dtype=np.float64)

            for i in range(2, len(x)):
                b0, b1, b2, a1, a2 = _calculate_lowpass_gains(f_mod[i] / self.params["fs"], Q)
                y = (
                        b2 * x[i - 2]
                        + b1 * x[i - 1]
                        + b0 * x[i]
                        - a1 * ys[i - 1]
                        - a2 * ys[i - 2]
                )
                ys[i] = y

            ys += x * np.asarray([mixer] * len(x))


            return ys, t
            
        else:       # Flanger effect (uso esta por defecto)
            delay = (tau_t * self.params["fs"]).astype(int)
            y = np.zeros_like(x)
            for i in range(len(x)):
                d = delay[i] if i - delay[i] >= 0 else 0
                y[i] = x[i] + self.params["depth_factor"] * x[i - d] if d > 0 else x[i]
            return y, t
        
        

        # Calcular retardo en muestras (en vez de segundos)
        # tau_t = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * self.params["f_LFO"] * t)
        # delay_samples = (tau_t * self.params["fs"]).astype(np.int32)

        # # Inicializar salida
        # y = np.zeros(N)

        # for n in range(N):
        #     d = delay_samples[n]
        #     if n - d >= 0:
        #         y[n] = x[n] + self.params["depth_factor"] * x[n - d]
        #     else:
        #         y[n] = x[n]  # No hay retardo al comienzo

        # return y, t
    
    def calculate_Hf(self, signal, f):
        time, x = signal.GetData()       # Uso Ydata ya que y=x(t)
        N = len(x)
        t = np.arange(N) / self.params["fs"]
        
        tau_t = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * self.params["f_LFO"] * t)
            
        if self.name == "Vibrato":
            print("-----------------------------------") 
            print("No tiene H(f) definido para vibrato")
            print("-----------------------------------")            
            
            return None, t
        
        elif self.name == "Chorus":
            H = 1
            for i in range(3):
                f_lfo_i = self.params["f_LFO"] + 0.2 * i
                tau_i = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * f_lfo_i * t)
                H += (self.params["depth_factor"] / 3) * np.exp(-1j * 2 * np.pi * f * tau_i)
            return np.abs(H), t
            
        elif self.name == "Phaser":
            print("---------------------------------------------------------------------") 
            print("H(f)muy compleja de estimar para phaser, depende del filtro utilizado")
            print("---------------------------------------------------------------------") 
            
            return None, t
            
        
        elif self.name == "Wah-wah":
            print("---------------------------------------------------------------------") 
            print("H(f)muy compleja de estimar para wah-wah, depende del filtro utilizado")
            print("---------------------------------------------------------------------") 
            
            return None, t
            
            
        else:       # Flanger effect (uso esta por defecto)
            return np.abs(1 + self.params["depth_factor"] * np.exp(-1j * 2 * np.pi * f * tau_t)), t

        
        
        
        # tau = self.params["tau0"] + self.params["delta_tau"] * np.sin(2 * np.pi * self.params["f_LFO"] * t)
        # H = 1 + self.params["depth_factor"] * np.exp(-1j * 2 * np.pi * f * tau)
        # return np.abs(H), t


FLANGERS_PRESETS = [
        FlangerPreset("Vibrato", params={
            "tau0": 0.005, 
            "delta_tau": 0.002, 
            "f_LFO": 5, 
            "fs": 44100, 
            "depth_factor": 0.5
        }),
        FlangerPreset("Chorus", params={
            "tau0": 0.01,
            "delta_tau": 0.005,
            "f_LFO": 1,
            "fs": 44100,
            "depth_factor": 0.7
        }),
        FlangerPreset("Flanger", params={
            "tau0": 0.01,
            "delta_tau": 0.005,
            "f_LFO": 0.25,
            "fs": 44100,
            "depth_factor": 0.8
        }),
        FlangerPreset("Phaser", params={
                "tau0": 0.02,
                "delta_tau": 0.01,
                "f_LFO": 0.5,
                "fs": 44100,
                "depth_factor": 0.6
        }),
        FlangerPreset("Wah-wah", params={
                "tau0": 0.03,
                "delta_tau": 0.015,
                "f_LFO": 0.75,
                "fs": 44100,
                "depth_factor": 0.9
        })
    ]



class FlangerTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="Flanger Tool", editor=editor, uuid=uuid)
        f=10
        fs=44100
        dur=1.0
        self.output_signal = None
        t = np.linspace(0, dur, int(fs * dur), endpoint=False)
        self.signal = Signal(math_expr=MathExpr(math_expression= lambda t : (np.sin(2 * np.pi * f * t))))
        
        self.flanger_preset = None
        
        self.Init(self.Run)
        
    def paste_signal(self):
        self.signal = self.editor.selected_signal

    def save_signal(self):
        if self.output_signal is not None:
            self.editor.AddSignal(self.output_signal)

    def Run(self):
        img.add_text("Seleccionar Flanger")
        img.add_button(label="Paste Signal", callback= lambda: self.paste_signal())
        with img.group(horizontal=True):
            for preset in FLANGERS_PRESETS:
                def make_callback(preset):
                    return lambda sender, app_data: self.set_preset(preset)

                img.add_button(label=preset.name, callback=make_callback(preset))
                
        img.add_slider_int(label="Freuencia fija para evaluar la transferencia", default_value=10, min_value=1, max_value=20000, tag="f_slider", parent=self.tab)
        img.add_slider_int(label="Frecuencia de muestreo", default_value=44100, min_value=1, max_value=100000, tag="fs_slider", callback=self.updateparams, parent=self.tab)
        img.add_slider_float(label="Profundidad del efecto", default_value=0.5, min_value=0.0, max_value=1.0, tag="depth_factor_slider", callback=self.updateparams, parent=self.tab)
        img.add_slider_float(label="tau0", default_value=0.03, min_value=0.001, max_value=0.5, tag="tau0_slider", callback=self.updateparams, parent=self.tab)
        img.add_slider_float(label="delta_tau", default_value=0.015, min_value=0.0001, max_value=0.25, tag="delta_tau_slider", callback=self.updateparams, parent=self.tab)
        img.add_slider_float(label="Frecuencia LFO", default_value=0.75, min_value=0.0, max_value=10.0, tag="f_LFO_slider", callback=self.updateparams, parent=self.tab)
        
        img.add_button(label="Actualizar gráficos", callback=self.update_plot, parent=self.tab)
        img.add_button(label="Save Signal", callback=lambda : self.save_signal(), parent=self.tab)
        with img.plot(label="Señal en el Tiempo", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            xt1 = img.add_plot_axis(img.mvXAxis)
            yt1 = img.add_plot_axis(img.mvYAxis)
            self.signal_plot = img.add_line_series([], [], parent=yt1)
        
        with img.plot(label="Función de flanger", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            xt2 = img.add_plot_axis(img.mvXAxis)
            yt2 = img.add_plot_axis(img.mvYAxis)
            self.flanger_plot = img.add_line_series([], [], parent=yt2)
            
        with img.plot(label="Transferenia de la función de flanger", width=-1, height=300, parent=self.tab):
            img.add_plot_legend()
            xt3 = img.add_plot_axis(img.mvXAxis)
            yt3 = img.add_plot_axis(img.mvYAxis)
            self.flanger_Hf_plot = img.add_line_series([], [], parent=yt3)
            

    def updateparams(self):
        if self.flanger_preset is None:                         # Version custom de Flanger
            
            self.flanger_preset = FlangerPreset("Custom", params={
                "tau0": img.get_value("tau0_slider"),
                "delta_tau": img.get_value("delta_tau_slider"),
                "f_LFO": img.get_value("f_LFO_slider"),
                "fs": img.get_value("fs_slider"),
                "depth_factor": img.get_value("depth_factor_slider")
                })      
        else:            
            self.flanger_preset.params["depth_factor"] = img.get_value("depth_factor_slider")
            self.flanger_preset.params["tau0"] = img.get_value("tau0_slider")
            self.flanger_preset.params["delta_tau"] = img.get_value("delta_tau_slider")
            self.flanger_preset.params["f_LFO"] = img.get_value("f_LFO_slider")
            self.flanger_preset.params["fs"] = img.get_value("fs_slider")
        
        self.update_plot()
        
           
    def set_preset(self, preset):
        self.flanger_preset = preset
        
        img.set_value("tau0_slider", preset.params["tau0"])
        img.set_value("delta_tau_slider", preset.params["delta_tau"])
        img.set_value("f_LFO_slider", preset.params["f_LFO"])
        img.set_value("depth_factor_slider", preset.params["depth_factor"])
        
        self.update_plot()
        
        
    def update_plot(self):
        frequency = img.get_value("f_slider")
        
        # Plot signal
        x, y = self.signal.GetData()
        img.set_value(self.signal_plot, [list(x), list(y)])
        
        if self.flanger_preset is None:
            return
        
        flanger, t = self.flanger_preset.apply(self.signal)

        def interpolator_func(x):
            if x <= t[0]:
                return flanger[0]
            elif x >= t[-1]:
                return flanger[-1]

                # Find the index where query_time fits
            idx = np.searchsorted(t, x) - 1
            t0, t1 = t[idx], t[idx + 1]
            y0, y1 = flanger[idx], flanger[idx + 1]

            # Linear interpolation
            ratio = (x - t0) / (t1 - t0)
            return y0 + ratio * (y1 - y0)

        self.output_signal = Signal(duration=t[-1], math_expr=MathExpr(math_expression=interpolator_func))

        img.set_value(self.flanger_plot, [list(t), list(flanger)])
        
        Hf, t_Hf = self.flanger_preset.calculate_Hf(self.signal, frequency)
        
        if Hf is None:
            img.set_value(self.flanger_Hf_plot, [[], []])
        
        else:        
            img.set_value(self.flanger_Hf_plot, [list(t_Hf), list(Hf)])
        
        
        
        
        
        
        
        
    
    