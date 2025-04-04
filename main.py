import dearpygui.dearpygui as img
import dearpygui.demo

import PlotTool.plot_tool as plt_tool

def save_callback():
    print("Save Clicked")


img.create_context()
img.create_viewport()
img.setup_dearpygui()

function_array = []

with img.window(label="Main Window", tag="Main Window", no_title_bar=True, no_resize=False):
    with img.menu_bar():
        with img.menu(label="Tools"):
            img.add_text("Available Tools")
            img.add_separator()
            if img.add_menu_item(label="Plot Tool"):
                print("Plot tool")

    with img.group(horizontal=True):
        with img.child_window(width=300, resizable_x=True):
            img.add_text("Signals")

        with img.child_window(autosize_x=True):
            with img.tab_bar():
                with (img.tab(label="Plot Tool")):
                   plt_tool.plot_tool()

                if (img.add_tab(label="Filter Tool")):
                    print("Plot tool")

                if (img.add_tab(label="FFT Tool")):
                    print("Plot tool")

                if (img.add_tab(label="Sampler Tool")):
                    print("Plot tool")

dearpygui.demo.show_demo()

img.set_primary_window("Main Window", True)
img.show_viewport()
img.start_dearpygui()
img.destroy_context()