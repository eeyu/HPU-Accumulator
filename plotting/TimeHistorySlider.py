from plotting.pyqSlider import Slider
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget
import util.MathUtil as mu
import numpy as np


class TimeHistorySlider:
    def __init__(self, maxTime, dt):
        self.slider = Slider(minimum=0, maximum=maxTime, resolution=dt, name="time")
        self.slider.connectValueChanged(self.sliderUpdate)
        self.labels = {}
        self.lines = []
        self.nextBtn = QtGui.QPushButton('+1')
        self.prevBtn = QtGui.QPushButton('-1')
        self.nextBtn.clicked.connect(self.nextButtonUpdate)
        self.prevBtn.clicked.connect(self.prevButtonUpdate)
        self.dt = dt

    def getSliderWidget(self):
        return self.slider

    def getNextButtonWidget(self):
        return self.nextBtn

    def getPrevButtonWidget(self):
        return self.prevBtn

    def setModelReference(self, models : dict):
        self.models = models

    def addLineToPlot(self, plotWidget):
        line = pg.InfiniteLine(angle=90, movable=False, pos=0)
        plotWidget.addItem(line)
        self.lines.append(line)  

    def createAndGetTextForPlot(self, plot, name):
        label = QLabel()
        label.setText(name)
        self.labels[name] = label
        return label

    def sliderUpdate(self):
        time = self.slider.getValue()
        for line in self.lines:
            line.setValue(time)

        for name in self.models.keys():
            times, values = self.models[name].getData()
            value = mu.quickInterp(time, times, values, self.dt)
            # value = np.interp(time, times, values) 
            self.labels[name].setText(name + ": {0:.6g}".format(value))

    def refreshData(self):
        self.sliderUpdate()

    def nextButtonUpdate(self):
        self.slider.moveSliderByTicks(1)

    def prevButtonUpdate(self):
        self.slider.moveSliderByTicks(-1)