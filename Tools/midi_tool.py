import numpy as np

from Tool import *
import mido as mido
from Signal import *
import sounddevice as sd

class TrackAndInstrument:
    def __init__(self, midi_track, instrument):
        self.midi_track = midi_track
        self.instrument = instrument

    midi_track = None
    instrument = None
    instrument_label_tag = None


class MidiTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Midi Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.midi_file: mido.MidiFile = mido.MidiFile()
        self.tracks_and_instruments: list[TrackAndInstrument] = []
        self.selected_signal = None

    def Run(self):

        def load_file(sender, app_data, user_data: MidiTool):
            print("Loading MIDI file...")
            print("Selected file:")
            print(app_data)
            user_data.midi_file = mido.MidiFile(filename=app_data["file_path_name"])
            for track in user_data.midi_file.tracks:
                user_data.tracks_and_instruments.append(TrackAndInstrument(track, None))
            user_data.UpdateTracks()


        with img.file_dialog(directory_selector=False, show=False, callback=load_file, user_data=self, tag="load_midi_tag", width=700, height=400):
            img.add_file_extension(".mid", color=(150, 255, 150, 255))

        img.add_button(label="Load MIDI", callback=lambda: img.show_item("load_midi_tag"))

        img.add_separator()
        img.add_text(label="Tracks:")
        with img.table() as self.track_table:
            img.add_table_column(label="Track")
            img.add_table_column(label="Instrument")
        img.add_button(label="Update File", callback=lambda: self.UpdateTracks())
        img.add_button(label="Save File", callback=lambda: self.ExportTracks())
        self.warning_tag = img.add_text("Warning! Make sure all tracks have an instrument assigned to them!", color=(150, 255, 150, 255), show=False)

        def play_signal():
            self.selected_signal = self.editor.selected_signal
            freq = 44100
            t, sound = self.selected_signal.GetData(total_samples=int(44100*self.selected_signal.duration))
            sd.play(sound, 44100)
            sd.wait()

        img.add_button(label="Play selected Signal", callback=lambda: play_signal())

    def _handle_paste_button(self, sender, app_data, user_data):
        index = user_data
        track_and_instrument = self.tracks_and_instruments[index]

        # Assign the selected instrument
        instrument = self.editor.selected_instrument
        track_and_instrument.instrument = instrument

        # Update the label text in the table
        img.set_value(track_and_instrument.instrument_label_tag, instrument.name)

    import functools

    def UpdateTracks(self):
        children = img.get_item_children(self.track_table, 1)
        if children:
            for child in children:
                img.delete_item(child)

        for index, track_and_instrument in enumerate(self.tracks_and_instruments):
            track = track_and_instrument.midi_track
            instrument = track_and_instrument.instrument

            with img.table_row(parent=self.track_table):
                img.add_text(track.name)

                with img.group(horizontal=True):
                    paste_tag = f"paste_btn_{index}"
                    label_tag = f"instrument_label_{index}"

                    img.add_button(
                        label="Paste",
                        tag=paste_tag,
                        callback=self._handle_paste_button,
                        user_data=index
                    )

                    # Add label that will show instrument name after pasting
                    label_text = instrument.name if instrument else ""
                    img.add_text(
                        label_text,
                        tag=label_tag
                    )

                    # Store tag for later update
                    track_and_instrument.instrument_label_tag = label_tag

    def ExportTracks(self):
        for track_and_instrument in self.tracks_and_instruments:
            #if track_and_instrument.instrument is None:
            #    img.show_item(self.warning_tag)
            #    break
            #else:
            #    img.hide_item(self.warning_tag)
            track = track_and_instrument.midi_track
            instrument = track_and_instrument.instrument
            ticks_per_beat = self.midi_file.ticks_per_beat
            tempo = 500000
            notes = []
            active_notes = {}
            absolute_ticks = 0
            total_duration = 0
            for msg in track:
                absolute_ticks += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = [mido.tick2second(absolute_ticks, ticks_per_beat, tempo), msg.velocity]

                if msg.type == 'note_off' or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, velocity = active_notes.pop(msg.note)
                        end_time = mido.tick2second(absolute_ticks, ticks_per_beat, tempo)
                        duration = end_time - start_time
                        if end_time > total_duration:
                            total_duration = end_time
                        notes.append({
                            "note": msg.note,
                            "velocity": velocity,
                            "start_time": start_time,
                            "duration": duration})

            signals_and_offsets = []

            for entry in notes:
                signals_and_offsets.append({
                    "signal": instrument.Play(entry["note"], entry["velocity"], entry["duration"]),
                    "offset": entry["start_time"]
                })

            class TrackMathExpr(MathExpr):
                def __init__(self, signals_and_offsets):
                    self.signals_and_offsets = signals_and_offsets

                def __call__(self, x: float):
                    result = 0
                    for signal, offset in self.signals_and_offsets:
                        if offset < x < offset + signal.duration:
                            result += signal.EvaluateMath(x - offset)

                def EvaluatePoints(self, xValues: list[float]):
                    y = [0.0] * len(xValues)
                    for el in self.signals_and_offsets:
                        resolution = xValues[1] - xValues[0]
                        offset = el["offset"]
                        signal = el["signal"]
                        local_result = signal.EvaluatePoints(np.linspace(start=0, stop=signal.duration, num=int(signal.duration/resolution)))
                        j = 0
                        for i, x in enumerate(xValues):
                            if x < offset:
                                continue
                            if x >= offset + signal.duration:
                                break
                            if j > len(local_result) - 1:
                                break
                            y[i] = local_result[j]
                            j += 1

                    return y
            self.editor.AddSignal(Signal(math_expr=TrackMathExpr(signals_and_offsets), name=track.name, duration=total_duration))