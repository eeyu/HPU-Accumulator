from ast import Mod
import numpy as np
from enum import Enum

class FunctionGenerator:
    class Mode(Enum):
        SIN=1
        CONSTANT=2
        STEP=3

    modeNameMap = {"sin" : Mode.SIN,
            "constant" : Mode.CONSTANT,
            "step" : Mode.STEP
            }

    def __init__(self):
        self.mode = FunctionGenerator.Mode.CONSTANT
        self.offset = 0.0
        self.periodOffset = 0.0
        self.amplitude = 0.0
        self.frequency = 0.0

    def useMode(self, mode : Mode):
        self.mode = mode

    def setParameters(self, offset, amplitude=0, frequency=0, periodOffset=0):
        self.offset = offset
        self.amplitude = amplitude
        self.frequency = frequency
        self.periodOffset = periodOffset

    def getValueAtTime(self, time):
        if self.mode == FunctionGenerator.Mode.SIN:
            return (self.offset + self.amplitude * np.sin(self.frequency * np.pi * 2.0 * (time - self.periodOffset)))
        if self.mode == FunctionGenerator.Mode.STEP:
            parity = int((time - self.offset) * self.frequency) % 2
            if (parity == 0):
                return self.offset - self.amplitude / 2.0
            else:
                return self.offset + self.amplitude / 2.0
        else: # Mode is CONSTANT
            return self.offset
