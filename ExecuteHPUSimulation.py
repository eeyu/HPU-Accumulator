# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:57:24 2022

@author: eyu
"""

from Simulation import Simulation
from Dynamics import HPUDynamics
from VoltageController import *
from InputSignalProvider import FlowSignalFromFile, ConstantFlowSignal
from DefaultOutputPlotter import DefaultOutputPlotter
from NameToHeaderMap import NameToHeaderMap
import scipy.signal

from pyqtgraph.Qt import QtGui, QtCore

filename = "./data/forward1.csv"
nameToHeaderMap = NameToHeaderMap.realMap
parameters = {"operatingPressure" : 2.1e7, #pa
              "accumulatorNozzleDiameter" : 0.012, #m
              "accumulatorVolume" : 0.00046, #m3
              "accumulatorPrechargePressure" : 1.9e7,
              "accumulatorNozzleLength" : 0.020,
              "motorVoltage" : 60,
              "pumpDisplacement" : 6.29e-6, #m3
              "motorTorqueConstant" : 0.3286,
              "motorViscousConstant" : 0.00811937,
              "motorInductance" : 0.0331, #0.001040
              "motorResistance" : 0.033,
              "accumulatorGasConstant" : 1.0,
              "fluidDensity" : 1000.0, # water
              "fluidViscosity" : 0.001
              }

flowProvider = FlowSignalFromFile(filename, nameToHeaderMap, dt=0.001)
#flowProvider = ConstantFlowSignal(0)
# voltageController = ConstantVoltageController(parameters["motorVoltage"])
voltageController = MaxPressureVoltageController(parameters["motorVoltage"], parameters["operatingPressure"])
# voltageController = StepVoltageController(parameters["motorVoltage"], 1)
dynamics = HPUDynamics(parameters, voltageController, flowProvider)

simulation = Simulation(dynamics, flowProvider)


# initialState = {"P_A" : parameters["operatingPressure"],
#                 "I" : dynamics.convertSupplyPressureToCurrent(parameters["operatingPressure"])}
# initialState = {"P_A" : parameters["accumulatorPrechargePressure"],
#                 "I" : dynamics.convertSupplyPressureToCurrent(parameters["operatingPressure"])}
initialState = {"P_A" : 3.0e7,
                "I" : dynamics.convertSupplyPressureToCurrent(parameters["operatingPressure"])}

dt = 0.001
maxTime = 10
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

for i in range(2):
    printOutputsAtIndex(i, outputHistory)

filteredOutputs = filterOutputs(outputHistory, dt)
# plotter = DefaultOutputPlotter("unt", timeHistory, outputHistory, dynamics.getParameterProperties())
plotter = DefaultOutputPlotter("unt", timeHistory, filteredOutputs, dynamics.getParameterProperties())
if __name__ == '__main__':
    import sys
    plotter.plot()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()