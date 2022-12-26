from util.UnitConversions import SIConversionMap

class ParameterProperties:
    def __init__(self, defaultBalueInPreferred : float, preferredUnits : str):
        self.preferredUnits = preferredUnits
        if preferredUnits is not None:
            self.scalingSIToPreferred = SIConversionMap[preferredUnits]
            self.defaultValueInSI = defaultBalueInPreferred / self.scalingSIToPreferred
            self.defaultValueInPreferred = defaultBalueInPreferred
        else:
            self.defaultValueInSI = defaultBalueInPreferred
            self.defaultValueInPreferred = defaultBalueInPreferred

    def getDefaultValueInSI(self):
        return self.defaultValueInSI

    def getDefaultValueInPreferredUnit(self):
        return self.defaultValueInPreferred

    def convertSIToPreferred(self, value):
        return value * self.scalingSIToPreferred
    
    def convertPreferredToSI(self, value):
        return value / self.scalingSIToPreferred

    def convertPropertiesMapToValuesMapInSI(propertiesMap : dict):
        valuesMap = {}
        for name in propertiesMap.keys():
            valuesMap[name] = propertiesMap[name].getDefaultValueInSI()

        return valuesMap