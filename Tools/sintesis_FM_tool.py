from Tool import *
from Instrument import *
import dearpygui.dearpygui as img
import numpy as np
import sounddevice as sd

from utl import Math


class FMInstrumentMathExpr(MathExpr):
    def __init__(self, mathexpr):
        MathExpr.__init__(self, mathexpr)

    def __call__(self, x: float):
        return self.math_expression(x)

    def EvaluatePoints(self, xValues: list[float]):
        return self.math_expression(xValues)

class FMInstrument(Instrument):
    def __init__(self, editor, mod_freq_mult, it_gain, it_decay, use_adsr, attack, decay, sustain, sustain_value, release):
        super(FMInstrument, self).__init__(editor)
        self.name = 'Sintesis_FM_tool'
        self.freq_mult = mod_freq_mult
        self.it_gain = it_gain
        self.it_decay = it_decay
        self.use_adsr = use_adsr
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.sustain_value = sustain_value
        self.release = release

    def Play(self, note, velocity, duration):
        func, at = SintesisFMTool.CreateFunc(440 * 2 ** ((note - 69) / 12), self.freq_mult,
                                  self.it_gain, self.it_decay, self.use_adsr,
                                  duration, self.attack, self.decay, self.sustain, self.sustain_value,
                                  self.release)
        return Signal(math_expr=FMInstrumentMathExpr(func),
                      duration=duration)


def fm_clarinet(fc, duration=2.0, fm_ratio=1.5, mod_index=2.0, fs=44100):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    A = np.exp(-3 * t) * (1 - np.exp(-5 * t))  # Envelope
    fm = fm_ratio * fc
    modulator = np.sin(2 * np.pi * fm * t)
    y = A * np.sin(2 * np.pi * fc * t + mod_index * modulator)
    return t, y


def adsr_envelope(t, duration, attack, decay, sustain, sustain_value, release):
    total = attack + decay + sustain + release
    t_attack = attack / total
    t_decay = decay / total
    t_sustain = sustain / total
    t_release = release / total
    a_samples = int(t_attack * len(t))
    d_samples = int(t_decay * len(t))
    r_samples = int(t_release * len(t))
    s_samples = len(t) - a_samples - d_samples - r_samples
    envelope = np.zeros_like(t)
    if len(envelope.tolist()) <= a_samples + d_samples + r_samples + s_samples:
        print("error")

    envelope[:a_samples] = np.linspace(0, 1, a_samples)
    envelope[a_samples:a_samples + d_samples] = np.linspace(1, sustain_value, d_samples)
    envelope[a_samples + d_samples:a_samples + d_samples + s_samples] = sustain_value
    envelope[a_samples + d_samples + s_samples:] = np.linspace(sustain_value, 0, r_samples)
    return envelope


class SintesisFMTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Sintesis FM Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.t = None
        self.y = None
        self.fs = None

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
    def CreateFunc(freq, mod_freq_mult, it_gain, it_decay, use_adsr, duration, attack, decay, sustain, sustain_value, release):
        a_t = SintesisFMTool.create_envelope(use_adsr, duration, attack, decay, sustain, sustain_value, release)
        i_t = lambda t: it_gain * np.exp(-1 * it_decay * t / duration)
        mod_freq = freq * mod_freq_mult
        func = lambda t: a_t(t) * np.sin(2 * np.pi * freq * t + i_t(t) * np.sin(2 * np.pi * mod_freq * t))
        return func, a_t

    def update_plot(self):
        freq = img.get_value("freq_input")
        duration = img.get_value(self.duration_tag)
        fs = 44100
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)

        func, a_t = self.CreateFunc(freq, img.get_value("mod_freq"), img.get_value("it_gain"),
                                    img.get_value("it_decay"),
                                    img.get_value("ADSR_bool"), img.get_value(self.duration_tag),
                                    attack=img.get_value("attack")
                                    , decay=img.get_value("decay")
                                    , sustain=img.get_value("sustain")
                                    ,sustain_value=img.get_value("sustain_value")
                                    , release=img.get_value("release"))
        y = func(t)
        a_t_list = a_t(t)
        self.t = t
        self.y = y
        self.fs = fs

        # Update plots
        img.set_value(self.fm_line, [t.tolist(), y.tolist()])
        img.set_value(self.env_line, [t.tolist(), a_t_list])

    def fm_clarinet(self):
        if self.y is not None and self.fs is not None:
            y = np.asarray(self.y, dtype=np.float32)
            sd.play(y, self.fs)
            sd.wait()
        else:
            print("No signal to play. Run 'update_plot' first.")

    def Run(self):
        with img.window(label="FM Clarinet Synth", width=500, height=850):
            img.add_slider_float(label="Duración (s)", default_value=1.0, min_value=0.1, max_value=5.0,
                                 tag="dur_slider")
            self.duration_tag = "dur_slider"

            img.add_input_float(label="Frecuencia (Hz)", default_value=147.0, tag="freq_input", step=1.0)
            img.add_checkbox(label="Usar ADSR", default_value=True, tag="ADSR_bool")

            # ADSR Controls
            img.add_text("ADSR Envelope:")
            img.add_slider_float(label="Attack (s)", default_value=0.05, min_value=0.01, max_value=1.0, tag="attack")
            img.add_slider_float(label="Decay (s)", default_value=0.1, min_value=0.01, max_value=1.0, tag="decay")
            img.add_slider_float(label="Sustain (s)", default_value=0.3, min_value=0.0, max_value=1.0, tag="sustain")
            img.add_slider_float(label="Sustain Value(0–1)", default_value=0.6, min_value=0.0, max_value=1.0, tag="sustain_value")
            img.add_slider_float(label="Release (s)", default_value=0.2, min_value=0.01, max_value=2.0, tag="release")

            img.add_slider_float(label="I(t) Gain ", default_value=5, min_value=0.01, max_value=10.0, tag="it_gain")
            img.add_slider_float(label="I(t) Decay rate ", default_value=4, min_value=0.01, max_value=10.0,
                                 tag="it_decay")
            img.add_slider_float(label="Mod Freq Multiplier", default_value=3, min_value=0.01, max_value=100.0,
                                 tag="mod_freq")

            # Plot: FM signal
            self.plot_tag = None
            with img.plot(label="Señal FM (Clarinet)", height=200) as self.fm_plot:
                x1 = img.add_plot_axis(img.mvXAxis, label="Tiempo")
                y1 = img.add_plot_axis(img.mvYAxis, label="Amplitud")
                self.fm_line = img.add_line_series([], [], parent=y1)

            # Plot: Amplitude envelope
            with img.plot(label="Envelope A(t)", height=200) as self.env_plot:
                x2 = img.add_plot_axis(img.mvXAxis, label="Tiempo")
                y2 = img.add_plot_axis(img.mvYAxis, label="Amplitud")
                self.env_line = img.add_line_series([], [], parent=y2)

            img.add_button(label="Actualizar Gráficos", callback=self.update_plot)
            img.add_button(label="Reproducir Sonido", callback=self.fm_clarinet)

            def AddInstrument():
                self.editor.AddInstrument(FMInstrument(self.editor,
                                                       img.get_value("mod_freq"), img.get_value("it_gain"),
                                                       img.get_value("it_decay"),
                                                       img.get_value("ADSR_bool"),
                                                       attack=img.get_value("attack")
                                                       , decay=img.get_value("decay")
                                                       , sustain=img.get_value("sustain")
                                                       , sustain_value=img.get_value("sustain_value")
                                                       , release=img.get_value("release")))

            img.add_button(label="Add instrument", callback=lambda: AddInstrument())
