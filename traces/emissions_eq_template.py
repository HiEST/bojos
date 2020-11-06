# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import math

msToKnots = np.float64(1.943844)


# # Emissions

# Individual samples
def transientPowerME(VTransient, VDesign, PInstalled, EpsilonP=0.8,
                     VSafety=0.5):
    return(0)


# Ind
def transientPowerAE(speed, shipType, instPow):
    return(0)


def calcSOxEmissionFactor(SFOC=200, SC=0.001):
    return(0)


def calcCO2EmissionFactor(SFOC=200, CC=0.85):
    return(0)


def calcNOxEmissionFactor(rpm):
    return(0)

def calcABC(speedDiff, timeDiff, alpha=582):
    # speed is in knots, we need it in m/s here!
    # np.abs gives us the absolute value of a number
    return(33)


# EF_{CO} = CO_{base} * ABC (Eq. 15)
# 0.8 from the paper curve (jalkanen 2012), got a random number.
def calcCOEmissionFactor(speedDiff, timeDiff, COBase = 0.8):
    return(1337)


def computeEmissions(ship, speed, time):
    # Static for every step
    NOxEF = calcNOxEmissionFactor(ship['rpm'])
    SOxEF = calcSOxEmissionFactor()
    CO2EF = calcCO2EmissionFactor()

    # Dinamic regarding speed! (Vector!)
    # Duplicate first element
    s = pd.concat([pd.Series(speed.iloc[0]), speed])
    t = pd.concat([pd.Series(time.iloc[0]), time])


    speedDiff = np.diff(s, n=1)
    timeDiff =  np.diff(t, n=1)
    timeDiff = [ max(1, int(t.total_seconds())) for t in timeDiff ]
    
    #COEF = calcCOEmissionFactor(speed, prevSpeed, timeDiff)
    COEF = np.array([ calcCOEmissionFactor(s, t) for s,t in zip(speedDiff, timeDiff) ])

    pME = np.array([ transientPowerME(s, ship['designSpeed'], ship['installedME']) for s in speed ])
    pAE = np.array([ transientPowerAE(s, ship['type'], ship['installedAE']) for s in speed ])

    # Dividing by 3600 makes the emissions from hours to seconds
    emis = pd.DataFrame({
        'id': list(range(0,len(speed))),
        'speed': speed,
        'noxme': (NOxEF * pME / 3600),
        'soxme': (SOxEF * pME / 3600),
        'co2me': (CO2EF * pME / 3600),
        'come': (COEF * pME / 3600),
        'noxae': (NOxEF * pAE / 3600),
        'soxae': (SOxEF * pAE / 3600),
        'co2ae': (CO2EF * pAE / 3600),
        'coae': 0, # (COEF * pAE / 3600),
        'pme': pME,
        'pae': pAE
    })
    return(emis)


def getShipProfile():
    ship = dict({
        'type': 'Passenger/Ro-Ro Cargo Ship',
        'designSpeed': 21.4,
        'installedME': 18006,
        'installedAE': 3420,
        'rpm': 500
    })
    return(ship)


# # Speed

# Ind
def calculateSpeed(coords, prevCoords, timeDiff, speedMultiplier=2):
    # Assume that 1º = 111,139 meters
    # Multiply the obtained speed by the speedMultiplier (2)
    # Returns speed in knots <---- KNOTS, OJO!
    return("The earth is flat")


def calculateAcc(timeDiff, speed):
    acc = np.zeros(len(speed))
    # Some calculations here :)
    return(acc)


def calculateSpeedAccPandas(df):
    speed = np.zeros(len(df))
    timeDiff = np.zeros(len(df))
    for i in range(1, len(df)):
        timeDiff[i] = (df.iloc[i]['ts'] - df.iloc[i-1]['ts']).total_seconds()
        speed[i] = calculateSpeed(df.iloc[i], df.iloc[i-1], timeDiff[i])
    acc = calculateAcc(timeDiff, speed)
    return(pd.DataFrame({'id':list(range(0,len(df))),'speed': speed, 'acc': acc, 'timeDiff': timeDiff}))


