from abc import ABC, abstractmethod
import numpy as np

class ExternalSignalProvider(ABC):
    @abstractmethod
    def getSignal(self, state, t):
        pass

    @abstractmethod
    def getName(self):
        pass

class ExternalSignalCollection:
    def __init__(self):
        self.collection = []

    def addSignalProvider(self, provider : ExternalSignalProvider):
        self.collection.append(provider)

    def getAllSignals(self, state, t):
        signals = {}
        for provider in self.collection:
            signals[provider.getName()] = provider.getSignal(state, t)
        return signals

    