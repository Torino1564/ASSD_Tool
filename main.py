import dearpygui.dearpygui as img
import dearpygui.demo

import PlotTool.plot_tool as plt_tool

def save_callback():
    print("Save Clicked")


img.create_context()
img.create_viewport()
img.setup_dearpygui()

with img.window(label="Main Window", height=800, width=800, no_title_bar=True):

    with img.menu_bar():
        with img.menu(label="Tools"):
            img.add_text("Avaiable Tools")
            img.add_separator()
            if (img.add_menu_item(label="Plot Tool")):
                plt_tool.plot_tool()

    with img.tab_bar():
        if (img.add_tab(label="Plot Tool")):
            plt_tool.plot_tool()

        if (img.add_tab(label="Filter Tool")):
            plt_tool.plot_tool()

        if (img.add_tab(label="FFT Tool")):
            plt_tool.plot_tool()

        if (img.add_tab(label="Sampler Tool")):
            plt_tool.plot_tool()


dearpygui.demo.show_demo()

img.show_viewport()
img.start_dearpygui()
img.destroy_context()