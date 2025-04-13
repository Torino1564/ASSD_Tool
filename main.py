import ASSD_Editor as editor
from Signal import *

import dearpygui.demo as demo

def save_callback():
    print("Save Clicked")


img.create_context()
img.create_viewport(title="ASSD Tool", width=800, height=600, x_pos=0, y_pos=0)
img.setup_dearpygui()
img.maximize_viewport()

editor = editor.ASSDEditor()
editor.Run()

demo.show_demo()

img.set_primary_window("Main Window", True)
img.show_viewport()
img.start_dearpygui()
img.destroy_context()
