import numpy as np

# All math can be referenced here:
# https://docs.google.com/presentation/d/1F06h3KazdXrJqL3oXz7IlBEz1O0cy0PYbd30vnif52o/edit#slide=id.g12aaf72706b_0_158

class HPUPhysicsToolbox:
    def __init__(self, parameters : dict):
        self.parameters = parameters

    def calculateAccumulatorVolumeFromPressure(self, P_A):
        a = self.parameters["accumulatorGasConstant"]
        gasVolume = np.power(self.parameters["initialGasPVConstant"] / P_A, 1.0/a)
        return self.parameters["accumulatorVolume"] - gasVolume

    
    def calculateLinearAccumulatorPressureFromVolume(self, V_A):
        mlin = (self.parameters["accumulatorGasConstant"] * np.power((self.parameters["accumulatorPrechargePressure"] * 
                np.power(self.parameters["accumulatorVolume"], self.parameters["accumulatorGasConstant"])), -1/self.parameters["accumulatorGasConstant"])
             * np.power(self.parameters["operatingPressure"], 1+1/self.parameters["accumulatorGasConstant"]))
        V_A_default = (self.parameters["accumulatorVolume"] - np.power(self.parameters["accumulatorPrechargePressure"] * 
                np.power(self.parameters["accumulatorVolume"], self.parameters["accumulatorGasConstant"]) / 
                self.parameters["operatingPressure"], 1/self.parameters["accumulatorGasConstant"]))
        return mlin * (V_A - V_A_default) + self.parameters["operatingPressure"]

    def calculateAccumulatorPressureFromVolume(self, V_A):
        if V_A < 1.0e-9:
            V_A = 0.0
        a = self.parameters["accumulatorGasConstant"]
        gasVolume = self.parameters["accumulatorVolume"] - V_A
        return self.parameters["initialGasPVConstant"] / np.power(gasVolume, a)

    def calculateAccumulatorGasPVConstant(P_A, V_A, gasConstant):
        return P_A * np.power(V_A, gasConstant)

    def calculateSteadyStateCurrentFromVoltage(self, voltage, flow):
        return (voltage - self.parameters['motorTorqueConstant'] * flow / self.parameters['pumpDisplacement']) / self.parameters['motorResistance']

    def calculateDCurrent(self, current, flow, voltage):
        return ((- self.parameters["motorResistance"] * current
            + voltage
            - self.parameters["motorTorqueConstant"] * flow / self.parameters['pumpDisplacement']) 
            / self.parameters["motorInductance"])

    def calculateSupplyPressureFromNozzle(self, P_A, Q_A):
        nozzleArea = (np.pi * np.power(self.parameters["accumulatorNozzleDiameter"]/2.0, 2))
        # Q_A > 0 means flowing outwards
        if (Q_A > 0): # then P_A > P_S
            return P_A - np.power((Q_A / nozzleArea / self.parameters["nozzleDischargeCoefficient"]), 2) * self.parameters["fluidDensity"] / 2.0
        else:
            return P_A + np.power((Q_A / nozzleArea / self.parameters["nozzleDischargeCoefficient"]), 2) * self.parameters["fluidDensity"] / 2.0
        
    
    def calculateDMotorFlow(self, current, motorFlow, supplyPressure):
        return ((self.parameters["motorTorqueConstant"] * current 
            - self.parameters["motorViscousConstant"] * motorFlow / self.parameters["pumpDisplacement"]
            - supplyPressure * self.parameters["pumpDisplacement"])
            / (self.parameters["motorInertia"] / self.parameters["pumpDisplacement"]))

    def calculateSupplyPressureBackwardsUsingMotor(self, current, motorFlow, dMotorFlow):
        return ((self.parameters["motorTorqueConstant"] * current
            - self.parameters["motorViscousConstant"] * motorFlow / self.parameters["pumpDisplacement"]
            - self.parameters["motorInertia"] / self.parameters["pumpDisplacement"] * dMotorFlow)
            / (self.parameters["pumpDisplacement"]))

    def getVoltageToMaintainSupplyPressureAtSteadyState(self, P_S):
        return P_S * self.parameters["pumpDisplacement"] * self.parameters["motorResistance"] / self.parameters["motorTorqueConstant"]
  