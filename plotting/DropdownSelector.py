from pyqtgraph import ComboBox
from plotting.SingleParameterWidget import SingleParameterWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton

class DropdownSelector(SingleParameterWidget):
    def __init__(self, dictionary, defaultText, parent=None):
        super(DropdownSelector, self).__init__(parent=parent)
        self.dictionary = dictionary
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(dictionary.keys())
        self.comboBox.setCurrentText(defaultText)

    def getValue(self):
        text = self.comboBox.currentText()
        return self.dictionary[text]

    def connectValueChanged(self, update):
        self.comboBox.activated.connect(update)

    def getWidget(self):
        return self.comboBox