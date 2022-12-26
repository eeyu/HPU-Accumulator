# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 14:09:38 2022

@author: eyu
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from abstractDynamics.ExternalSignal import ExternalSignalProvider

class VoltageController(ExternalSignalProvider):
    def getName(self):
        return "V"

class ConstantVoltageController(VoltageController):
    def __init__(self, voltage):
        self.voltage = voltage
        
    def getSignal(self, state, t):
        return self.voltage
    
class MaxPressureVoltageController(VoltageController):
    def __init__(self, voltage, maxPressure):
        self.voltage = voltage
        self.maxPressure = maxPressure
        
    def getSignal(self, state, t):
        if (state["P_S"] > self.maxPressure):
            return 0
        else:
            return self.voltage

# Voltage scales between maxVoltage and 0
class ProportionalVoltageController(VoltageController):
    def __init__(self, maxVoltage, maxPressure, minPressure, minVoltage=0, alpha=1.0):
        self.maxVoltage = maxVoltage
        self.maxPressure = maxPressure
        self.minPressure = minPressure
        self.minVoltage = minVoltage
        self.alpha = alpha
        
    def getSignal(self, state, t):
        pressure = state["P_S"]
        voltage = np.interp(pressure, [self.minPressure, self.maxPressure], [self.maxVoltage, self.minVoltage])
        if voltage > self.maxVoltage:
            voltage = self.maxVoltage
        elif voltage < 0:
            voltage = 0
        voltage = self.alpha * voltage + (1.0 - self.alpha) * state["Volt"]
        return voltage

class PIVoltageController(VoltageController):
    def __init__(self, maxVoltage, maxPressure, minPressure, dt, ki=0, minVoltage=0, alpha=1.0):
        self.maxVoltage = maxVoltage
        self.maxPressure = maxPressure
        self.minPressure = minPressure
        self.minVoltage = minVoltage
        self.alpha = alpha
        self.ki = ki
        self.dt = dt
        
    def getSignal(self, state, t):
        pressure = state["P_S"]
        error = pressure - self.maxPressure

        voltage = np.interp(pressure, [self.minPressure, self.maxPressure], [self.maxVoltage, self.minVoltage])
        #this is a hack 
        maxIntegrator = self.maxVoltage - voltage
        state["motorControllerIntegrator"] += -error * self.dt * self.ki
        if state["motorControllerIntegrator"] > maxIntegrator:
            state["motorControllerIntegrator"] = maxIntegrator
        voltage += state["motorControllerIntegrator"] 

        if voltage > self.maxVoltage:
            voltage = self.maxVoltage
        elif voltage < 0:
            voltage = 0
        voltage = self.alpha * voltage + (1.0 - self.alpha) * state["Volt"]
        return voltage
        
class StepVoltageController(VoltageController):
    def __init__(self, voltage, time):
        self.voltage = voltage
        self.time = time
        
    def getSignal(self, state, t):
        if (t > self.time):
            return 0
        else:
            return self.voltage