from Tool import *
import mido as mido

class MidiTool(Tool):
    def __init__(self, editor, uuid):
        Tool.__init__(self, name="Midi Tool", editor=editor, uuid=uuid)
        self.Init(self.Run)
        self.midi_file: mido.MidiFile = mido.MidiFile()

    def Run(self):

        def load_file(sender, app_data, user_data: MidiTool):
            print("Loading MIDI file...")
            print("Selected file:")
            print(app_data)
            user_data.midi_file = mido.MidiFile(filename=app_data["file_path_name"])
            user_data.UpdateTracks()


        with img.file_dialog(directory_selector=False, show=False, callback=load_file, user_data=self, tag="load_midi_tag", width=700, height=400):
            img.add_file_extension(".mid", color=(150, 255, 150, 255))

        img.add_button(label="Load MIDI", callback=lambda: img.show_item("load_midi_tag"))

        img.add_separator()
        img.add_text(label="Tracks:")
        with img.table() as self.track_table:
            img.add_table_column(label="Track")
            img.add_table_column(label="Tempo")


    def UpdateTracks(self):
        self.midi_file.print_tracks()

        children = img.get_item_children(self.track_table, 1)
        if children:
            for child in children:
                img.delete_item(child)

        for track in self.midi_file.tracks:
            with img.table_row(parent=self.track_table):
                img.add_text(track.name)
