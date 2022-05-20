import numpy as np

class DerivativeMonitor:
    def __init__(self, initialValue=0, firstDerivativeIsZero=False):
        self.lastValue = initialValue
        self.setNextDerivativeToZero = firstDerivativeIsZero

    def getDerivativeAfterNextMeasurement(self, value, dt):
        if self.setNextDerivativeToZero:
            self.setNextDerivativeToZero = False
            self.lastValue = value
            return 0
        else:
            derivative = (value - self.lastValue) / dt
            self.lastValue = value
            return derivative