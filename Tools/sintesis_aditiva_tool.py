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
    def __init__(self, editor, name, harm_count, adsr_params):
        super(AditivaInstrument, self).__init__(editor)
        self.name = name
        self.harm_count = harm_count
        self.adsr_params = adsr_params

    def Play(self, note, velocity, duration):
        func, _ = SintesisAditivaTool.CreateFunc(440 * 2**((note - 69)/12), self.harm_count, duration, self.adsr_params)
        return Signal(math_expr=AditivaInstrumentMathExpr(func), duration=duration)

class SintesisAditivaTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis Aditiva Tool", editor=editor, uuid=uuid)
        self.fs = 44100
        self.previous_harmonics = 3
        self.init: bool = False
        self.Init(self.Run)

    @staticmethod
    def create_envelope(use_adsr, duration, attack, decay, sustain, sustain_value, release):
        a_t = MathExpr()

        # Scale times to match overall duration
        total = attack + decay + sustain + release
        attack *= duration / total
        decay *= duration / total
        sustain *= duration / total
        release *= duration / total

        # Phase boundaries
        t1 = attack
        t2 = t1 + decay
        t3 = t2 + sustain
        t4 = t3 + release

        if use_adsr:
            # Linear ADSR (already fixed in previous message)
            e1 = lambda t: (t / attack)
            e2 = lambda t: 1 - (1 - sustain_value) * ((t - t1) / decay)
            e3 = lambda t: sustain_value
            e4 = lambda t: sustain_value * (1 - ((t - t3) / release))
        else:
            # Exponential ADSR
            # Attack: scaled exponential growth from 0 to 1
            e1 = lambda t: (1 - np.exp(-5 * t / attack)) / (1 - np.exp(-5))  # normalizing to reach 1 at t=attack

            # Decay: scaled exponential decay from 1 to sustain_value
            e2 = lambda t: sustain_value + (1 - sustain_value) * np.exp(-5 * (t - t1) / decay)

            # Sustain: hold value
            e3 = lambda t: sustain_value

            # Release: decay from sustain_value to 0
            e4 = lambda t: sustain_value * np.exp(-5 * (t - t3) / release)

        def envelope_function(t):
            conditions = [
                (t >= 0) & (t < t1),
                (t >= t1) & (t < t2),
                (t >= t2) & (t < t3),
                t >= t3
            ]
            return np.piecewise(t, conditions, [e1, e2, e3, e4])

        a_t.math_expression = envelope_function
        return a_t

    @staticmethod
    def CreateFunc(freq, harmonics, duration, adsr_params):
        t = np.linspace(0, duration, int(44100 * duration), endpoint=False)
        y = np.zeros_like(t)
        envelopes = []
        for k in range(1, harmonics + 1):
            a, d, s, s_v, r = adsr_params[k - 1]
            env = SintesisAditivaTool.create_envelope(True, duration, a, d, s, s_v, r)
            y += env(t) * np.sin(2 * np.pi * k * freq * t) * 1/k
            envelopes.append((t, env))
        return lambda t_in: np.interp(t_in, t, y), envelopes

    def update_plot(self):
        freq = img.get_value(self.freq_tag)
        duration = img.get_value(self.dur_tag)

        saved_values = []

        for i in range(1, self.previous_harmonics + 1):
            saved_values.append({
                "Attack": img.get_value(f"attack_{i}"),
                "Decay": img.get_value(f"decay_{i}"),
                "Sustain": img.get_value(f"sustain_{i}"),
                "Sustain Value": img.get_value(f"sustain_value_{i}"),
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
                img.add_slider_float(label=f"Sustain Value{i}", default_value=0.6, min_value=0.0, max_value=1.0,
                                     tag=f"sustain_value_{i}")
                img.add_slider_float(label=f"Release {i}", default_value=0.2, min_value=0.0, max_value=1.0,
                                     tag=f"release_{i}")

        if (self.init == True):
            for i, entry in enumerate(saved_values):
                if i+1> harmonics:
                    break
                img.set_value(f"attack_{i + 1}", entry["Attack"])
                img.set_value(f"decay_{i + 1}", entry["Decay"])
                img.set_value(f"sustain_{i + 1}", entry["Sustain"])
                img.set_value(f"sustain_value_{i + 1}", entry["Sustain Value"])
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
                img.get_value(f"sustain_value_{k}"),
                img.get_value(f"release_{k}")
            ])

        print(adsr_params)

        func, envelopes = self.CreateFunc(freq, harmonics, duration, adsr_params)
        t = np.linspace(0, duration, int(self.fs * duration), endpoint=False)
        y = func(t)

        for idx in range(1, harmonics + 1):
            t_e, env = envelopes[idx - 1]
            img.set_value(f"env_line_{idx}", [t, env(t)])

        self.init = True
        self.previous_harmonics = harmonics

    def play_sound(self):
        duration = img.get_value(self.dur_tag)
        freq = img.get_value(self.freq_tag)
        harmonics = img.get_value("harmonics_slider")
        adsr_params = []
        for k in range(1, harmonics + 1):
            adsr_params.append([
                img.get_value(f"attack_{k}"),
                img.get_value(f"decay_{k}"),
                img.get_value(f"sustain_{k}"),
                img.get_value(f"sustain_value_{k}"),
                img.get_value(f"release_{k}")
            ])
        func, _ = self.CreateFunc(freq, harmonics, duration, adsr_params)
        t = np.linspace(0, duration, int(self.fs * duration), endpoint=False)
        y = func(t).astype(np.float32)
        sd.play(y, self.fs)
        sd.wait()

    def create_instrument(self):
        name = img.get_value("instrument_name")
        freq = img.get_value(self.freq_tag)
        harmonics = img.get_value("harmonics_slider")
        adsr_params = []
        for k in range(1, harmonics + 1):
            adsr_params.append([
                img.get_value(f"attack_{k}"),
                img.get_value(f"decay_{k}"),
                img.get_value(f"sustain_{k}"),
                img.get_value(f"sustain_value_{k}"),
                img.get_value(f"release_{k}")
            ])
        self.editor.AddInstrument(AditivaInstrument(self.editor, name, harmonics, adsr_params))

    def Run(self):
        img.add_input_text(label="Nombre del Instrumento", default_value="MiInstrumento", tag="instrument_name")
        self.dur_tag = img.add_slider_float(label="Duración (s)", default_value=1.0, min_value=0.1, max_value=5.0)
        self.freq_tag = img.add_input_float(label="Frecuencia base (Hz)", default_value=220.0, step=1.0)
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
            "Piano": (
                261.63,
                [
                    [0.01, 0.2, 0.3, 0.7, 0.3] for _ in range(8)
                ]
            ),
            "Guitarra": (
                196.00,
                [
                    [0.02, 0.3, 0.4, 0.6, 0.4] for _ in range(8)
                ]
            ),
            "Violín": (
                440.00,
                [
                    [0.05, 0.1, 0.8, 0.9, 0.2] for _ in range(8)
                ]
            ),
            "Flauta": (
                880.00,
                [
                    [0.1, 0.2, 0.9, 0.8, 0.3] for _ in range(8)
                ]
            ),
            "Clarinete": (
                147.00,
                [
                    [0.03, 0.2, 0.6, 0.7, 0.3] for _ in range(8)
                ]
            ),
            "Trompeta": (
                349.23,
                [
                    [0.02, 0.1, 0.7, 0.8, 0.2] for _ in range(8)
                ]
            )
        }
        selected = img.get_value("preset_selector")
        if selected in presets:
            freq, adsr_list = presets[selected]
            img.set_value(self.freq_tag, freq)
            img.set_value("harmonics_slider", 8)
            self.update_plot()
            for i, (a, d, s, s_v, r) in enumerate(adsr_list):
                img.set_value(f"attack_{i + 1}", a)
                img.set_value(f"decay_{i + 1}", d)
                img.set_value(f"sustain_{i + 1}", s)
                img.set_value(f"sustain_value_{i + 1}", s_v)
                img.set_value(f"release_{i + 1}", r)
            self.update_plot()

