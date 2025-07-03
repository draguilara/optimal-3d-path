# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# import libraries

import numpy as np
import pandas as pd
from math import radians, sqrt, sin, cos, atan2

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# some functions

# calculate distnace over the surface of the earth using haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radius of Earth in kilometers
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def evaluatePoints(data, neighbors, slope, reporting, prec):
    if reporting:
        print('__________Step 2: Evaluate Points___________')


    # calculate distances between points, considering elevation
    if reporting:
        print('Calculating distances between points, considering elevation ...')

    total_items = len(neighbors)
    index = 0
    distances = []
    for key in neighbors:
        value = neighbors[key]
        n = len(value)

        index += 1
        percentage = (index / total_items) * 100
        print(f"   Progress: {percentage:.1f}%", end='\r') 

        i = key[0]
        j = key[1]

        for p in value:
            ii = p[0]
            jj = p[1]

            a = (i,j)
            b = (ii,jj)

            aidx = data.loc[data['pos'] == a].index[0]
            bidx = data.loc[data['pos'] == b].index[0]

            if slope == 1:
                alat = data['lat'][aidx]
                alon = data['lon'][aidx]

                blat = data['lat'][bidx]
                blon = data['lon'][bidx]

                abtm = data['btm'][aidx]
                bbtm = data['btm'][bidx]
                
            elif slope == -1:
                alat = data['lat2'][aidx]
                alon = data['lon2'][aidx]

                blat = data['lat2'][bidx]
                blon = data['lon2'][bidx]

                abtm = data['btm2'][aidx]
                bbtm = data['btm2'][bidx]

            # calculate haversine distance
            d = haversine(alat,alon,blat,blon)*1000

            # calculate difference in elevation
            h = bbtm - abtm

            # use pythagoras to approximate total distance
            c = round(sqrt(d**2 + h**2),prec)
            
            distances.append({'Start': a, 'End': b, 'Distance': c})

    if reporting:
        print('Creating DataFrame of distances...')
    distances = pd.DataFrame(distances)

    if reporting:
        print('***Points evaluation done***')
        print('')

    return distances
