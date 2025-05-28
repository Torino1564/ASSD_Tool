import numpy as np
import soundfile as sf
import dearpygui.dearpygui as img
from Tool import Tool
import scipy
from Instrument import *
import librosa
import psola


class SampleInstrument(Instrument):
    def __init__(self, editor, data, original_sample_rate, original_freq, name="Sample Instrument"):
        super().__init__(editor)
        self.name = name
        self.data = data
        self.original_sample_rate = original_sample_rate
        self.original_freq = original_freq

    def Play(self, note, velocity, duration):

        f0_clean = self.original_freq[~np.isnan(self.original_freq)]
        target_f0 = self.original_freq * (440 * 2 ** ((note - 69) / 12)) / f0_clean[0]

        shifted = psola.vocode(
            self.data,
            sample_rate=self.original_sample_rate,
            target_pitch=target_f0,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            constant_stretch=None
        )

        # Convert stereo to mono if needed
        if shifted.ndim == 2 and shifted.shape[1] == 2:
            shifted = np.mean(shifted, axis=1)

        shifted = np.asarray(shifted)

        sample_indices = np.arange(len(shifted))

        def func(x):
            index = x * self.original_sample_rate
            return np.interp(index, sample_indices, shifted, left=0.0, right=0.0)

        duration = len(shifted) / self.original_sample_rate
        return Signal(math_expr=MathExpr(math_expression=func), duration=duration)


class SampleSynthTool(Tool):
    def __init__(self, editor, uuid, tab: bool = True):
        Tool.__init__(self, name="SampleSynthTool", editor=editor, uuid=uuid)
        self.sr = None
        self.file_path_tag = None
        self.target_freq_tag = None
        self.audio = None
        self.f0 = None
        self.shifted = None
        self.sample_data = None
        self.sample_rate = None
        self.file_path = None
        if tab:
            self.Init(self.Run)

    def Run(self):

        img.add_button(label="Create Instrument", callback=lambda: self.CreateInstrument())

        self.file_path_tag = img.add_input_text(label="Sample Path", default_value="sample.wav")
        self.target_freq_tag = img.add_input_float(label="Target Frequency", default_value=440)
        img.add_button(label="Load Sample", callback=self.LoadSample)
        img.add_button(label="Synthesize Note", callback=self.SynthesizeNote)

    def LoadSample(self):
        with img.file_dialog(directory_selector=False, show=True, callback=self.FileSelected, width=500, height=400):
            img.add_file_extension(".wav", color=(150, 255, 150, 255))
            img.add_file_extension(".mp3", color=(150, 255, 150, 255))

    def FileSelected(self, sender, app_data):
        self.file_path = app_data[0] if isinstance(app_data, (list, tuple)) else app_data
        img.set_value(self.file_path_tag, self.file_path)
        self.audio, self.sr = librosa.load(self.file_path["file_path_name"], sr=None)
        self.f0, voiced_flag, voiced_probabilities = librosa.pyin(
            self.audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=self.sr
        )

        # Replace unvoiced frames with NaN
        self.f0 = np.where(voiced_flag, self.f0, np.nan)

    def SynthesizeNote(self):
        f0_clean = self.f0[~np.isnan(self.f0)]
        target_f0 = self.f0 * img.get_value(self.target_freq_tag) / f0_clean[0]
        target_f0_clean = target_f0[~np.isnan(target_f0)]

        self.shifted = psola.vocode(
            self.audio,
            sample_rate=self.sr,
            target_pitch=target_f0,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            constant_stretch= None
        )

        sf.write(f"synth_{target_f0_clean[0]}.wav", self.shifted, self.sr)
        print(f"Synthesized note saved as synth_{target_f0_clean[0]}.wav")

    def CreateInstrument(self):
        self.editor.AddInstrument(SampleInstrument(self.editor, data=self.audio, original_sample_rate=self.sr, original_freq=self.f0))
