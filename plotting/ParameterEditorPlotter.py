from abc import abstractmethod

from numpy import ndarray
from abstractDynamics.ParameterProperties import ParameterProperties
from plotting.DefaultOutputPlotter import DefaultOutputPlotter
from abstractDynamics.StateUnitProperties import StateUnitProperties
from plotting.DropdownSelector import DropdownSelector
from plotting.SingleParameterWidget import SingleParameterWidget
from plotting.TimeHistorySlider import TimeHistorySlider
from plotting.pyqSlider import Slider
from abc import ABC, abstractmethod
from abstractDynamics.ParameterProperties import ParameterProperties

class FullSimulationExecutor(ABC):
    def setParameters(self, parameters):
        self.parameters = parameters

    @abstractmethod
    def getPlots(self) -> tuple[ndarray, dict]:
        pass

    @abstractmethod
    def getStateUnitProperties(self):
        pass

class BoundedParameterProperties:
    def __init__(self, minScale, maxScale, start, resolution):
        self.minScale = minScale
        self.maxScale = maxScale
        self.start = start
        self.resolution = resolution

class EnumParameterProperties:
    def __init__(self, dictionary : dict, default):
        self.dictionary = dictionary
        self.default = default

class BooleanParameterProperties:
    def __init__(self, default):
        self.default = default

class ParameterEditorGUIOnPlot:
    def __init__(self, simulationExecutor : FullSimulationExecutor, 
            plotsMap, defaultParameterProperties : dict[str, ParameterProperties], 
            parameterSelectionMap : dict,
            timeDataManager : TimeHistorySlider):
        self.parameterWidgets : dict[str, SingleParameterWidget] = {}

        for name in parameterSelectionMap.keys():
            edittorProperties = parameterSelectionMap[name]
            unit = defaultParameterProperties[name].preferredUnits
            if type(edittorProperties) == BoundedParameterProperties:
                slider = Slider(edittorProperties.minScale * edittorProperties.start, 
                    edittorProperties.maxScale * edittorProperties.start, 
                    edittorProperties.start, 
                    edittorProperties.resolution, 
                    name, unit=unit)
                slider.connectValueChanged(self.selectorUpdate)
                self.parameterWidgets[name] = slider
            elif type(edittorProperties) == EnumParameterProperties:
                dropDown = DropdownSelector(edittorProperties.dictionary, edittorProperties.default)
                dropDown.connectValueChanged(self.selectorUpdate)
                self.parameterWidgets[name] = dropDown
            elif type(edittorProperties) == BooleanParameterProperties:
                slider = Slider(0, 1, 
                    edittorProperties.default, 1, 
                    name, unit="")
                slider.connectValueChanged(self.selectorUpdate)
                self.parameterWidgets[name] = slider
        self.simulationExecutor = simulationExecutor
        self.plotsMap = plotsMap
        self.defaultParameterProperties = defaultParameterProperties
        self.parametersInSI = ParameterProperties.convertPropertiesMapToValuesMapInSI(defaultParameterProperties)
        self.timeDataManager = timeDataManager
        
    def selectorUpdate(self):
        for name in self.parameterWidgets.keys():
            valueInPreferred = self.parameterWidgets[name].getValue()
            if type(self.parameterWidgets[name]) == DropdownSelector:
                self.parametersInSI[name] = valueInPreferred
            else:
                self.parametersInSI[name] = self.defaultParameterProperties[name].convertPreferredToSI(valueInPreferred)

        self.simulationExecutor.setParameters(self.parametersInSI)
        time, output = self.simulationExecutor.getPlots()
        for name in output.keys():
            self.plotsMap[name].setData(time, output[name])
        
        self.timeDataManager.refreshData()

    def refreshParameters(self):
        self.selectorUpdate()

    def getKeys(self):
        return self.parameterWidgets.keys()

class ParameterEditorPlotter:
    def __init__(self, fullSimulationExecutor : FullSimulationExecutor, 
                    defaultParameterProperties, sliderMap):
        defaultParameters = ParameterProperties.convertPropertiesMapToValuesMapInSI(defaultParameterProperties)
        stateUnitProperties = fullSimulationExecutor.getStateUnitProperties()

        fullSimulationExecutor.setParameters(defaultParameters)
        initialTimes, initialOutputs = fullSimulationExecutor.getPlots()
        self.plotter = DefaultOutputPlotter("untitled", initialTimes, initialOutputs, stateUnitProperties)
        self.plotter.plot()
        self.timeHistorySlider = self.plotter.getTimeDataManager()
        plotsMap = self.plotter.getModelsMap()

        self.parameterEditorManager = ParameterEditorGUIOnPlot(fullSimulationExecutor, 
            plotsMap, 
            defaultParameterProperties, 
            sliderMap, 
            self.timeHistorySlider)
        self.addSlidersToPlot()
        self.parameterEditorManager.refreshParameters()

    def plot():
        pass

    def addSlidersToPlot(self):
        layout = self.plotter.getLayout()
        layout.nextRow()
        rowIndex = 0
        
        for name in self.parameterEditorManager.getKeys():
            # layout.nextRow()
            layout.addWidget(self.parameterEditorManager.parameterWidgets[name], colspan=1)
            rowIndex += 1
            if (rowIndex == 3):
                rowIndex = 0
                layout.nextRow()