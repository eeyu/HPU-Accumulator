from HPUNozzlelessDynamics import HPUDynamicsNoNozzlePhysics
import numpy as np

initialPressure = 10.0
maxVolume = 10.0
gasConstant = 1.0
PVConstant = initialPressure * np.power(maxVolume, gasConstant)
parameters = {"accumulatorGasConstant" : gasConstant,
            "accumulatorVolume" : maxVolume,
            "initialGasPVConstant" : PVConstant }

physics = HPUDynamicsNoNozzlePhysics(parameters)

def calculateNextPVThroughVolume(Q_A, P_last, V_last, dt):
    V = V_last - Q_A * dt
    P = physics.calculateAccumulatorPressureFromVolume(V)
    return {"P" : P,
        "V" : V}

def calculateNextPVThroughPressure(Q_A, P_last, V_last, dt):
    dP = physics.calculateDAccumulatorPressure(P_last, Q_A)
    P = P_last + dt * dP
    V = physics.calculateAccumulatorVolumeFromPressure(P)
    return {"P" : P,
        "V" : V}

P_last = 1000
V_last = physics.calculateAccumulatorVolumeFromPressure(P_last)
Q_A = -0.1
dt = 0.1
print(calculateNextPVThroughPressure(Q_A, P_last, V_last, dt))
print(calculateNextPVThroughVolume(Q_A, P_last, V_last, dt))