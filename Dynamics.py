# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 11:28:45 2022

@author: eyu
"""
from abc import ABC, abstractmethod
from InputSignalProvider import InputSignalProvider
from VoltageController import VoltageController
import numpy as np

class ParameterProperties:
    def __init__(self, name : str, SIUnits : str, preferredUnits : str, scalingSIToPreferred):
        self.name = name
        self.SIUnits = SIUnits
        self.preferredUnits = preferredUnits
        self.scalingSIToPreferred = scalingSIToPreferred

class Dynamics(ABC):  
    @abstractmethod
    def getStateDims(self):
        pass
    
    @abstractmethod
    def getOutputNames(self):
        pass
    
    @abstractmethod
    def getOutputForCurrentState(self, state : dict, inputSignal : dict, t):
        pass
    
    @abstractmethod
    def getDState(self, output : dict, t):
        pass
    
    def addStates(state1 : dict, state2 : dict):
        outputState = {}
        for key in state1.keys():
            outputState[key] = state1[key] + state2[key]
        return outputState
    
    def scaleState(scalar, state1 : dict):
        outputState = {}
        for key in state1.keys():
            outputState[key] = state1[key] * scalar
        return outputState
    
    def multiplyState(scalingState, state1 : dict):
        outputState = {}
        for key in state1.keys():
            outputState[key] = state1[key] * scalingState[key]
        return outputState
    
    def convertOutputToPreferredUnits(self, output):
        parameterProperties = self.getParameterProperties()
        convertedOutput = {}
        for key in output.keys():
            convertedOutput[key] = output[key] * parameterProperties[key].scalingSIToPreferred
        return convertedOutput
    
    @abstractmethod
    def getParameterProperties(self):
        pass
    
class HPUDynamics(Dynamics):
    def __init__(self, parameters, voltageController : VoltageController, inputSignal):
        parameters["initialGasPVConstant"] = (parameters["accumulatorPrechargePressure"] * 
                                              np.power(parameters["accumulatorVolume"], parameters["accumulatorGasConstant"]))
        self.parameters = parameters
        self.voltageController = voltageController
        self.lastQ_A = 0.000001
        self.parameterProperties = {"P_A" : ParameterProperties("accumulatorPressure", "Pa", "bar", 1e-5),
                                    "Q_A" : ParameterProperties("accumulatorFlowOut", "m3/s", "L/min", 60000),
                                    "P_S" : ParameterProperties("supplyPressure", "Pa", "bar", 1e-5),
                                    "Q_S" : ParameterProperties("supplyFlowOut", "m3/s", "L/min", 60000),
                                    "V_A" : ParameterProperties("accumulatorFluidVolume", "m3", "L", 1000.),
                                    "Q_T" : ParameterProperties("totalFlowOut", "m3/s", "L/min", 60000),
                                    "I" : ParameterProperties("motorCurrent", "A", "A", 1),
                                    "Volt" : ParameterProperties("motorVoltage", "V", "V", 1),
                                    "P_A-P_S" : ParameterProperties("P_A - P_S", "Pa", "bar", 1e-5)
                                    }
                  
    def getOutputForCurrentState(self, state : dict, inputSignal : dict, t):
        # The math
        P_S = self.convertCurrentToSupplyPressure(state["I"])
        
        Q_T = inputSignal["Q_T"] * 1.66667e-5 # conversion to m3/s
        P_A = state["P_A"]
        V_A = self.getAccumulatorVolumeFromPressure(P_A)
        Q_A = self.getAccumulatorFlowFromPressure(P_A, P_S, self.lastQ_A)
        if V_A <= 0:
            V_A = 0
            if Q_A > 0:
                Q_A = 0

        I = state["I"]
        
        Q_S = Q_T - Q_A

        # Convert to outputs
        output = {"P_A" : P_A,
                  "Q_A" : Q_A,
                  "P_S" : self.convertCurrentToSupplyPressure(I),
                  "Q_S" : Q_S,
                  "V_A" : V_A,
                  "Q_T" : Q_T,
                  "I" : I,
                  "Volt" : self.voltageController.getControl({"P_S" : P_S}, t),
                  "P_A-P_S" : P_A - P_S
                  }
        
        self.lastQ_A = Q_A
        return output
    
    def getDState(self, output : dict, t):
        if output["V_A"] < 0:
            dP_A = 0
        else:
            dP_A = self.getDPressureFromFlow(output["P_A"], output["Q_A"])
            
        pumpRotVel = output["Q_S"] / self.parameters["pumpDisplacement"] * 2 * np.pi
        voltage = self.voltageController.getControl({"P_S" : output["P_S"]}, t)
        dI = ((- self.parameters["motorResistance"] * output["I"]
               + voltage
               - self.parameters["motorTorqueConstant"] * pumpRotVel) 
                  /self.parameters["motorInductance"])
        
        dstate = {"P_A" : dP_A,
                    "I" : dI}
        return dstate
    
    def getDischargeCoefficient(self, reynolds):
        # return 0.6
        laminarConstant = (self.parameters["accumulatorNozzleDiameter"] * reynolds / 
            self.parameters["accumulatorNozzleLength"])
        if (laminarConstant > 50):
            return 1.0 / np.sqrt(1.5 + 13.74 / np.sqrt(laminarConstant))
        else:
            return 1.0 / np.sqrt(2.28 + 64.0 / laminarConstant)
    
    def getReynoldsNumber(self, flow):
        return (4.0 * self.parameters["fluidDensity"] * np.abs(flow) / 
            (np.pi * self.parameters["fluidViscosity"] * 
             self.parameters["accumulatorNozzleDiameter"]) )

    def getStateDims(self):
        return 2
    
    def getOutputDims(self):
        return len(self.parameterProperties)
    
    def getOutputNames(self):
        return self.parameterProperties.keys()
    
    def getParameterProperties(self):
        return self.parameterProperties
    
    def convertCurrentToSupplyPressure(self, current):
        motorTorque = self.parameters["motorTorqueConstant"] * current
        supplyPressure = motorTorque / self.parameters["pumpDisplacement"] * 2.0 * np.pi
        return supplyPressure
    
    def convertSupplyPressureToCurrent(self, pressure):
        motorTorque = pressure * self.parameters["pumpDisplacement"] / 2.0 / np.pi
        current = motorTorque / self.parameters["motorTorqueConstant"]
        return current
    
    def getAccumulatorFlowFromPressure(self, P_A, P_S, Q_A):
        # if (P_S == P_A):
        #     return 0.000001
        
        reynolds = self.getReynoldsNumber(Q_A)
        # reynolds = 0
        dischargeCoefficient = self.getDischargeCoefficient(reynolds)
        pressureDifference = P_A - P_S
        area = np.pi * np.square(self.parameters["accumulatorNozzleDiameter"]/2.0)
        
        return (area * dischargeCoefficient * 
            np.sqrt(np.abs(pressureDifference) * 2.0 / self.parameters["fluidDensity"]) * 
            np.sign(pressureDifference))
    
    def getDPressureFromFlow(self, P_A, Q_A):
        # positive Q_A means flow is going outwards
        a = self.parameters["accumulatorGasConstant"] * 1.0
        PVa0 = self.parameters["initialGasPVConstant"] * 1.0
        return -Q_A * np.power(PVa0, -1.0/a) * a * np.power(P_A, 1.0 + 1.0/a)
    
    def getAccumulatorVolumeFromPressure(self, P_A):
        a = self.parameters["accumulatorGasConstant"]
        gasVolume = np.power(self.parameters["initialGasPVConstant"] / P_A, 1.0/a)
        return self.parameters["accumulatorVolume"] - gasVolume

        