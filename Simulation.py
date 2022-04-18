# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:39:39 2022

@author: eyu
"""

import numpy as np
from Dynamics import Dynamics
from InputSignalProvider import InputSignalProvider


class Simulation():
    def __init__(self, dynamics : Dynamics, inputSignalProvider : InputSignalProvider):
        self.dynamics = dynamics
        self.stateDims = dynamics.getStateDims()
        self.inputSignalProvider = inputSignalProvider
        
    def simulate(self, initialState, dt, maxTime):
        numSamples = int(maxTime//dt) + 1
        outputHistory = self.generateEmptyOutputHistory(numSamples)
        timeHistory = np.empty(numSamples)
        
        state = initialState
        t = 0
        for i in range(numSamples):
            # interpret current state
            inputSignal = self.inputSignalProvider.getSignal(t)
            # state, output = self.dynamics.getNextState(state, dt, inputSignal)
            output = self.dynamics.getOutputForCurrentState(state, inputSignal, t)
            
            scaledOutput = self.dynamics.convertOutputToPreferredUnits(output)
            self.addOutputToHistory(scaledOutput, outputHistory, i)
            timeHistory[i] = t
            
            # prepare next state
            dstate = self.dynamics.getDState(output, t)
            state = Dynamics.addStates(state, Dynamics.scaleState(dt, dstate))
            t += dt
        
        return (timeHistory, outputHistory)
    
    def addOutputToHistory(self, output, outputHistory, i):
        keys = self.dynamics.getOutputNames()
        for key in keys:
            outputHistory[key][i] = output[key]
            
    def generateEmptyOutputHistory(self, numSamples):
        keys = self.dynamics.getOutputNames()
        outputHistory = {}
        for key in keys:
            outputHistory[key] = np.empty(numSamples)
        return outputHistory
            