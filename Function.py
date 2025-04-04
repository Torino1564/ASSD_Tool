class Function(object):
    def __init__(self, name):
        self.name = name
        self.Xdata = []
        self.Ydata = []
        self.periodic: bool = False
        self.period: float = 0.0

    def IsPeriodic(self) -> bool:
        return self.periodic

    def SetPeriodic(self, periodic: bool):
        self.periodic = periodic

    def GetXData(self) -> list:
        return self.Xdata

    def GetYData(self) -> list:
        return self.Ydata


