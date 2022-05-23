# All math is done in SI units. these properties can be used to scale to human-preferred units

class StateUnitProperties:
    def __init__(self, name : str, SIUnits : str, preferredUnits : str, scalingSIToPreferred):
        self.name = name
        self.SIUnits = SIUnits
        self.preferredUnits = preferredUnits
        self.scalingSIToPreferred = scalingSIToPreferred