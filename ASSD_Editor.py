from Tools.plot_tool import *
from Tools.sample_tool import *
from Tools.fourier_tool import *
from Tools.system_tool import *
from Tools.transfer_tool import *
from Tools.generator_tool import *
from Tools.midi_tool import *
from Tools.sintesis_aditiva_tool import *
from Tools.sintesis_modelado_fisico_tool import *
from Tools.sintesis_FM_tool import *
from Tools.Effects_tool import *
from Tools.espectrogram_tool import *
from Instrument import *

class Data:
    def __init__(self, editor, signal):
        self.editor = editor
        self.signal = signal


def select_signal(sender, data, user_data: Data):
    user_data.editor.selected_signal = user_data.signal
    print(f"Copied: {str(user_data.signal.name)}")


def update_plot_size(editor):
    # Get dimensions of the window
    width, height = img.get_item_rect_size("SignalWindow")

    for signal in editor.signal_array:
        # Apply the dimensions to the plot
        img.set_item_width(str(signal.uuid), width)
        img.set_item_height(str(signal.uuid), width * 0.6)

    img.set_frame_callback(img.get_frame_count() + 10, lambda: update_plot_size(editor))


class ASSDEditor(object):
    def __init__(self):
        self.selected_instrument_tag = None
        self.selected_instrument = None
        self.signal_array: list[Signal] = []
        print(len(self.signal_array))
        self.selected_signal = None
        self.tool_array: list[Tool] = []
        self.tool_uuid = [0]
        self.signal_uuid = [0]
        self.tab_bar = None
        self.signal_window_tag = None
        self.instruments = []

        img.set_frame_callback(img.get_frame_count() + 10, lambda: update_plot_size(self))

    def GetNewToolUUID(self):
        self.tool_uuid[0] += 1
        return self.tool_uuid[0]

    def GetNewSignalUUID(self):
        self.signal_uuid[0] += 1
        return self.signal_uuid[0]

    def AddSignal(self, signal: Signal):
        if signal is None:
            return
        signal.uuid = self.GetNewSignalUUID()
        self.signal_array.append(signal)
        self.selected_signal = signal
        tag = img.add_button(label="Copy", parent="SignalWindow", width=40)
        img.set_item_callback(tag, select_signal)
        img.set_item_user_data(tag, Data(editor=self, signal=signal))
        signal.ShowPreview(100, 100, self.signal_window_tag)
        img.add_separator(parent=self.signal_window_tag)

    def AddInstrument(self, instrument: Instrument):
        if instrument is None:
            return
        self.instruments.append(instrument)
        with img.table_row(parent=self.instrument_table) as table_row_tag:
            img.add_text(instrument.name)
            img.add_button(label="Select", callback=lambda: self.SelectInstrument(instrument, table_row_tag))
        self.SelectInstrument(instrument, table_row_tag)


    def AddTool(self, toolType):
        new_tool = toolType(self, self.GetNewToolUUID())
        img.set_value(self.tab_bar, new_tool.tab)
        self.tool_array.append(new_tool)

    def Run(self):
        with img.window(label="Main Window", tag="Main Window", no_title_bar=True, no_resize=False):
            with img.menu_bar():
                with img.menu(label="Tools"):
                    img.add_text("Available Tools")
                    img.add_separator()
                    img.add_menu_item(label="Plot Tool", callback=lambda: self.AddTool(PlotTool))
                    img.add_menu_item(label="Sample Tool", callback=lambda: self.AddTool(SampleTool))
                    img.add_menu_item(label="Fourier Tool", callback=lambda: self.AddTool(FourierTool))
                    img.add_menu_item(label="Espectrogram Tool", callback=lambda: self.AddTool(EspectrogramTool))
                    img.add_menu_item(label="Transfer Tool", callback=lambda: self.AddTool(TransferTool))
                    img.add_menu_item(label="Generator Tool", callback=lambda: self.AddTool(GeneratorTool))
                    img.add_menu_item(label="System Tool", callback=lambda: self.AddTool(SystemTool))
                    img.add_menu_item(label="Midi Tool", callback=lambda: self.AddTool(MidiTool))
                    img.add_menu_item(label="Audio Effects Tool", callback=lambda: self.AddTool(EffectsTool))
                    img.add_separator(label="Instrument Synthesis")
                    img.add_menu_item(label="Additive Synthesis Tool", callback=lambda: self.AddTool(SintesisAditivaTool))
                    img.add_menu_item(label="KPS Synthesis Tool", callback=lambda: self.AddTool(KPStrongTool))
                    img.add_menu_item(label="FM Synthesis Tool", callback=lambda: self.AddTool(SintesisFMTool))

                with img.menu(label="View"):
                    img.add_menu_item(label="Instruments", callback=lambda: self.ShowInstruments())
                    img.add_menu_item(label="Signals")

            with img.group(horizontal=True):
                with img.child_window(width=300, resizable_x=True, label="SignalWindow", tag="SignalWindow") as self.signal_window_tag:
                    img.add_text("Signals")
                    img.add_separator()

                with img.child_window(autosize_x=True):
                    with img.tab_bar() as self.tab_bar:
                        img.add_tab(label="ASSD Tool")

        with img.window(label="Instruments", show=False) as self.instruments_window:
            with img.table() as self.instrument_table:
                img.add_table_column(label="Name")
                img.add_table_column(label="Select")

    def SelectInstrument(self, instrument, instrument_tag):
        self.selected_instrument_tag = instrument_tag
        self.selected_instrument = instrument
        with img.theme() as selected_row_theme:
            with img.theme_component(img.mvAll):
                img.add_theme_color(img.mvThemeCol_Header, (0, 120, 215, 100), category=img.mvThemeCat_Core)
                img.add_theme_color(img.mvThemeCol_HeaderHovered, (30, 150, 255, 120), category=img.mvThemeCat_Core)
                img.add_theme_color(img.mvThemeCol_HeaderActive, (0, 100, 180, 120), category=img.mvThemeCat_Core)
        if self.selected_instrument_tag is not None:
            img.bind_item_theme(item=self.selected_instrument_tag, theme=selected_row_theme)


    def ShowInstruments(self):
        img.show_item(self.instruments_window)