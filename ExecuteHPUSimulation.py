# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:57:24 2022

@author: eyu
"""

from ExternalSignal import ExternalSignalCollection
from HPUNozzlelessDynamics import HPUDynamicsNoNozzle, HPUDynamicsNoNozzlePhysics
from Simulation import Simulation
from VoltageController import *
from FlowProvider import FlowSignalFromFile, ConstantFlowSignal
from DefaultOutputPlotter import DefaultOutputPlotter
from NameToHeaderMap import NameToHeaderMap
from StateUnitProperties import StateUnitProperties
import UnitConversions as uc
import scipy.signal

from pyqtgraph.Qt import QtGui, QtCore

filename = "./data/forward1.csv"
nameToHeaderMap = NameToHeaderMap.realMap
parameters = {# Desired/Controller
              "operatingPressure" : uc.PSIToPascal(3000.0), #pa
              "minimumSupplyPressure" : uc.PSIToPascal(2400.0),
              "motorVoltage" : 90.0, #check? nominal is 60
              # Accumulator
              "accumulatorNozzleDiameter" : 0.012, #m
              "accumulatorVolume" : 0.00046, #m3
              "accumulatorPrechargePressure" : uc.PSIToPascal(2700.0),
              "accumulatorGasConstant" : 1.4, # nitrogen cp/cv. technically not the "gas constant"
              # Motor / Pump
              "pumpDisplacement" : 6.29e-6 / (2.0 * np.pi), #m3/rad
              "motorTorqueConstant" : 0.3286,
              "motorViscousConstant" : 0.00811937, # calculated from steady state values. bw==T
              "motorInductance" : 0.000080, #H
              "motorResistance" : 0.0330, #ohm
              "motorInertia" : 4.45e-3, # kgm2
              # Nozzle
              "fluidDensity" : 1000.0, # water, but we are using oil. double check
              "fluidViscosity" : 0.001, #double check
              "accumulatorNozzleLength" : 0.020, #m
              }
physicsToolbox = HPUDynamicsNoNozzlePhysics(parameters)

flowProvider = FlowSignalFromFile(filename, nameToHeaderMap, samplingDt=0.001)
# flowProvider = ConstantFlowSignal(0)
# voltageController = ConstantVoltageController(parameters["motorVoltage"])
# voltageController = MaxPressureVoltageController(parameters["motorVoltage"], maxPressure=parameters["operatingPressure"])
voltageController = ProportionalVoltageController(maxVoltage=parameters["motorVoltage"], 
    maxPressure=parameters["operatingPressure"], 
    minPressure=parameters["minimumSupplyPressure"],
    minVoltage=physicsToolbox.getVoltageToMaintainSupplyPressureAtSteadyState(parameters["operatingPressure"]))
# print(physicsToolbox.getVoltageToMaintainSupplyPressureAtSteadyState(parameters["operatingPressure"]))
# voltageController = StepVoltageController(parameters["motorVoltage"], 1)
externalSignals = ExternalSignalCollection()
externalSignals.addSignalProvider(voltageController)
externalSignals.addSignalProvider(flowProvider)
dynamics = HPUDynamicsNoNozzle(parameters, externalSignals, useSteadyStateCurrent=False)

simulation = Simulation(dynamics)

initialPressure = uc.PSIToPascal(3000.0)
initialIntegrableState = {"V_A" : physicsToolbox.calculateAccumulatorVolumeFromPressure(P_A = initialPressure),
                        "I" : initialPressure * parameters["pumpDisplacement"] / parameters["motorTorqueConstant"],
                        "Q_S" : 0}
initialState = dynamics.getInitialFullStateFromIntegrables(initialIntegrableState)

dt = 0.001
maxTime = 7
# maxTime = flowProvider.getMaxTime()
timeHistory, outputHistory = simulation.simulate(initialState, dt, maxTime)

def printOutputsAtIndex(i, outputHistory):
    print(i)
    for key in outputHistory.keys():
        print(key + ": " + str(outputHistory[key][i]))
        
def filterOutputs(outputHistory, dt):
    bfilt = scipy.signal.butter(1, 1/dt/10, btype='low', analog=False, fs=1/dt, output='sos')
    filteredOutputs = {}
    for key in outputHistory.keys():
        filteredOutputs[key] = scipy.signal.sosfilt(bfilt, outputHistory[key])
    return filteredOutputs

# for i in range(2):
#     printOutputsAtIndex(i, outputHistory)

filteredOutputs = filterOutputs(outputHistory, dt)
plotter = DefaultOutputPlotter("untitled", timeHistory, outputHistory, dynamics.getStateUnitProperties())
# plotter = DefaultOutputPlotter("unt", timeHistory, filteredOutputs, dynamics.getStateUnitProperties())
if __name__ == '__main__':
    import sys
    plotter.plot()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()