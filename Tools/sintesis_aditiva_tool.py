# sintesis_aditiva_tool.py

from Tool import *
from Instrument import *
import dearpygui.dearpygui as img
import numpy as np
import sounddevice as sd
from utl import Math

class AditivaInstrumentMathExpr(MathExpr):
    def __init__(self, mathexpr):
        MathExpr.__init__(self, mathexpr)
    def __call__(self, x: float):
        return self.math_expression(x)
    def EvaluatePoints(self, xValues: list[float]):
        return self.math_expression(xValues)

class AditivaInstrument(Instrument):
    def __init__(self, editor, name, freq, harm_count, adsr_params):
        super(AditivaInstrument, self).__init__(editor)
        self.name = name
        self.freq = freq
        self.harm_count = harm_count
        self.adsr_params = adsr_params

    def Play(self, note, velocity, duration):
        func, _ = SintesisAditivaTool.CreateFunc(440 * 2**((note - 69)/12), self.harm_count, duration, self.adsr_params)
        return Signal(math_expr=AditivaInstrumentMathExpr(func), duration=duration)

def adsr_envelope(t, duration, attack, decay, sustain, release):
    a_samples = int(attack * len(t) / duration)
    d_samples = int(decay * len(t) / duration)
    r_samples = int(release * len(t) / duration)
    s_samples = len(t) - (a_samples + d_samples + r_samples)
    envelope = np.zeros_like(t)
    envelope[:a_samples] = np.linspace(0, 1, a_samples)
    envelope[a_samples:a_samples + d_samples] = np.linspace(1, sustain, d_samples)
    envelope[a_samples + d_samples:a_samples + d_samples + s_samples] = sustain
    envelope[-r_samples:] = np.linspace(sustain, 0, r_samples)
    return envelope

class SintesisAditivaTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis Aditiva Tool", editor=editor, uuid=uuid)
        self.fs = 44100
        self.previous_harmonics = 3
        self.init: bool = False
        self.Init(self.Run)


    @staticmethod
    def CreateFunc(freq, harmonics, duration, adsr_params):
        t = np.linspace(0, duration, int(44100 * duration), endpoint=False)
        y = np.zeros_like(t)
        envelopes = []
        for k in range(1, harmonics + 1):
            a, d, s, r = adsr_params[k - 1]
            env = adsr_envelope(t, duration, a, d, s, r)
            y += env * np.sin(2 * np.pi * k * freq * t)
            envelopes.append((t, env))
        return lambda t_in: np.interp(t_in, t, y), envelopes

    def update_plot(self):
        freq = img.get_value("freq_input")
        duration = img.get_value("dur_slider")

        saved_values = []

        for i in range(1, self.previous_harmonics + 1):
            saved_values.append({
                "Attack": img.get_value(f"attack_{i}"),
                "Decay": img.get_value(f"decay_{i}"),
                "Sustain": img.get_value(f"sustain_{i}"),
                "Release": img.get_value(f"release_{i}")
            })

        harmonics = img.get_value("harmonics_slider")

        # Eliminar sliders antiguos
        img.delete_item("SLIDER_GROUP_TAG", children_only=True)
        img.delete_item("PLOT_GROUP_TAG", children_only=True)

        # Crear nuevos sliders según K
        for i in range(1, harmonics + 1):
            with img.group(horizontal=False, tag=f"env_group_{i}", parent="SLIDER_GROUP_TAG"):
                img.add_text(f"Armónico {i}")
                img.add_slider_float(label=f"Attack {i}", default_value=0.01, min_value=0.0, max_value=1.0,
                                     tag=f"attack_{i}")
                img.add_slider_float(label=f"Decay {i}", default_value=0.1, min_value=0.0, max_value=1.0,
                                     tag=f"decay_{i}")
                img.add_slider_float(label=f"Sustain {i}", default_value=0.6, min_value=0.0, max_value=1.0,
                                     tag=f"sustain_{i}")
                img.add_slider_float(label=f"Release {i}", default_value=0.2, min_value=0.0, max_value=2.0,
                                     tag=f"release_{i}")

        if (self.init == True):
            for i, entry in enumerate(saved_values):
                if i+1> harmonics:
                    break
                img.set_value(f"attack_{i + 1}", entry["Attack"])
                img.set_value(f"decay_{i + 1}", entry["Decay"])
                img.set_value(f"sustain_{i + 1}", entry["Sustain"])
                img.set_value(f"release_{i + 1}", entry["Release"])

        for k in range(1, harmonics + 1):
            with img.plot(label=f"Envelope Armónico {k}", height=150, tag=f"env_plot_{k}", parent="PLOT_GROUP_TAG"):
                x = img.add_plot_axis(img.mvXAxis, label="Tiempo")
                y = img.add_plot_axis(img.mvYAxis, label="Amplitud")
                img.add_line_series([], [], parent=y, tag=f"env_line_{k}")


        adsr_params = []
        for k in range(1, harmonics + 1):
            adsr_params.append([
                img.get_value(f"attack_{k}"),
                img.get_value(f"decay_{k}"),
                img.get_value(f"sustain_{k}"),
                img.get_value(f"release_{k}")
            ])

        print(adsr_params)

        func, envelopes = self.CreateFunc(freq, harmonics, duration, adsr_params)
        t = np.linspace(0, duration, int(self.fs * duration), endpoint=False)
        y = func(t)

        for idx in range(1, harmonics + 1):
            t_e, env = envelopes[idx - 1]
            img.set_value(f"env_line_{idx}", [t_e.tolist(), env.tolist()])

        self.init = True
        self.previous_harmonics = harmonics

    def play_sound(self):
        if hasattr(self, 'sig_line'):
            duration = img.get_value(self.duration_tag)
            freq = img.get_value("freq_input")
            harmonics = img.get_value("harmonics_slider")
            adsr_params = []
            for k in range(1, harmonics + 1):
                adsr_params.append([
                    img.get_value(f"attack_{k}"),
                    img.get_value(f"decay_{k}"),
                    img.get_value(f"sustain_{k}"),
                    img.get_value(f"release_{k}")
                ])
            func, _ = self.CreateFunc(freq, harmonics, duration, adsr_params)
            t = np.linspace(0, duration, int(self.fs * duration), endpoint=False)
            y = func(t).astype(np.float32)
            sd.play(y, self.fs)
            sd.wait()

    def create_instrument(self):
        name = img.get_value("instrument_name")
        freq = img.get_value("freq_input")
        harmonics = img.get_value("harmonics_slider")
        adsr_params = []
        for k in range(1, harmonics + 1):
            adsr_params.append([
                img.get_value(f"attack_{k}"),
                img.get_value(f"decay_{k}"),
                img.get_value(f"sustain_{k}"),
                img.get_value(f"release_{k}")
            ])
        self.editor.AddInstrument(AditivaInstrument(self.editor, name, freq, harmonics, adsr_params))

    def Run(self):
        with img.window(label="Síntesis Aditiva", width=520, height=1000):
            img.add_input_text(label="Nombre del Instrumento", default_value="MiInstrumento", tag="instrument_name")
            img.add_slider_float(label="Duración (s)", default_value=1.0, min_value=0.1, max_value=5.0, tag="dur_slider")
            img.add_input_float(label="Frecuencia base (Hz)", default_value=220.0, tag="freq_input", step=1.0)
            img.add_slider_int(label="Cantidad de armónicos", default_value=3, min_value=1, max_value=8, tag="harmonics_slider", callback=self.update_plot)

            img.add_group(tag="SLIDER_GROUP_TAG")
            img.add_group(tag="PLOT_GROUP_TAG")

            img.add_button(label="Actualizar Gráficos", callback=self.update_plot)
            img.add_button(label="Reproducir Sonido", callback=self.play_sound)
            img.add_button(label="Guardar Instrumento", callback=self.create_instrument)

            img.add_combo(
                label="Preset de instrumento",
                items=["Piano", "Guitarra", "Violín", "Flauta", "Clarinete", "Trompeta"],
                default_value="Piano",
                tag="preset_selector"
            )
            img.add_button(label="Cargar Instrumento Prearmado", callback=self.load_preset)

            self.update_plot()

    def load_preset(self):
        presets = {
            "Piano": (261.63, [[0.01 + i * 0.005, 0.4 + i * 0.01, 0.3 - i * 0.03, 1.0 - i * 0.05] for i in range(8)]),
            "Guitarra": (
            196.00, [[0.01 + i * 0.004, 0.3 + i * 0.01, 0.5 - i * 0.02, 0.8 - i * 0.04] for i in range(8)]),
            "ViolÃn": (440.00, [[0.2 - i * 0.01, 0.3 - i * 0.01, 0.8 - i * 0.02, 0.3 - i * 0.01] for i in range(8)]),
            "Flauta": (880.00, [[0.05 + i * 0.005, 0.2, 0.9 - i * 0.01, 0.5 - i * 0.02] for i in range(8)]),
            "Clarinete": (147.00, [[0.03, 0.2 + i * 0.005, 0.6 - i * 0.02, 0.6 - i * 0.03] for i in range(8)]),
            "Trompeta": (349.23, [[0.05 + i * 0.003, 0.2 + i * 0.01, 0.7 - i * 0.02, 0.4 - i * 0.01] for i in range(8)])
        }
        selected = img.get_value("preset_selector")
        if selected in presets:
            freq, adsr_list = presets[selected]
            img.set_value("freq_input", freq)
            img.set_value("harmonics_slider", 8)
            for i, (a, d, s, r) in enumerate(adsr_list):
                img.set_value(f"attack_{i + 1}", a)
                img.set_value(f"decay_{i + 1}", d)
                img.set_value(f"sustain_{i + 1}", s)
                img.set_value(f"release_{i + 1}", r)
            self.update_plot()
