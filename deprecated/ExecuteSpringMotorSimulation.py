# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:57:24 2022

@author: eyu
"""

from Simulation import Simulation
from SpringDynamics import SpringDynamics, SpringlessDynamics
from FlowProvider import FlowSignalFromFile, ConstantFlowSignal
from DefaultOutputPlotter import DefaultOutputPlotter
from NameToHeaderMap import NameToHeaderMap
import scipy.signal

from pyqtgraph.Qt import QtGui, QtCore

filename = "./data/forward1.csv"
nameToHeaderMap = NameToHeaderMap.realMap
dt = 0.001

parameters = {"springConstant" : 500, #N/m
              "motorRadius" : 0.01, #m
              "I" : 6,
              "motorTorqueConstant" : 0.3286,
              "motorDamping" : 0.01,
              "motorInductance" : 0.0331, #0.001040
              "motorResistance" : 0.033,
              "motorInertia" : 1, #kgm^4,
              "dt" : dt,
              "inputScaling" : 100
              }

flowProvider = FlowSignalFromFile(filename, nameToHeaderMap, samplingDt=0.001)
# flowProvider = ConstantFlowSignal(1)

springDynamics = SpringDynamics(parameters)
springSimulation = Simulation(springDynamics, flowProvider)

springlessDynamics = SpringlessDynamics(parameters)
springlessSimulation = Simulation(springlessDynamics, flowProvider)


initialStateSpringed = {"x" : 0,
                        "V_m" : 0}

initialStateSpringless = {}

maxTime = 5
# maxTime = flowProvider.getMaxTime()
timeHistorySpring, outputHistorySpring = springSimulation.simulate(initialStateSpringed, dt, maxTime)
timeHistorySpringless, outputHistorySpringless = springlessSimulation.simulate(initialStateSpringless, dt, maxTime)

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

# filteredOutputs = filterOutputs(outputHistory, dt)
# plotter = DefaultOutputPlotter("unt", timeHistory, outputHistory, dynamics.getParameterProperties())
plotter1 = DefaultOutputPlotter("Spring", timeHistorySpring, outputHistorySpring, springDynamics.getParameterProperties())
plotter2 = DefaultOutputPlotter("Springless", timeHistorySpringless, outputHistorySpringless, springlessDynamics.getParameterProperties())

print(outputHistorySpringless["T_m"]  )
if __name__ == '__main__':
    import sys
    plotter1.plot()
    plotter2.plot()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()