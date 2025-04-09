import dearpygui.dearpygui as img

class Function(object):
    def __init__(self, name, Xdata=None, Ydata=None, periodic: bool = False, period: float = 0):
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

    def ShowPreview(self):
        with img.plot(label=self.name):
            img.add_plot_legend()

            img.add_plot_axis(img.mvXAxis, label="x")
            img.add_plot_axis(img.mvYAxis, label="y", tag="y_axis")

            img.add_line_series(self.GetXData(), self.GetYData(), parent="y_axis")