# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# import libraries

import numpy as np
import pandas as pd
from math import radians, sqrt, sin, cos, atan2


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# some functions

# find direction from point b to point a
def find_direction(a, b):
    xdiff = b[0] - a[0]
    ydiff = b[1] - a[1] 

    if xdiff > 0:
        hm = -1         # if xB > xA it moves left
    elif xdiff == 0:
        hm = 0         # if xB = xA it does not move
    else:
        hm = 1         # if xB < xA it moves right

    if ydiff > 0:
        vm = -1         # if yB > yA it moves down
    elif ydiff == 0:
        vm = 0         # if yB + yA it does not move
    else:
        vm = 1         # if yB < yA it moves up

    return (hm, vm)

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
def constructSequence(data, neighborsAB, slope, M, N, distances, reporting, prec, lons, lats, save, name):
    if reporting:
        print('_________Step 3: Construct Sequence__________')

    # bathymetry at end points
    if reporting:
        print('Calculating bathymetry at endpoints ...')
    if slope == 1:
        btmA =  data[data['pos'] == (0,0)]['btm'].values[0]
        btmB =  data[data['pos'] == (M,N)]['btm'].values[0]

    elif slope == -1:
        btmA =  data[data['pos'] == (0,0)]['btm2'].values[0]
        btmB =  data[data['pos'] == (M,N)]['btm2'].values[0]

    # # # # # # # # # # # # # # # # # # # # # # #
    # construct value function
    if reporting:
        print('Constructing value function ...')
    V = {}
    U = {}

    total_keys = len(neighborsAB.keys())
    processed = 0
    for key in reversed(list(neighborsAB.keys())):
        value = neighborsAB[key]
        n = len(value)

        processed += 1
        percentage = (processed / total_keys) * 100
        print(f"  Progress: {percentage:.1f}%", end='\r')  

        z = key
        if n == 0:
            # add length to surface at endpoint B
            V[z] = abs(btmB)

            U[z] = (0,0)

        elif n == 1:
            zn = value[0]

            znidx = distances.loc[(distances['End'] == zn) & (distances['Start'] == z)].index[0]

            wn = distances['Distance'][znidx]
            V[z] = abs(wn + V[zn])

            Uh, Uv = find_direction(zn,z)
            U[z] = (Uh, Uv)       

        elif n == 3:
            zv = value[0]
            zh = value[1]
            zd = value[2]
            
            zhidx =  distances.loc[(distances['End'] == zh) & (distances['Start'] == z)].index[0]
            zvidx =  distances.loc[(distances['End'] == zv) & (distances['Start'] == z)].index[0]
            zdidx =  distances.loc[(distances['End'] == zd) & (distances['Start'] == z)].index[0]
            
            wh = distances['Distance'][zhidx]
            wv = distances['Distance'][zvidx]
            wd = distances['Distance'][zdidx]
            
            V[z] = min(abs(wh + V[zh]), abs(wv + V[zv]), abs(wd + V[zd]))

            if V[z] == wh + V[zh]:
                zn = zh
            elif V[z] == wv + V[zv]:
                zn = zv
            elif V[z] == wd + V[zd]:
                zn = zd

            Uh, Uv = find_direction(zn,z)
            U[z] = (Uh, Uv) 

    # add length to surface at endpoint A
    V[(0,0)] = V[(0,0)] + abs(btmA)

    # calculate minimal route
    Vmin = round(V[(0,0)], prec)

    # # # # # # # # # # # # # # # # # # # # # # #
    # recover optimal control sequence
    if reporting:
        print('Recovering optimal control sequence ...')
        
    z = (0,0)
    u = [z]
    while True:

        value = neighborsAB[z]
        n = len(value)

        if n == 0:
            break

        elif n == 1:

            zn = value[0] 

            u.append(zn)

            z = zn

        elif n == 3:
            zv = value[0]
            zh = value[1]
            zd = value[2]
            
            zhidx =  distances.loc[(distances['End'] == zh) & (distances['Start'] == z)].index[0]
            zvidx =  distances.loc[(distances['End'] == zv) & (distances['Start'] == z)].index[0]
            zdidx =  distances.loc[(distances['End'] == zd) & (distances['Start'] == z)].index[0]

            if z == (0,0):
                c = V[z] - abs(btmA)
            else:
                c = V[z]

            ch = V[zh]
            cv = V[zv]
            cd = V[zd]

            if round(c - ch,prec) == distances['Distance'][zhidx]:
                zn = zh
                u.append(zn)
                z = zn
            elif round(c - cv,prec) == distances['Distance'][zvidx]:
                zn = zv
                u.append(zn)
                z = zn
            elif round(c - cd,prec) == distances['Distance'][zdidx]:
                zn = zd
                u.append(zn)
                z = zn

    # # # # # # # # # # # # # # # # # # # # # # #
    # calculate optimal path cost
    pcost = []
    for p in range(len(u)-1):
        start = u[p]
        end = u[p+1]

        pcost.append(distances[(distances['Start'] == start) & (distances['End'] == end)].values[0][2])

    ucost_bottom = sum(pcost)
    ucost = ucost_bottom + abs(btmA) + abs(btmB)

    # flip sequence
    if slope == 1:
        u = u
    elif slope == -1:
        u = [(x, N - y) for x, y in u]

    # calculate area dimensions
    al = haversine(min(lats), min(lons), min(lats), max(lons))*1000
    aw = haversine(min(lats), min(lons), max(lats), min(lons))*1000
    a = al * aw

    # # # # # # # # # # # # # # # # # # # # # # #
    # reporting             
    # check result
    if reporting:
        print('==========================')
        print('Report')
        print(f'Region of analysis: \n Longitude = [{min(lons):.4f},{max(lons):.4f}] °W \n Latitude = [{min(lats):.4f},{max(lats):.4f}] °N \n Length = {al:.0f}(m) \n Width = {aw:.0f} (m) \n Total area ~ {a:.0f} (m^2)')
        if ucost == Vmin:
            print(f'The control sequence finds the least costly path with with a value of {ucost:.2f} m')
            print(f'The optimal control sequence is {u}')
        else:
            print(f'The control sequence does not find the least costly path. \n Dynamic programming  = {Vmin} m \n Control sequence = {ucost} m')

    if reporting:
        print('***Sequence construction done***')
        print('')

    # # # # # # # # # # # # # # # # # # # # # # #
    # save results
    if save:
        # save sequence
        seq = pd.DataFrame()
        for coord in u:
            seqx = data[data['pos'] == coord][['lon', 'lat', 'pos']]
            seq = pd.concat([seq,seqx])

        data_name = name + '_data.feather'
        seq_name = name + '_seq.feather'

        # save feather file
        data.to_feather(data_name)
        seq.to_feather(seq_name)     

    return btmA, btmB, u, ucost, data, seq
