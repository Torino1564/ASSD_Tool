import copy
import numpy as np
import soundfile as sf
from Tool import Tool
from Signal import MathExpr
import dearpygui.dearpygui as img


class MixerTool(Tool):
    def __init__(self, editor, uuid, tab: bool = True):
        Tool.__init__(self, name="MixerTool", editor=editor, uuid=uuid)
        self.signals = []
        self.offset_tags = []
        self.output_signal = None
        self.sample_rate_tag = None
        self.pasted_signals = []
        if tab:
            self.Init(self.Run)

    def Run(self):
        img.add_text("Paste selected signals and apply time offsets [s]")

        self.sample_rate_tag = img.add_input_int(label="Sample Rate [Hz]", default_value=44100, min_value=1)
        img.add_button(label="Paste Signal", callback=self.PasteSignal)
        self.signals_group = img.add_group()
        img.add_button(label="Mix and Export", callback=self.MixSignals)

    def PasteSignal(self):
        signal = self.editor.selected_signal
        if signal is None:
            return

        offset_tag = img.add_input_float(label=f"Offset {signal.name} [s]", default_value=0.0, step=0.01, parent=self.signals_group)
        self.offset_tags.append((signal, offset_tag))
        self.signals.append((signal, offset_tag))

    def MixSignals(self):
        if not self.signals:
            return

        sample_rate = img.get_value(self.sample_rate_tag)
        all_samples = []

        for signal, offset_tag in self.signals:
            offset_s = img.get_value(offset_tag)
            x, y = signal.GetData(total_samples=int(sample_rate * signal.duration))

            # Calculate sample offset
            sample_offset = int(offset_s * sample_rate)
            padded_y = np.pad(y, (sample_offset, 0), mode='constant')
            all_samples.append(padded_y)

        # Pad all arrays to the same length
        max_len = max(len(y) for y in all_samples)
        aligned_signals = [np.pad(y, (0, max_len - len(y)), mode='constant') for y in all_samples]

        mixed = np.sum(aligned_signals, axis=0)
        mixed = np.clip(mixed, -1.0, 1.0)  # avoid clipping

        sf.write('mixed_output.wav', mixed, sample_rate)
        print("Exported mixed_output.wav")
