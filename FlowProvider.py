# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:25:04 2022

@author: eyu
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from ExternalSignal import ExternalSignalProvider

class FlowProvider(ExternalSignalProvider):
    def getName(self):
        return "Q_T"

# dt sampling rate
class FlowSignalFromFile(FlowProvider):
    def __init__(self, filename, nameToHeaderMap, samplingDt=None):
        data = pd.read_csv(filename)
        self.flowHistory = np.array(data[nameToHeaderMap["totalFlow"]].values.tolist())
        if samplingDt is not None:
            numHistory = self.flowHistory.size
            self.timeHistory = self.__generateTimeHistory(samplingDt, numHistory)
        else:
            self.timeHistory = np.array(data[nameToHeaderMap["time"]].values.tolist())
            
        self.time = 0
        
    def getSignal(self, state, t):
        # input is in L/min
        return np.interp(t, self.timeHistory, self.flowHistory)  * 1.66667e-5 # conversion to m3/s
        
    def __generateTimeHistory(self, dt, num):
        timeHistory = np.arange(num)
        timeHistory = timeHistory * dt
        return timeHistory
    
    def getMaxTime(self):
        return self.timeHistory[-1]

class ConstantFlowSignal(FlowProvider):
    def __init__(self, value):
        self.value = value
        
    def getSignal(self, state, t):
        return self.value