# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:20:08 2022

@author: eyu
"""

from AbstractClass import ABC, abstractmethod
import numpy as np

class ControlSignal(ABC):
    @abstractmethod
    def getNextState(self, currentStateVector : np.ndarray, dt, controlInput=None):
        pass
    
    @abstractmethod
    def getStateDims(self):
        pass
    
class HPUDynamics(Dynamics):
    def __init__(self, parameters):
        self.parameters = parameters
        
    def getNextState(self, currentStateVector : dict, dt, controlInputVector : dict):
        state = self.convertStateVectorToNamed(currentStateVector)
        control = self.convertControlVectorToNamed(controlInputVector)
        
        # The math
        dP_A = 1 * state["P_A"] * state["P_A"] * np.sqrt(state["P_A"] - state["P_S"])
        Q_T = control["Q_T"]
        Q_A = self.getAccumulatorFlowFromPressure(currentStateVector)
        Q_S = Q_T - Q_A
        pumpRotVel = Q_S
        voltage = self.voltageController.getControl(state)
        dI = - 1 * state["I"] + 1 * voltage - 1 * pumpRotVel
        
        # Integrate
        nextState = {"P_A" : state['P_A'] + dt * dP_A,
                     "I" : state["I"] + dt * dI}
        
        # Convert to outputs
        motorTorque = 1 * nextState["I"]
        P_S = 1 * motorTorque
        
        output = {"P_A" : nextState["P_A"],
                  "Q_A" : Q_A,
                  "P_S" : P_S,
                  "Q_S" : Q_S}
        
        return nextState, output