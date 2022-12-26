# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 11:00:16 2022

@author: eyu
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from plotting.pyqSlider import Slider
from abstractDynamics.StateUnitProperties import StateUnitProperties
from plotting.TimeHistorySlider import TimeHistorySlider
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget

class DefaultOutputPlotter():
    def __init__(self, name, timeHistory, outputHistory, stateUnitProperties : StateUnitProperties):
        self.name = name
        self.logNamesToPlot = stateUnitProperties.keys()
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
        
        self.timeHistorySlider = TimeHistorySlider(maxTime=timeHistory[-1], dt=(timeHistory[1] - timeHistory[0]))
        self.timeHistorySlider.setModelReference(self.models)
        
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
        layout.nextRow()
                
        layout.addWidget(self.timeHistorySlider.getSliderWidget(), colspan=2)
        layout.nextRow()
        layout.addWidget(self.timeHistorySlider.getPrevButtonWidget())
        layout.addWidget(self.timeHistorySlider.getNextButtonWidget())
        layout.nextRow()
        
        for logName in self.logNamesToPlot:
            # Main Plot
            p1 = pg.PlotWidget(title=self.stateUnitProperties[logName].name)
            p1.setLabel('bottom', "time" )
            p1.setLabel('left', logName, units = self.stateUnitProperties[logName].preferredUnits )
            p1.addLegend()
            model = p1.plot(y=self.outputHistory[logName],
                    x=self.timeHistory,
                    pen=self.defaultColor)
            p1.showGrid(x = True, y = True, alpha = 0.3)                                        
            
            # Line on x
            self.timeHistorySlider.addLineToPlot(p1)

            # Wrapper for plot
            verticalLayout = layout.addLayout()
            verticalLayout.addWidget(p1)
            verticalLayout.nextRow()
            text = self.timeHistorySlider.createAndGetTextForPlot(None, logName)
            verticalLayout.addWidget(text)
            
            # layout stuff
            # layout.addWidget(p1)
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

    def getTimeDataManager(self):
        return self.timeHistorySlider