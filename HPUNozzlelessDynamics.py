# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 10:31:32 2022

@author: eyu
"""

from Dynamics import Dynamics
from StateUnitProperties import StateUnitProperties
import numpy as np
from DerivativeMonitor import DerivativeMonitor
from ExternalSignal import ExternalSignalCollection

class HPUDynamicsNoNozzlePhysics:
    def __init__(self, parameters : dict):
        self.parameters = parameters

    def calculateAccumulatorVolumeFromPressure(self, P_A):
        a = self.parameters["accumulatorGasConstant"]
        gasVolume = np.power(self.parameters["initialGasPVConstant"] / P_A, 1.0/a)
        return self.parameters["accumulatorVolume"] - gasVolume

    def calculateAccumulatorPressureFromVolume(self, V_A):
        a = self.parameters["accumulatorGasConstant"]
        gasVolume = self.parameters["accumulatorVolume"] - V_A
        return self.parameters["initialGasPVConstant"] / np.power(gasVolume, a)

    def calculateAccumulatorGasPVConstant(P_A, V_A, gasConstant):
        return P_A * np.power(V_A, gasConstant)

    def calculateSteadyStateCurrentFromVoltage(self, voltage, flow):
        return (voltage - self.parameters['motorTorqueConstant'] * flow / self.parameters['pumpDisplacement']) / self.parameters['motorResistance']

    def calculateDCurrent(self, current, flow, voltage):
        return ((- self.parameters["motorResistance"] * current
            + voltage
            - self.parameters["motorTorqueConstant"] * flow / self.parameters['pumpDisplacement']) 
            / self.parameters["motorInductance"])

    def calculateDAccumulatorPressure(self, P_A, Q_A):
        # positive Q_A means flow is going outwards
        a = self.parameters["accumulatorGasConstant"] * 1.0
        PVa0 = self.parameters["initialGasPVConstant"] * 1.0
        return -Q_A * np.power(PVa0, -1.0/a) * a * np.power(P_A, 1.0 + 1.0/a)
    
    def calculateDMotorFlow(self, current, motorFlow, supplyPressure):
        return ((self.parameters["motorTorqueConstant"] * current 
            - self.parameters["motorViscousConstant"] * motorFlow / self.parameters["pumpDisplacement"]
            - supplyPressure * self.parameters["pumpDisplacement"])
            / (self.parameters["motorInertia"] / self.parameters["pumpDisplacement"]))

    def calculateSupplyPressureBackwards(self, current, motorFlow, dMotorFlow):
        return ((self.parameters["motorTorqueConstant"] * current
            - self.parameters["motorViscousConstant"] * motorFlow / self.parameters["pumpDisplacement"]
            - self.parameters["motorInertia"] / self.parameters["pumpDisplacement"] * dMotorFlow)
            / (self.parameters["pumpDisplacement"]))
    
class HPUDynamicsNoNozzle(Dynamics):
    def __init__(self, parameters : dict, externalSignals : ExternalSignalCollection, useSteadyStateCurrent=False):
        parameters["initialGasPVConstant"] = HPUDynamicsNoNozzlePhysics.calculateAccumulatorGasPVConstant(
                                                parameters["accumulatorPrechargePressure"], 
                                                parameters["accumulatorVolume"], 
                                                parameters["accumulatorGasConstant"])
        self.parameters = parameters
        self.physicsToolbox = HPUDynamicsNoNozzlePhysics(parameters)
        self.useSteadyStateCurrent=useSteadyStateCurrent
        self.stateUnitProperties = {# Integrables
                                    "I"   : StateUnitProperties("motorCurrent", "A", "A", 1),
                                    "Q_S" : StateUnitProperties("supplyFlowOut", "m3/s", "L/min", 60000),
                                    "V_A" : StateUnitProperties("accumulatorFluidVolume", "m3", "L", 1000.),
                                    # Equality
                                    "Q_A" : StateUnitProperties("accumulatorFlowOut", "m3/s", "L/min", 60000),
                                    "P_S" : StateUnitProperties("supplyPressure", "Pa", "bar", 1e-5),
                                    "dQ_S" : StateUnitProperties("supplyFlowAccelerationOut", "m3/s^2", "L/min^2", 3600000),
                                    # External signals
                                    "Q_T" : StateUnitProperties("totalFlowOut", "m3/s", "L/min", 60000),
                                    "Volt" : StateUnitProperties("motorVoltage", "V", "V", 1),
                                }
        self.externalSignals = externalSignals

    def getInitialFullStateFromIntegrables(self, integrableStates : dict):
        # this isn't the best way to do things, but the only way I could think of doing things
        t = 0
        P_S = self.physicsToolbox.calculateAccumulatorPressureFromVolume(integrableStates["V_A"])
        integrableStates["P_S"] = P_S
        signals = self.externalSignals.getAllSignals(integrableStates, t)
        Q_T = signals["Q_T"]
        V = signals["V"]

        Q_A = Q_T - integrableStates["Q_S"]

        output = {"I" : integrableStates["I"],
            "Q_S" : integrableStates["Q_S"],
            "V_A" : integrableStates["V_A"],
            "P_S" : P_S,
            "Q_A" : Q_A,
            "dQ_S" : 0,
            "Q_T" : Q_T,
            "Volt" : V,
        }

        return output

    def getNextFullState(self, lastFullState : dict, dt, t):
        signals = self.externalSignals.getAllSignals(lastFullState, t)
        Q_T = signals["Q_T"]
        V = signals["V"]

        # calculate flow
        dQ_S_candidate = self.physicsToolbox.calculateDMotorFlow(lastFullState["I"], lastFullState["Q_S"], lastFullState["P_S"])
        Q_S_candidate = lastFullState["Q_S"] + dt * dQ_S_candidate
        Q_A_candidate = Q_T - Q_S_candidate
        dV_A_candidate = -Q_A_candidate
        V_A_candidate = lastFullState["V_A"] + dV_A_candidate * dt # plus or minus?

        # if accumulator has been depleted, calculate with no accumulator
        if V_A_candidate < 0:
            Q_A = lastFullState["V_A"] / dt
            V_A = 0
            Q_S = Q_T - Q_A
            dQ_S = (Q_S - lastFullState["Q_S"]) / dt
            P_S = self.physicsToolbox.calculateSupplyPressureBackwards(I, Q_S, dQ_S)
        else: # else, continue with calculations
            Q_S = Q_S_candidate
            Q_A = Q_A_candidate
            V_A = V_A_candidate
            dQ_S = dQ_S_candidate
            P_S = self.physicsToolbox.calculateAccumulatorPressureFromVolume(V_A)

        if self.useSteadyStateCurrent:
            I = self.physicsToolbox.calculateSteadyStateCurrentFromVoltage(V, Q_S)
        else:
            dI = self.physicsToolbox.calculateDCurrent(lastFullState["I"], lastFullState["Q_S"], V)
            I = lastFullState["I"] + dI * dt
            
        output = {"P_S" : P_S,
                "Q_A" : Q_A,
                "Q_S" : Q_S,
                "dQ_S" : dQ_S,
                "V_A" : V_A,
                "Q_T" : Q_T,
                "I" : I,
                "Volt" : V,
            }

        return output

    def getStateUnitProperties(self):
        return self.stateUnitProperties