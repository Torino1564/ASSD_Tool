import dearpygui.dearpygui as img
class Signal(object):
    def __init__(self, name, index: int, Xdata=None, Ydata=None, periodic: bool = False, period: float = 0):
        self.index: int = index
        self.name = name
        self.Xdata = Xdata
        self.Ydata = Ydata
        self.periodic: bool = periodic
        self.period: float = period

    def IsPeriodic(self) -> bool:
        return self.periodic

    def SetPeriodic(self, periodic: bool):
        self.periodic = periodic

    def GetXData(self) -> list:
        return self.Xdata

    def GetYData(self) -> list:
        return self.Ydata

    def ShowPreview(self, width, height):
        with img.plot(label=self.name, tag=self.name, width=width, height=height,
                      no_mouse_pos=True,
                      no_box_select=True,
                      no_menus=True):
            img.add_plot_legend()

            img.add_plot_axis(img.mvXAxis, label="x", no_label=True, no_tick_marks=True, no_tick_labels=True)
            img.add_plot_axis(img.mvYAxis, label="y", tag=str("y_axis"+self.name), no_label=True, no_tick_marks=True, no_tick_labels=True)

            img.add_line_series(self.GetXData(), self.GetYData(), parent=str("y_axis"+self.name))