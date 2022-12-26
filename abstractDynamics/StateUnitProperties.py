# All math is done in SI units. these properties can be used to scale to human-preferred units
from util.UnitConversions import SIConversionMap

class StateUnitProperties:
    def __init__(self, name : str, preferredUnits : str):
        self.name = name
        self.preferredUnits = preferredUnits
        self.scalingSIToPreferred = SIConversionMap[preferredUnits]

    def convertSIToPreferred(self, valueSI):
        return valueSI * self.scalingSIToPreferred

    def convertPreferredToSI(self, valuePreferred):
        return valuePreferred / self.scalingSIToPreferred