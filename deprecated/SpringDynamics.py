from re import X
from DerivativeMonitor import DerivativeMonitor
from Dynamics import Dynamics, ParameterProperties

class SpringDynamics(Dynamics):
    def __init__(self, parameters):
        self.parameters = parameters
        self.parameterProperties = {"x" : ParameterProperties("springDeflection", "m", "m", 1),
                            "dx" : ParameterProperties("springVelocity", "m/s", "m/s", 1),
                            "T_m" : ParameterProperties("torqueOnMotor", "Nm", "Nm", 1),
                            "V_m" : ParameterProperties("motorVelocity", "m/s", "m/s", 1),
                            "dV_m" : ParameterProperties("motorAcceleration", "m/s2", "m/s2", 1.),
                            "V_o" : ParameterProperties("signalVelocity", "m/s", "m/s", 1),
                            }
        self.dVmMonitor = DerivativeMonitor()
        self.dxMonitor = DerivativeMonitor()
                            

    def getOutputForCurrentState(self, state : dict, inputSignal : dict, t):
        I = self.parameters["I"]
        V_o = inputSignal["Q_T"] * self.parameters["inputScaling"] # this is in m3/s
        V_m = state["V_m"]
        x = state["x"]

        dV_m = self.dVmMonitor.getDerivativeAfterNextMeasurement(V_m, self.parameters["dt"])
        dx = self.dxMonitor.getDerivativeAfterNextMeasurement(x, self.parameters["dt"])

        T_m = self.parameters["springConstant"] * x

        # Convert to outputs
        output = {"x" : x,
                "dx" : dx,
                "T_m" : T_m,
                "V_m" : V_m,
                "dV_m" : dV_m,
                "V_o" : V_o
                  }
        return output

    def getStateDims(self):
        return 2
    
    def getFullStateNames(self):
        return self.parameterProperties.keys()

    def getDState(self, output : dict, t):
        dV_m = ((self.parameters["motorTorqueConstant"] * self.parameters["I"]
                - self.parameters["motorDamping"] / self.parameters["motorRadius"] * output["V_m"]
                - output["T_m"]) /
                self.parameters["motorInertia"] / self.parameters["motorRadius"])
        dx = output["V_m"] - output["V_o"]
        return {"V_m" : dV_m,
                "x" : dx}

    def getParameterProperties(self):
        return self.parameterProperties

class SpringlessDynamics(Dynamics):
    def __init__(self, parameters):
        self.parameters = parameters
        self.parameterProperties = {"x" : ParameterProperties("springDeflection", "m", "m", 1.),
                            "dx" : ParameterProperties("springVelocity", "m/s", "m/s", 1.),
                            "T_m" : ParameterProperties("torqueOnMotor", "Nm", "m", 1.),
                            "V_m" : ParameterProperties("motorVelocity", "m/s", "m/s", 1.),
                            "dV_m" : ParameterProperties("motorAcceleration", "m/s2", "m/s2", 1.),
                            "V_o" : ParameterProperties("signalVelocity", "m/s", "m/s", 1.),
                            }
        self.dVmMonitor = DerivativeMonitor()
    
    def getOutputForCurrentState(self, state : dict, inputSignal : dict, t):
        # there is no state...
        I = self.parameters["I"]
        V_o = inputSignal["Q_T"] * self.parameters["inputScaling"] # this is in m3/s
        V_m = V_o
        dV_m = self.dVmMonitor.getDerivativeAfterNextMeasurement(V_m, self.parameters["dt"])

        T_m = (self.parameters["motorTorqueConstant"] * I
                - self.parameters["motorDamping"] / self.parameters["motorRadius"] * V_m
                - self.parameters["motorInertia"] / self.parameters["motorRadius"] * dV_m)

        # Convert to outputs
        output = {"x" : 0,
                "dx" : 0,
                "T_m" : T_m,
                "V_m" : V_m,
                "dV_m" : dV_m,
                "V_o" : V_o
                  }
        return output

    def getDState(self, output : dict, t):
        return {}

    def getParameterProperties(self):
        return self.parameterProperties

    def getStateDims(self):
        return 0
    
    def getFullStateNames(self):
        return self.parameterProperties.keys()

        

    
