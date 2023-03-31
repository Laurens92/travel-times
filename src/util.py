# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 20:55:59 2017

@author: Laurens
"""

# Flat earth coördinates to latitude, longitude
def flat2lla(East_m,North_m, long0,lat0):
    import math
    import numpy as np
    R = 6378136.6 # meters
    f = 1/298.257223563 # flattening
    
    Rn = R/(1-(2*f - f**2)*(math.sin(lat0*math.pi/180))**2)**0.5
    Rm = Rn * (1-(2*f - f**2))/(1-(2*f - f**2)*(math.sin(lat0*math.pi/180))**2)

    lat = np.zeros(len(North_m))
    long = np.empty(len(North_m))

    for i in range(0,len(North_m)):
        dlong = math.atan(1/(Rn*math.cos(lat0*math.pi/180))) * East_m[i] * 180/math.pi
        long[i] = long0 + dlong

        dlat = math.atan(1/Rm) * North_m[i] * 180/math.pi
        lat[i] = lat0 + dlat

    return long, lat