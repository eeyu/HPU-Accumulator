from abstractDynamics.StateUnitProperties import StateUnitProperties

# This list only affect what gets plotted. No effect on the actual physics
stateUnitProperties = {# External signals
                            "Volt" : StateUnitProperties("motorVoltage", "V"),
                            "Q_T" : StateUnitProperties("totalFlowOut", "L/min"),
                            # "dQ_S" : StateUnitProperties("supplyFlowAccelerationOut", "m3/s^2", "L/min^2", 3600000),
                            "Q_S" : StateUnitProperties("supplyFlowOut", "L/min"),
                            "Q_A" : StateUnitProperties("accumulatorFlowOut", "L/min"),
                            "V_A" : StateUnitProperties("accumulatorFluidVolume", "L"),
                            "P_A" : StateUnitProperties("accumulatorPressure", "psi"),
                            "P_S" : StateUnitProperties("supplyPressure", "psi"),
                            "I"   : StateUnitProperties("motorCurrent", "A"),
                            
                            'Fail' : StateUnitProperties("simulationFailed", "-"),
                            # 'nozzleError' : StateUnitProperties("P_S nozzle - noNozzle * 1e15", "psi")
                        }