from Tool import *
import mido as mido
from Signal import *

class TrackAndInstrument:
    def __init__(self, midi_track, instrument):
        self.midi_track = midi_track
        self.instrument = instrument

    midi_track = None
    instrument = None


class MidiTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Midi Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.midi_file: mido.MidiFile = mido.MidiFile()
        self.tracks_and_instruments: list[TrackAndInstrument] = []

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

    def UpdateTracks(self):
        children = img.get_item_children(self.track_table, 1)
        if children:
            for child in children:
                img.delete_item(child)

        for track_and_instrument in self.tracks_and_instruments:
            track = track_and_instrument.midi_track
            instrument = track_and_instrument.instrument
            with img.table_row(parent=self.track_table):
                img.add_text(track.name)
                with img.group() as cell_group_tag:
                    img.add_button(label="Paste")

    def ExportTracks(self):
        for track_and_instrument in self.tracks_and_instruments:
            if track_and_instrument.instrument is None:
                img.show_item(self.warning_tag)
                break
            else:
                img.hide_item(self.warning_tag)
            track = track_and_instrument.midi_track
            instrument = track_and_instrument.instrument

            tick_time = track.time

            notes = []
            active_notes = {}
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time * tick_time
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = [absolute_time, msg.velocity]
                if msg.type == 'note_off' or (msg.type == "note_on" and msg.velocity == 0):
                    if msg.note not in active_notes:
                        start_time, velocity = active_notes[msg.note]
                        duration = absolute_time - start_time
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
