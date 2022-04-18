# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 14:09:38 2022

@author: eyu
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class VoltageController(ABC):
    @abstractmethod
    def getControl(self, output):
        pass

class ConstantVoltageController(VoltageController):
    def __init__(self, voltage):
        self.voltage = voltage
        
    def getControl(self, output, t):
        return self.voltage
    
class MaxPressureVoltageController(VoltageController):
    def __init__(self, voltage, maxPressure):
        self.voltage = voltage
        self.maxPressure = maxPressure
        
    def getControl(self, output, t):
        if (output["P_S"] > self.maxPressure):
            return 0
        else:
            return self.voltage
        
class StepVoltageController(VoltageController):
    def __init__(self, voltage, time):
        self.voltage = voltage
        self.time = time
        
    def getControl(self, output, t):
        if (t > self.time):
            return 0
        else:
            return self.voltage