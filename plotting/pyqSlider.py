# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 16:02:58 2022

@author: eyu
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QSlider

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget
from plotting.SingleParameterWidget import SingleParameterWidget

class Slider(SingleParameterWidget):
    def __init__(self, minimum, maximum, start=None, resolution=1.0, name="", parent=None, unit=""):
        super(Slider, self).__init__(parent=parent)
        self.resolution = resolution
        self.name = name
        if start is None:
            start = minimum
        self.unit = unit

        # Set up the slider
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(int(minimum / resolution))
        self.slider.setMaximum(int(maximum / resolution))
        self.slider.setValue(int(start / resolution))
        self.slider.valueChanged.connect(self.setLabelValue)

        # Set up the layout
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.label = QLabel(self)
        self.horizontalLayout.addWidget(self.slider)
        self.horizontalLayout.addWidget(self.label)
        # spacerItem1 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.x = None
        self.setLabelValue(self.slider.value())
        
    def setLabelValue(self, value):
        self.x = float(value) * self.resolution
        self.label.setText(self.name + ": {0:.4g}".format(self.x) + " " + self.unit)

    def getValue(self):
        return self.x

    def connectValueChanged(self, update):
        self.slider.valueChanged.connect(update)

    def getWidget(self):
        return self.slider

    def moveSliderByTicks(self, ticks):
        newValue = self.slider.value() + ticks
        if newValue < self.slider.minimum():
            newValue = self.slider.minimum()
        if newValue > self.slider.maximum():
            newValue = self.slider.maximum()
        self.slider.setValue(newValue)