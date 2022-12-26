# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:57:24 2022

@author: eyu
"""

from email.policy import default
from queue import Full
from abstractDynamics.ExternalSignal import ExternalSignalCollection
from abstractDynamics.ParameterProperties import ParameterProperties
from hpuDynamics.FlowDataProperties import FlowDataProperties
from hpuDynamics.HPUCollectiveDynamics import HPUCollectiveDynamics
from hpuDynamics.HPUNozzleDynamics import HPUDynamicsNozzle
from hpuDynamics.HPUNozzlelessDynamics import HPUDynamicsNoNozzle
from hpuDynamics.HPUPhysics import HPUPhysicsToolbox
from abstractDynamics.Simulation import Simulation
from hpuDynamics.VoltageController import *
from hpuDynamics.FlowProvider import FlowFunctionGenerator, FlowSignalFromFile, ConstantFlowSignal
from plotting.DefaultOutputPlotter import DefaultOutputPlotter
from hpuDynamics.NameToHeaderMap import NameToHeaderMap
from abstractDynamics.StateUnitProperties import StateUnitProperties
import util.UnitConversions as uc
import scipy.signal
from plotting.ParameterEditorPlotter import BooleanParameterProperties, EnumParameterProperties, ParameterEditorPlotter, FullSimulationExecutor, BoundedParameterProperties
import hpuDynamics.HPUCommonStateUnitProperties as stateUP

from pyqtgraph.Qt import QtGui, QtCore
 #dd
defaultParameterProperties = {# Desired/Controller
                    "operatingPressure" : ParameterProperties(3000.0, "psi"),
                    "minimumSupplyPressure" : ParameterProperties(2400.0, "psi"),
                    "motorVoltage" : ParameterProperties(90.0, "V"), #check? nominal is 60
                    # Accumulator
                    "removeAccumulator" : ParameterProperties(False, "-"), 
                    "accumulatorVolume" : ParameterProperties(460.0, "cc"), #
                    "accumulatorPrechargePressure" : ParameterProperties(2000.0, "psi"),
                    "accumulatorGasConstant" : ParameterProperties(1.4, "-"), # nitrogen cp/cv. technically not the "gas constant"
                    "alphaSupplyPressureDifferentiation" : ParameterProperties(0.001, "-"),
                    "alphaAccumulatorFlowEmpty" : ParameterProperties(0.01, "-"),
                    # Motor / Pump
                    "pumpDisplacement" : ParameterProperties(6.29e-6 / (2.0 * np.pi), "m3/rad"), 
                    "motorTorqueConstant" : ParameterProperties(0.3286, "SI"),
                    "motorViscousConstant" : ParameterProperties(0.00811937, "SI"), # calculated from steady state values. bw==T
                    "motorInductance" : ParameterProperties(0.000080, "H"), 
                    "motorResistance" : ParameterProperties(0.0330, "ohm"), 
                    "motorInertia" : ParameterProperties(4.45e-3, "kgm2"), 
                    "motorKi" : ParameterProperties(0, "-"), #5e-5
                    # Nozzle
                    "accumulatorNozzleDiameter" : ParameterProperties(12.0, "mm"), 
                    "fluidDensity" : ParameterProperties(870.0, "kg/m3"), # Castrol Hyspin AWS 32
                    "fluidViscosity" : ParameterProperties(0.001, "SI"), #double check. not currently used in calcs
                    "accumulatorNozzleLength" : ParameterProperties(0.020, "m"), #m, not currently used
                    "nozzleDischargeCoefficient" : ParameterProperties(0.6, "-"), # conventional approx for turbulent
                    # Hyperparams
                    "useFuncGenFlowSignal" : ParameterProperties(True, "-"), 
                    "flowFuncGenOffset" : ParameterProperties(5.0, "L/min"), 
                    "flowFuncGenAmplitude" : ParameterProperties(5.0, "L/min"), 
                    "flowFuncGenPeriodOffset" : ParameterProperties(0.0, "s"),
                    "flowFuncGenFrequency" : ParameterProperties(2.0, "hz"), 
                    "flowFuncGenMode" : ParameterProperties("sin", None), 
                    "useNozzle" : ParameterProperties(False, "-"),
                    "flowDataFile" : ParameterProperties(FlowDataProperties("forward6.csv", NameToHeaderMap.realMap), None),
                    "useSteadyStateCurrent" : ParameterProperties(True, "-"),
                    "useLinear" : ParameterProperties(False, "-")
                    }

parameterSelectionMap = {
            # "useLinear" : BooleanParameterProperties(
            #     default=defaultParameterProperties["useLinear"].getDefaultValueInPreferredUnit()),
        # Function Generator
            "useFuncGenFlowSignal" : BooleanParameterProperties(
                default=defaultParameterProperties["useFuncGenFlowSignal"].getDefaultValueInPreferredUnit()),
            "flowFuncGenOffset" : BoundedParameterProperties(
                minScale=0, 
                maxScale=10.0, 
                start=defaultParameterProperties["flowFuncGenOffset"].getDefaultValueInPreferredUnit(),
                resolution=0.1),
            "flowFuncGenAmplitude" : BoundedParameterProperties(
                minScale=0, 
                maxScale=4.0, 
                start=defaultParameterProperties["flowFuncGenAmplitude"].getDefaultValueInPreferredUnit(),
                resolution=0.1),
            "flowFuncGenFrequency" : BoundedParameterProperties(
                minScale=0, 
                maxScale=20.0, 
                start=defaultParameterProperties["flowFuncGenFrequency"].getDefaultValueInPreferredUnit(),
                resolution=1.0),
            "flowFuncGenMode" : EnumParameterProperties(
                dictionary = {"sin" : "sin",
                                "constant" : "constant",
                                "step" : "step",
                              },
                default="constant"),
            "flowDataFile" : EnumParameterProperties(
                dictionary = {"forward6" : FlowDataProperties("forward6.csv", NameToHeaderMap.realMap),
                                "quickWalk" : FlowDataProperties("quickWalk.csv", NameToHeaderMap.scriptSimMap),
                                "stairsDownFast" : FlowDataProperties("stairsDownFast.csv", NameToHeaderMap.scriptSimMap),
                                "stairsUpSlow" : FlowDataProperties("stairsUpSlow.csv", NameToHeaderMap.scriptSimMap)
                              },
                default="forward6"),
        # Accumulator and pressure
            # "operatingPressure" : BoundedParameterProperties(
            #     minScale=0.5, 
            #     maxScale=1.5, 
            #     start=defaultParameterProperties["operatingPressure"].getDefaultValueInPreferredUnit(),
            #     resolution=10.),
            "accumulatorPrechargePressure" : BoundedParameterProperties(
                minScale=0.5, 
                maxScale=1.5, 
                start=defaultParameterProperties["accumulatorPrechargePressure"].getDefaultValueInPreferredUnit(),
                resolution=10.),
            "accumulatorVolume" : BoundedParameterProperties(
                minScale=0.5, 
                maxScale=1.5, 
                start=defaultParameterProperties["accumulatorVolume"].getDefaultValueInPreferredUnit(),
                resolution=10.),
            # "removeAccumulator" : BooleanParameterProperties(
            #     default=defaultParameterProperties["removeAccumulator"].getDefaultValueInPreferredUnit()),
        # Nozzle
            "useNozzle" : BooleanParameterProperties(
                default=defaultParameterProperties["useNozzle"].getDefaultValueInPreferredUnit()),
            "accumulatorNozzleDiameter" : BoundedParameterProperties(
                minScale=0.000001,
                maxScale=1.0, 
                start=defaultParameterProperties["accumulatorNozzleDiameter"].getDefaultValueInPreferredUnit(),
                resolution=0.00001),
        # Motor
            # "useSteadyStateCurrent" : BooleanParameterProperties(
            #     default=defaultParameterProperties["useSteadyStateCurrent"].getDefaultValueInPreferredUnit()),
            "motorVoltage" : BoundedParameterProperties(
                minScale=0.6666, 
                maxScale=1.0, 
                start=defaultParameterProperties["motorVoltage"].getDefaultValueInPreferredUnit(),
                resolution=30.),
            "motorKi" : BoundedParameterProperties(
                minScale=0.0, 
                maxScale=10.0, 
                start=defaultParameterProperties["motorKi"].getDefaultValueInPreferredUnit(),
                resolution=2.0e-6),
        }
            

class HPUSimulationExecutor(FullSimulationExecutor):
    def getStateUnitProperties(self):
        return stateUP.stateUnitProperties

    def getPlots(self):
        dt = 0.001
        parameters = self.parameters

        physicsToolbox = HPUPhysicsToolbox(parameters)

        if (parameters["useFuncGenFlowSignal"]):
            flowProvider = FlowFunctionGenerator(offset=parameters["flowFuncGenOffset"],
                amplitude=parameters["flowFuncGenAmplitude"],
                frequency=parameters["flowFuncGenFrequency"],
                periodOffset=parameters["flowFuncGenPeriodOffset"])
            flowProvider.setModeByName(parameters["flowFuncGenMode"])
            maxTime = 7
        else:
            filename = "./data/" + parameters["flowDataFile"].fileName
            nameToHeaderMap = parameters["flowDataFile"].nameToHeaderMap
            flowProvider = FlowSignalFromFile(filename, nameToHeaderMap, samplingDt=0.001)
            maxTime = flowProvider.getMaxTime()

        voltageController = PIVoltageController(maxVoltage=parameters["motorVoltage"], 
            maxPressure=parameters["operatingPressure"], 
            minPressure=parameters["minimumSupplyPressure"],
            dt=dt,
            ki=parameters["motorKi"],
            minVoltage=0,
            # minVoltage=physicsToolbox.getVoltageToMaintainSupplyPressureAtSteadyState(parameters["operatingPressure"]),
            alpha=0.05)
        
        externalSignals = ExternalSignalCollection()
        externalSignals.addSignalProvider(voltageController)
        externalSignals.addSignalProvider(flowProvider)
        dynamics = HPUCollectiveDynamics(parameters, externalSignals)

        simulation = Simulation(dynamics)

        initialPressure = parameters["operatingPressure"]
        initialIntegrableState = {"V_A" : physicsToolbox.calculateAccumulatorVolumeFromPressure(P_A = initialPressure),
                                "I" : 0, #this value does not matter anymore
                                "Q_S" : 0}
        initialState = dynamics.getInitialFullStateFromIntegrables(initialIntegrableState)

        # plottingDt = 0.001
        # simulationDt = 0.0001

        
        return simulation.simulate(initialState, dt, maxTime)
        
plotter = ParameterEditorPlotter(HPUSimulationExecutor(), defaultParameterProperties, parameterSelectionMap)
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()