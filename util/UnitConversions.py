def PSIToPascal(pressurePSI):
    return 6894.76 * pressurePSI

def LminToM3s(flowLmin):
    return flowLmin / 60000.0

SIConversionMap = {
    # Pressure
    "pa" : 1.0,
    "psi" : 0.000145038,
    "bar" : 1.0e-5,

    # Length
    "m" : 1.0,
    "mm" : 0.001,

    # Density
    "kg/m3" : 1.0,

    # Flow
    "m3/s" : 1.0,
    "L/min" : 60000.0,

    # Pump Displacement
    "m3/rad" : 1.0,

    # Frequency
    "hz" : 1.0,

    # Time
    "s" : 1.0,

    # Volume
    "m3" : 1.0,
    "L" : 1000.0,
    "cc" : 1000000.0,

    # Electrical
    "V" : 1.0,
    "A" : 1.0,
    "H" : 1.0,
    "ohm" : 1.0,
    "kgm2" : 1.0,

    # Unitless/dont care
    "-" : 1.0,
    "SI" : 1.0
}

def convertFromSIToUnit(value, unit):
    return SIConversionMap[unit] * value

def convertFromUnitToSI(value, unit):
    return value/ SIConversionMap[unit]