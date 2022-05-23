from abc import abstractmethod

from numpy import ndarray
from DefaultOutputPlotter import DefaultOutputPlotter
from StateUnitProperties import StateUnitProperties
from pyqSlider import Slider
from abc import ABC, abstractmethod

class FullSimulationExecutor(ABC):
    def setParameters(self, parameters):
        self.parameters = parameters

    @abstractmethod
    def getPlots(self) -> tuple[ndarray, dict]:
        pass

    @abstractmethod
    def getStateUnitProperties(self):
        pass

class SliderProperties:
    def __init__(self, min, max, resolution):
        self.min = min
        self.max = max
        self.resolution = resolution

class SliderOnPlotScale:
    def __init__(self, simulationExecutor : FullSimulationExecutor, plotsMap, defaultParameters, sliderMap : dict):
        self.sliders = {}
        for name in sliderMap.keys():
            properties = sliderMap[name]
            slider = Slider(properties.min, properties.max, properties.resolution, name)
            slider.connectValueChanged(self.sliderUpdate)
            self.sliders[name] = slider
        self.simulationExecutor = simulationExecutor
        self.plotsMap = plotsMap
        self.defaultParameters = defaultParameters
        
        
    def sliderUpdate(self):
        parameters = self.defaultParameters
        for name in self.sliders.keys():
            value = self.sliders[name].x
            parameters[name] = value

        self.simulationExecutor.setParameters(parameters)
        time, output = self.simulationExecutor.getPlots()
        for name in output.keys():
            self.plotsMap[name].setData(time, output[name])

    def getKeys(self):
        return self.sliders.keys()

class SliderOutputPlotter:
    def __init__(self, fullSimulationExecutor : FullSimulationExecutor, 
                    defaultParameters, sliderMap):
        stateUnitProperties = fullSimulationExecutor.getStateUnitProperties()
        fullSimulationExecutor.setParameters(defaultParameters)
        initialTimes, initialOutputs = fullSimulationExecutor.getPlots()
        self.plotter = DefaultOutputPlotter("untitled", initialTimes, initialOutputs, stateUnitProperties)
        self.plotter.plot()
        plotsMap = self.plotter.getModelsMap()
        self.slidersManager = SliderOnPlotScale(fullSimulationExecutor, plotsMap, defaultParameters, sliderMap)
        self.addSlidersToPlot()

    def plot():
        pass

    def addSlidersToPlot(self):
        layout = self.plotter.getLayout()
        
        for name in self.slidersManager.getKeys():
            layout.addWidget(self.slidersManager.sliders[name], colspan=2)
            layout.nextRow()