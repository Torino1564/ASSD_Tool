from Tools.plot_tool import *
from Tools.sample_tool import *
from Tools.fourier_tool import *
from Tools.system_tool import *
from Tools.transfer_tool import *
from Tools.generator_tool import *
from Tools.midi_tool import *
from Signal import *


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
        self.signal_array: list[Signal] = []
        print(len(self.signal_array))
        self.selected_signal = None
        self.tool_array: list[Tool] = []
        self.tool_uuid = [0]
        self.signal_uuid = [0]
        self.tab_bar = None
        self.signal_window_tag = None

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
                    img.add_menu_item(label="Transfer Tool", callback=lambda: self.AddTool(TransferTool))
                    img.add_menu_item(label="Generator Tool", callback=lambda: self.AddTool(GeneratorTool))
                    img.add_menu_item(label="System Tool", callback=lambda: self.AddTool(SystemTool))
                    img.add_menu_item(label="Midi Tool", callback=lambda: self.AddTool(MidiTool))

            with img.group(horizontal=True):
                with img.child_window(width=300, resizable_x=True, label="SignalWindow", tag="SignalWindow") as self.signal_window_tag:
                    img.add_text("Signals")
                    img.add_separator()

                with img.child_window(autosize_x=True):
                    with img.tab_bar() as self.tab_bar:
                        img.add_tab(label="ASSD Tool")
