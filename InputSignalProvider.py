# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:25:04 2022

@author: eyu
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class InputSignalProvider(ABC):
    @abstractmethod
    def getSignal(self, time):
        pass
 
class FlowSignalFromFile(InputSignalProvider):
    def __init__(self, filename, nameToHeaderMap, dt=None):
        data = pd.read_csv(filename)
        self.flowHistory = np.array(data[nameToHeaderMap["totalFlow"]].values.tolist())
        if dt is not None:
            numHistory = self.flowHistory.size
            self.timeHistory = self.generateTimeHistory(dt, numHistory)
        else:
            self.timeHistory = np.array(data[nameToHeaderMap["time"]].values.tolist())
            
        self.time = 0
        
    def getSignal(self, time):
        # input is in L/min
        return {"Q_T" : np.interp(time, self.timeHistory, self.flowHistory)  * 1.66667e-5 } # conversion to m3/s
        
    def generateTimeHistory(self, dt, num):
        timeHistory = np.arange(num)
        timeHistory = timeHistory * dt
        return timeHistory
    
    def getMaxTime(self):
        return self.timeHistory[-1]

class ConstantFlowSignal(InputSignalProvider):
    def __init__(self, value, dt=None):
        self.value = value
        
    def getSignal(self, time):
        # input is in L/min
        return {"Q_T" : self.value}