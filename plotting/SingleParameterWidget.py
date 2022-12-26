from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget

class SingleParameterWidget(QWidget):
    def __init__(self, parent=None):
        super(SingleParameterWidget, self).__init__(parent=parent)

    def getValue(self):
        pass

    def connectValueChanged(self, update):
        pass

    def getWidget(self):
        pass
