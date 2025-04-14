import dearpygui.dearpygui as img


class MathExpr:
    def __init__(self, math_expression = None, period = None):
        self.math_expression = math_expression
        self.period = period
    def __call__(self, x: float):
        return self.math_expression(x)

    def EvaluatePoints(self, xValues: list[float]):
        yData = []
        if hasattr(self.math_expression, 'EvaluatePoints') and callable(
                getattr(self.math_expression, 'EvaluatePoints')):
            y_data = self.math_expression.EvaluatePoints(xValues)
        else:
            y_data = []
            for x in xValues:
                x = x % self.period
                yData.append(self.math_expression(x))
        return yData

    def Get(self):
        return self.math_expression


class Signal(object):
    def __init__(self, name, uuid = None, Xdata=None, Ydata=None, math_expr: MathExpr = None, x_label: str = "x", y_label: str = "y",
                 periodic: bool = False, period: float = None, preview_span: float = 100):
        self.name = name
        self.uuid = uuid
        self.Xdata = Xdata
        self.Ydata = Ydata
        self.periodic: bool = periodic
        self.period: float = period
        self.x_label: str = x_label
        self.y_label: str = y_label
        self.math_expr: MathExpr = math_expr
        self.math_expr.period = self.period
        self.preview_span: float = preview_span
        if period is not None:
            self.periodic = True
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

    def GetXData(self, pointsPerPeriod=100) -> list:
        if self.has_math_expr:
            Xdata: list[float] = []
            upper_bound = -1
            if self.periodic:
                upper_bound = 4 * pointsPerPeriod
            else:
                upper_bound = self.preview_span * 100

            for i in range(0, int(upper_bound)):
                Xdata.append(i * self.period / pointsPerPeriod)
            return Xdata
        else:
            return self.Xdata

    def GetYData(self) -> list:
        return self.Ydata

    def EvaluatePoints(self, x_data: list[float]):
        return self.math_expr.EvaluatePoints(x_data)

    def GetData(self, pointsPerPeriod=100):
        if not self.has_math_expr:
            return self.Xdata, self.Ydata
        else:
            x_data = self.GetXData(pointsPerPeriod)
            if hasattr(self.math_expr, 'EvaluatePoints') and callable(getattr(self.math_expr, 'EvaluatePoints')):
                y_data = self.math_expr.EvaluatePoints(x_data)
            else:
                y_data = []
                for x in x_data:
                    y_data.append(self.EvaluateMath(x))
            return x_data, y_data

    def ShowPreview(self, width, height, window_tag):
        with img.item_handler_registry() as handler:
            img.add_item_double_clicked_handler(callback=on_double_click, user_data=self)

        text_id = img.add_text(self.name, parent=window_tag)
        img.bind_item_handler_registry(text_id, handler)

        with img.plot(tag=str(self.uuid), width=width, height=height,
                      no_mouse_pos=True,
                      no_box_select=True,
                      no_menus=True, parent=window_tag):
            img.add_plot_legend()

            img.add_plot_axis(img.mvXAxis, label="x", no_label=True, no_tick_marks=True, no_tick_labels=True)
            y_axis_tag = img.add_plot_axis(img.mvYAxis, label="y", no_label=True, no_tick_marks=True,
                              no_tick_labels=True)
            xdata, ydata = self.GetData()
            img.add_line_series(xdata, ydata, parent=y_axis_tag)

def on_double_click(sender, data, user_data):
    print("Renaming Functionalities: " + str(user_data.name))