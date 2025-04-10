import dearpygui.dearpygui as img
class Signal(object):
    def __init__(self, name, Xdata=None, Ydata=None, math_expr = None, x_label: str = "x", y_label: str = "y", periodic: bool = False, period: float = 0, preview_span: float = 100):
        self.name = name
        self.Xdata = Xdata
        self.Ydata = Ydata
        self.periodic: bool = periodic
        self.period: float = period
        self.x_label: str = x_label
        self.y_label: str = y_label
        self.math_expr = math_expr
        self.preview_span: float = preview_span
        if math_expr is None:
            self.has_math_expr: bool = False
        else:
            self.has_math_expr: bool = True


    def IsPeriodic(self) -> bool:
        return self.periodic

    def EvaluateMath(self, x: float) -> float:
        if not self.has_math_expr:
            raise AttributeError("Signal doesnt support math expression")
        if self.periodic:
            x = x % self.period
        return self.math_expr(x)


    def SetPeriodic(self, periodic: bool):
        self.periodic = periodic

    def GetXData(self) -> list:
        if self.has_math_expr:
            Xdata: list[float] = []
            upper_bound = -1
            if self.periodic:
                upper_bound = 4*self.period*100
            else:
                upper_bound = self.preview_span*100

            for i in range(0, int(upper_bound)):
                Xdata.append(i/100)
            return Xdata
        else:
            return self.Xdata

    def GetYData(self) -> list:
        return self.Ydata

    def EvaluatePoints(self, x_data: list[float]):
        YData: list[float] = []
        for point in x_data:
            YData.append(self.EvaluateMath(point))
        return YData

    def GetData(self):
        if not self.has_math_expr:
            return self.Xdata, self.Ydata
        else:
            x_data = self.GetXData()
            y_data = self.EvaluatePoints(x_data)
            return x_data, y_data



    def ShowPreview(self, width, height):
        with img.plot(label=self.name, tag=self.name, width=width, height=height,
                      no_mouse_pos=True,
                      no_box_select=True,
                      no_menus=True):
            img.add_plot_legend()

            img.add_plot_axis(img.mvXAxis, label="x", no_label=True, no_tick_marks=True, no_tick_labels=True)
            img.add_plot_axis(img.mvYAxis, label="y", tag=str("y_axis"+self.name), no_label=True, no_tick_marks=True, no_tick_labels=True)
            xdata, ydata = self.GetData()
            img.add_line_series(xdata, ydata, parent=str("y_axis"+self.name))