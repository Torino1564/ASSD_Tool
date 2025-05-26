from Tool import *
from Instrument import *


class InstrumentoAditivo(Instrument):
    def __init__(self, editor):
        super().__init__(editor)
        self.attack = None
        self.sustain = None
        self.decay = None
        self.release = None

    def Play(self, note, velocity, duration):
        return 0


class SintesisAditivaTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis Aditiva Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)

    def Run(self):
        img.add_child_window()
        # Desarrollo paso a paso de la herramienta "Sintesis Aditiva Tool"


# Esto incluye la generación de la GUI en DearPyGui, selección de instrumento,
# sliders de control y visualización en tiempo real de la señal sintetizada.

from Tool import *
from Signal import Signal, MathExpr
import dearpygui.dearpygui as img
import numpy as np


class InstrumentoPreset:
    def __init__(self, name, partials, adsr):
        self.name = name
        self.partials = partials  # Lista de (n, amplitud) donde n es el multiplicador de f0
        self.adsr = adsr  # Diccionario con keys: attack, decay, sustain, release, k, alpha


# === Presets de instrumentos reales (valores aproximados obtenidos de literatura y análisis espectral) ===
INSTRUMENT_PRESETS = [
    InstrumentoPreset("Flauta", [(1, 1.0), (2, 0.5), (3, 0.2), (4, 0.1)],
                      {"attack": 0.05, "decay": 0.1, "sustain": 0.7, "release": 0.2, "k": 1.2, "alpha": 0.3}),
    InstrumentoPreset("Clarinete", [(1, 1.0), (3, 0.6), (5, 0.3), (7, 0.15)],
                      {"attack": 0.02, "decay": 0.08, "sustain": 0.6, "release": 0.3, "k": 1.3, "alpha": 0.2}),
    InstrumentoPreset("Violin", [(1, 1.0), (2, 0.8), (3, 0.6), (4, 0.4), (5, 0.2)],
                      {"attack": 0.01, "decay": 0.1, "sustain": 0.5, "release": 0.3, "k": 1.5, "alpha": 0.25}),
    InstrumentoPreset("Trompeta", [(1, 1.0), (2, 0.7), (3, 0.4), (4, 0.3), (5, 0.1)],
                      {"attack": 0.03, "decay": 0.1, "sustain": 0.8, "release": 0.4, "k": 1.1, "alpha": 0.35}),
    InstrumentoPreset("Guitarra", [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.2), (5, 0.1)],
                      {"attack": 0.02, "decay": 0.2, "sustain": 0.4, "release": 0.5, "k": 1.3, "alpha": 0.4}),
    InstrumentoPreset("Piano", [(1, 1.0), (2, 0.7), (3, 0.4), (4, 0.25), (5, 0.1)],
                      {"attack": 0.01, "decay": 0.15, "sustain": 0.5, "release": 0.3, "k": 1.4, "alpha": 0.5})
]


class SintesisAditivaTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis Aditiva Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)

    def Run(self):
        self.duration_tag = img.add_slider_float(label="Duración (s)", default_value=1.0, min_value=0.1, max_value=5.0)
        self.attack_tag = img.add_slider_float(label="Attack (s)", default_value=0.05, min_value=0.001, max_value=1.0)
        self.decay_tag = img.add_slider_float(label="Decay (s)", default_value=0.1, min_value=0.001, max_value=1.0)
        self.sustain_tag = img.add_slider_float(label="Sustain (0-1)", default_value=0.7, min_value=0.0, max_value=1.0)
        self.release_tag = img.add_slider_float(label="Release (s)", default_value=0.2, min_value=0.001, max_value=2.0)
        self.k_tag = img.add_slider_float(label="Factor de Ataque (k)", default_value=1.2, min_value=1.0, max_value=2.0)
        self.alpha_tag = img.add_slider_float(label="Pendiente Alpha", default_value=0.3, min_value=0.0, max_value=1.0)

        self.plot_tag = None
        with img.plot(label="Señal Aditiva", width=-1, height=300) as self.plot_tag:
            x_axis = img.add_plot_axis(img.mvXAxis, label="Tiempo")
            y_axis = img.add_plot_axis(img.mvYAxis, label="Amplitud")
            self.line_series = img.add_line_series([], [], parent=y_axis)

        img.add_button(label="Actualizar Grafico", callback=self.update_plot)

        img.add_text("Instrumentos:")
        with img.group(horizontal=True):
            for preset in INSTRUMENT_PRESETS:
                def make_callback(preset):
                    return lambda sender, app_data: self.set_preset(preset)

                img.add_button(label=preset.name, callback=make_callback(preset))

    def set_preset(self, preset):
        self.selected_partials = preset.partials
        img.set_value(self.attack_tag, preset.adsr["attack"])
        img.set_value(self.decay_tag, preset.adsr["decay"])
        img.set_value(self.sustain_tag, preset.adsr["sustain"])
        img.set_value(self.release_tag, preset.adsr["release"])
        img.set_value(self.k_tag, preset.adsr["k"])
        img.set_value(self.alpha_tag, preset.adsr["alpha"])
        self.update_plot()

    def update_plot(self):
        duration = img.get_value(self.duration_tag)
        A = img.get_value(self.attack_tag)
        D = img.get_value(self.decay_tag)
        S = img.get_value(self.sustain_tag)
        R = img.get_value(self.release_tag)
        k = img.get_value(self.k_tag)
        alpha = img.get_value(self.alpha_tag)

        if not hasattr(self, 'selected_partials'):
            self.selected_partials = [(1, 1.0)]

        fs = 44100
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        envelope = self.adsr_envelope(t, A, D, S, R, k, alpha, duration)

        y = envelope
        img.set_value(self.line_series, [t.tolist(), y.tolist()])

    def adsr_envelope(self, t, A, D, S, R, k, alpha, T):
        env = np.zeros_like(t)
        A0 = 1.0
        A_end = A
        D_end = A + D
        R_start = T - R

        for i, ti in enumerate(t):
            if ti < A_end:
                env[i] = (ti / A_end) * (k * A0)
            elif ti < D_end:
                env[i] = k * A0 - ((k * A0 - A0) * (ti - A_end) / D)
            elif ti < R_start:
                env[i] = max(0, A0 - alpha * (ti - D_end))
            elif ti < T:
                env[i] = env[i - 1] * (1 - (ti - R_start) / R)
        return env
