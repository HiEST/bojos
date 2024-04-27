import pandas as pd
import numpy as np
import math

pi = np.float64(3.14159)
earthR = np.float64(6378100)
msToKnots = np.float64(1.943844)


# # Emissions

# Ind
def transientPowerME(VTransient, VDesign, PInstalled, EpsilonP=0.8,
                     VSafety=0.5):
    if VTransient > VDesign:
        VTransient = VDesign
    if VTransient < 0:
        VTransient = 0
    k = (EpsilonP * PInstalled) / ((VDesign + VSafety) ** 3)
    return k * (VTransient ** 3)


# Ind
def transientPowerAE(speed, shipType, instPow):
    if pd.isnull(instPow):
        return 0.0
    # Cruisers, Ro-Ro and passenger ships
    if (shipType == "Passenger (Cruise) Ship" or
            shipType == "Passenger/Ro-Ro Cargo Ship" or
            shipType == "Passenger Ship"):
        if instPow <= 0:
            return 4000.0
        return min(4000.0, instPow)
    # The rest
    res = 1000.0
    if speed > 1 and speed <= 5:
        res = 1250.0
    if speed > 5:
        res = 750.0
    if instPow > 0 and res > instPow:
        res = instPow
    return res


def calcSOxEmissionFactor(SFOC=200, SC=0.001):
    nS = (SFOC * SC) / 32.0655
    mSOx = 64.06436 * nS
    return mSOx


def calcCO2EmissionFactor(SFOC=200, CC=0.85):
    nC = (SFOC * CC) / 12.01
    mCO2 = 44.00886 * nC
    return mCO2


def calcNOxEmissionFactor(rpm):
    res = 0
    if rpm > 0:
        if rpm < 130:
            res = 17.0
        else:
            if rpm < 2000:
                res = 45 * (rpm ** (-0.2))
            else:
                res = 9.8
    return res

def calcABC(speedDiff, timeDiff, alpha=582):
    # speed is in knots, we need it in m/s here!
    abc = alpha*(np.abs(speedDiff/msToKnots)/timeDiff)

    # Is it max? paper might be wrong
    if (abc < 1):
        abc = 1 # If LESS than 1, value is 1

    return(abc)


# EF_{CO} = CO_{base} * ABC (Eq. 15)
# 0.8 from the paper curve (jalkanen 2012), got a random number.
def calcCOEmissionFactor(speedDiff, timeDiff, COBase = 0.8):
    ABC = calcABC(speedDiff, timeDiff)
    return(COBase * ABC)


def estimateEmission(factor, power, sampleGranularity=1, unit=1):
    return (factor * power / 3600.0) / unit * sampleGranularity


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
    #timeDiff = [ int(t)/pow(10,9) for t in timeDiff ]
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
    # Deg. to radians
    lat1 = coords['lat'] * pi / 180.0
    lon1 = coords['lon'] * pi / 180.0

    lat2 = prevCoords['lat'] * pi / 180.0
    lon2 = prevCoords['lon'] * pi / 180.0

    # P
    rho1 = earthR * math.cos(lat1)
    z1 = earthR * math.sin(lat1)
    x1 = rho1 * math.cos(lon1)
    y1 = rho1 * math.sin(lon1)

    # Q
    rho2 = earthR * math.cos(lat2)
    z2 = earthR * math.sin(lat2)
    x2 = rho2 * math.cos(lon2)
    y2 = rho2 * math.sin(lon2)

    # Dot product
    dot = (x1 * x2 + y1 * y2 + z1 * z2)
    cosTheta = dot / (earthR * earthR)
    if (cosTheta > 1):
        cosTheta = 1
    elif (cosTheta < 0):
        cosTheta = 0

    theta = math.acos(cosTheta)

    # Distance in Meters
    dist = earthR * theta


    speed = dist / timeDiff


    # Returns speed in knots
    return (speed * msToKnots * speedMultiplier)


def calculateAcc(timeDiff, speed):
    acc = np.zeros(len(speed))
    for i in range(1, len(speed)):
        acc[i] = (speed[i] - speed[i-1])/timeDiff[i]
    return(acc)


def calculateSpeedAccPandas(df):
    speed = np.zeros(len(df))
    timeDiff = np.zeros(len(df))
    for i in range(1, len(df)):
        timeDiff[i] = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds()
        speed[i] = calculateSpeed(df.iloc[i], df.iloc[i-1], timeDiff[i])
    acc = calculateAcc(timeDiff, speed)
    return(pd.DataFrame(
                        {'id': list(range(0, len(df))), 'speed': speed,
                         'acc': acc, 'timeDiff': timeDiff
                        }
                       )
          )
