# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:39:39 2022

@author: eyu
"""

import numpy as np
from Dynamics import Dynamics

class Simulation():
    def __init__(self, dynamics : Dynamics):
        self.dynamics = dynamics
        
    def simulate(self, initialFullState, dt, maxTime):
        numSamples = int(maxTime//dt) + 1
        fullStateHistory = self.generateEmptyFullStateHistory(numSamples)
        timeHistory = np.empty(numSamples)
        
        fullState = initialFullState
        t = 0
        for i in range(numSamples):
            fullState = self.dynamics.getNextFullState(fullState, dt, t)

            scaledFullState = self.dynamics.convertFullStateToPreferredUnits(fullState)
            self.addFullStateToHistory(scaledFullState, fullStateHistory, i)
            timeHistory[i] = t
            t += dt
        
        return (timeHistory, fullStateHistory)
    
    def addFullStateToHistory(self, output, outputHistory, i):
        keys = self.dynamics.getFullStateNames()
        for key in keys:
            outputHistory[key][i] = output[key]
            
    def generateEmptyFullStateHistory(self, numSamples):
        keys = self.dynamics.getFullStateNames()
        outputHistory = {}
        for key in keys:
            outputHistory[key] = np.empty(numSamples)
        return outputHistory
            