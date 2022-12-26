# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 13:45:09 2022

@author: eyu
"""

import numpy as np

def findNearestValueInArray(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def findLowerBoundValueInIncreasingArray(array, value, step):
    minimum = array[0]
    difference = value - minimum
    index = int(difference / step)
    return array[index], index

# For an ordered, increasing driving array
def quickInterp(value, drivingArray, drivenArray, step):
    lowerDrivingValue, lowerDrivingIndex = findLowerBoundValueInIncreasingArray(drivingArray, value, step)
    scale = (value - lowerDrivingValue) / step
    
    lowerDrivenValue = drivenArray[lowerDrivingIndex]
    upperDrivenValue = drivenArray[lowerDrivingIndex + 1]
    return lowerDrivenValue + scale * (upperDrivenValue - lowerDrivenValue)

# def interpolateFromOrderedDrivingArray(drivingArray, value, drivenArray):
    # nearestDrivingValue, nearestDrivingIndex = findNearest(drivingArray, value)
    # nearestValueIsLarger = nearestDrivingValue > value
    
    # boundingDrivingIndex = nearestDrivingIndex - 1 if nearestValueIsLarger else nearestDrivingIndex + 1
    # boundingDrivingValue = drivingArray[boundingDrivingIndex]
    
    # if boundingDrivingIndex < 0 or boundingDrivingIndex > drivingArray.size():
    #     print("error interpolation")
    #     return False
    
    # drivenBound1 = drivenArray[nearestDrivingIndex]
    # drivenBound2 = drivenArray[boundingDrivingIndex]
    
    # return interpolate()