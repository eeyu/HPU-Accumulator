# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 10:31:32 2022

@author: eyu
"""

# All math can be referenced here:
# https://docs.google.com/presentation/d/1F06h3KazdXrJqL3oXz7IlBEz1O0cy0PYbd30vnif52o/edit#slide=id.g12aaf72706b_0_158

from abstractDynamics.Dynamics import Dynamics
from abstractDynamics.StateUnitProperties import StateUnitProperties
import numpy as np
from abstractDynamics.ExternalSignal import ExternalSignalCollection
import hpuDynamics.HPUCommonStateUnitProperties as stateUP
from hpuDynamics.HPUPhysics import HPUPhysicsToolbox
    
class HPUDynamicsNoNozzle(Dynamics):
    # All of these get plotted. they serve a similar function to yovariables
    stateUnitProperties = stateUP.stateUnitProperties
    def __init__(self, parameters : dict, externalSignals : ExternalSignalCollection, useSteadyStateCurrent=False):
        parameters["initialGasPVConstant"] = HPUPhysicsToolbox.calculateAccumulatorGasPVConstant(
                                                parameters["accumulatorPrechargePressure"], 
                                                parameters["accumulatorVolume"], 
                                                parameters["accumulatorGasConstant"])
        self.parameters = parameters
        self.physicsToolbox = HPUPhysicsToolbox(parameters)
        self.useSteadyStateCurrent=useSteadyStateCurrent

        self.externalSignals = externalSignals

    def getInitialFullStateFromIntegrables(self, integrableStates : dict):
        t = 0
        P_S = self.physicsToolbox.calculateAccumulatorPressureFromVolume(integrableStates["V_A"])
        integrableStates["P_S"] = P_S
        integrableStates["Volt"] = 0
        integrableStates["motorControllerIntegrator"] = 0
        signals = self.externalSignals.getAllSignals(integrableStates, t)
        Q_T = signals["Q_T"]
        V = signals["V"]

        Q_A = Q_T - integrableStates["Q_S"]

        output = {"I" : integrableStates["I"],
            "Q_S" : integrableStates["Q_S"],
            "V_A" : integrableStates["V_A"],
            "P_S" : P_S,
            "P_A" : P_S,
            "Q_A" : Q_A,
            "dQ_S" : 0,
            "Q_T" : Q_T,
            "Volt" : V,
            "Fail" : 0,
            "motorControllerIntegrator" : 0.0
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
        V_A_candidate = lastFullState["V_A"] + dV_A_candidate * dt
        if lastFullState["V_A"] <= 0:
            V_A = 0

        # if accumulator has been depleted, calculate with no accumulator
        # don't trust these values. differentiation is bad
        if V_A_candidate <= 0:
            fail = 1
            Q_A = 0
            # Q_A = lastFullState["V_A"] / dt
            alpha = self.parameters["alphaAccumulatorFlowEmpty"]
            Q_A = alpha * Q_A + (1 - alpha) * lastFullState["Q_A"]
            V_A = 0.0
            Q_S = Q_T - Q_A
            dQ_S = (Q_S - lastFullState["Q_S"]) / dt
            if self.useSteadyStateCurrent:
                I = self.physicsToolbox.calculateSteadyStateCurrentFromVoltage(V, Q_S)
            else:
                dI = self.physicsToolbox.calculateDCurrent(lastFullState["I"], lastFullState["Q_S"], V)
                I = lastFullState["I"] + dI * dt
            P_S = self.physicsToolbox.calculateSupplyPressureBackwardsUsingMotor(I, Q_S, dQ_S)
            alpha = self.parameters["alphaSupplyPressureDifferentiation"]
            P_S = alpha * P_S + (1 - alpha) * lastFullState["P_S"]
            P_A = self.physicsToolbox.calculateAccumulatorPressureFromVolume(V_A)
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
            P_A = P_S

        if P_S < self.parameters["minimumSupplyPressure"]:
            fail = 1
        else:
            fail = 0
        if lastFullState["Fail"] == 1:
            fail = 1
            
        output = {"P_S" : P_S,
                "P_A" : P_A,
                "Q_A" : Q_A,
                "Q_S" : Q_S,
                "dQ_S" : dQ_S,
                "V_A" : V_A,
                "Q_T" : Q_T,
                "I" : I,
                "Volt" : V,
                "Fail" : fail,
                "motorControllerIntegrator" : lastFullState["motorControllerIntegrator"]
            }

        return output

    def getStateUnitProperties(self):
        return HPUDynamicsNoNozzle.stateUnitProperties