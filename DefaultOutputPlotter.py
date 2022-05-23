# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 11:00:16 2022

@author: eyu
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqSlider import Slider
from StateUnitProperties import StateUnitProperties

class SliderWithLines:
    def __init__(self, lines, minVal, maxVal):
        self.slider = Slider(minVal, maxVal)
        self.slider.slider.valueChanged.connect(self.sliderUpdate)
        self.lines = lines
        
    def sliderUpdate(self):
        idx = self.slider.x
        for line in self.lines:
            line.setValue(idx)

class DefaultOutputPlotter():
    def __init__(self, name, timeHistory, outputHistory, stateUnitProperties : StateUnitProperties):
        self.name = name
        self.logNamesToPlot = outputHistory.keys()
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', 'w')
        
        self.stateUnitProperties = stateUnitProperties
        
        # set up containers
        self.plots = []
        self.models = {}
        self.docks = []
        self.layouts = []
        self.sliders = []
        
        # Set up plotter
        self.app = QtGui.QApplication([])
        self.win = QtGui.QMainWindow()
        self.area = DockArea()
        self.win.setCentralWidget(self.area)
        self.win.resize(1000,600)
        self.win.setWindowTitle(self.name)
        pg.setConfigOptions(antialias=True)
        
        # Default Params
        self.defaultColor = (0, 140, 170)
        self.mirrorColor = (190, 75, 50)
        self.maxRowLength = 3        
        
        self.timeHistory = timeHistory
        self.outputHistory = outputHistory

    def plot(self):
        d1 = Dock("temp")
        layout = pg.LayoutWidget()
        rowIndex = 0
        layout.addLabel(self.name + ": ", colspan=1)
        # layout.nextRow()
        
        lines = []
        # slider = SliderWithLines(lines, 0, self.timeHistory.size)
        
        # layout.addWidget(slider.slider, colspan=2)
        layout.nextRow()
        
        for logName in self.logNamesToPlot:
            # Main Plot
            p1 = pg.PlotWidget(title=self.stateUnitProperties[logName].name)
            p1.setLabel('bottom', "time" )
            p1.setLabel('left', logName, units = self.stateUnitProperties[logName].preferredUnits )
            p1.addLegend()
            model = p1.plot(y=self.outputHistory[logName],
                    x=self.timeHistory,
                    pen=self.defaultColor, 
                    name = 'time')
            # p1.plot(y=data.getAverageTimePlotForName(logName), pen=self.defaultColor, name = 'avg')
            # p1.plot(y=data.getMaxTimePlotForName(logName), pen=self.defaultColor, name = 'max')
            p1.showGrid(x = True, y = True, alpha = 0.3)                                        
            
            # Line on x
            line = pg.InfiniteLine(angle=90, movable=False, pos=0)
            p1.addItem(line)
            lines.append(line)
            
            # layout stuff
            layout.addWidget(p1)
            self.plots.append(p1)
            self.models[logName] = model
            
            rowIndex += 1
            if (rowIndex == 3):
                rowIndex = 0
                layout.nextRow()
                
                
        # slider.lines = lines
        d1.addWidget(layout)
        
        self.area.addDock(d1, 'left')

        # Save everything
        self.docks.append(d1)
        self.layout = layout
        # self.sliders.append(slider)
        
        self.win.show()

    def getModelsMap(self):
        return self.models

    def getLayout(self):
        return self.layout