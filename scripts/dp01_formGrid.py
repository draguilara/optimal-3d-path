# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# import libraries

import numpy as np
# import pandas as pd


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# some functions

# find neighbors in an integer grid (diagonal and orthogonal directions)
def find_neighbors(coords):
    neighbors_dict = {}
    total_coords = len(coords)
    processed_coords = 0  # Track how many coordinates we've worked on

    for coord in coords:
        x, y = coord
        neighbors = [(x+i, y+j) for i in [-1, 0, 1] for j in [-1, 0, 1] if i != 0 or j != 0]
        valid_neighbors = [neighbor for neighbor in neighbors if neighbor in coords]
        neighbors_dict[coord] = valid_neighbors

        processed_coords += 1
        completion_percentage = (processed_coords / total_coords) * 100

        print(f"   Progress: {completion_percentage:.1f}%", end='\r')  

    return neighbors_dict

# find neighbors in an integer grid (only orthogonal directions)
def find_neighbors_orthogonal(coords):
    neighbors_dict = {}
    for coord in coords:
        x, y = coord
        neighbors = [(x+i, y) for i in [-1, 0, 1] if i != 0] + [(x, y+j) for j in [-1, 0, 1] if j != 0]
        valid_neighbors = [neighbor for neighbor in neighbors if neighbor in coords]
        neighbors_dict[coord] = valid_neighbors
    return neighbors_dict

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

# finds closest value in another list
def find_closest_value(target, values):
    closest_index = np.argmin(np.abs(values - target))
    return values[closest_index]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def formGrid(btm_df, px, py, qx, qy, reporting):
    if reporting:
        print('______________Step 1: Form Grid______________')


    # adjust points to btm_df
    if reporting:
        print('Adjusting points to btm_df ...')
    px = find_closest_value(px, btm_df['lon'])
    py = find_closest_value(py, btm_df['lat'])
    qx = find_closest_value(qx, btm_df['lon'])
    qy = find_closest_value(qy, btm_df['lat'])

    # create grid 
    if reporting:
        print('Creating grid ...')
    xmax = max(px, qx)
    xmin = min(px, qx)
    ymax = max(py, qy)
    ymin = min(py, qy)
    data = btm_df.query("`lon` >= @xmin and `lon` <= @xmax and `lat` >= @ymin and `lat` <= @ymax")   

    # define A, B, slope
    if px < qx:
        A = (px, py)
        B = (qx, qy)
    elif px > qx:
        A = (qx, qy)
        B = (px, py)

    if A[1] < B[1]:
        slope = 1
    elif A[1] > B[1]:
        slope = -1
    else:
        slope = 0

    lons = data['lon'].drop_duplicates()
    lats = data['lat'].drop_duplicates()

    M = len(lons) - 1
    N = len(lats) - 1

    # get data
    if reporting:
        print('Creating grid positions ...')
    lats = data['lat'].drop_duplicates()
    lons = data['lon'].drop_duplicates()

    # get grid dimensions
    rows = len(lons)
    cols = len(lats)

    # get number of branches G
    G = 2*rows*cols - cols - rows # (m-1)*n + (n-1)*m

    # # # # # # # # # # # # # # # # # # # # # # #
    # create grid of points
    pos = [(i, j) for j in range(cols) for i in range(rows) ]

    if slope == 1:
        posA = (0,0)
        posB = (M,N)
    elif slope == -1:
        posA = (0,N)
        posB = (M,0)

    if reporting:
        print('   Grid positions created.')
        print(f'   # of lats = {len(lats)}')
        print(f'   # of lons = {len(lons)}')
        print(f'   Point A: {posA} = {A}')
        print(f'   Point B: {posB} = {B}')
        print(f'   Slope: {slope}')

    # find valid neighbors of each point
    if reporting:
        print('Finding neighbors...')

    neighbors = find_neighbors(pos)
    if reporting:
        print('   Neighbors found.')

    # # # # # # # # # # # # # # # # # # # # # # #
    # add position column to data
    if reporting:
        print('Adding position to column data ...')
    data = data.copy()
    data['pos'] = pos

    if reporting:
        print('Positioning done.')

    # # # # # # # # # # # # # # # # # # # # # # #
    OO = pos[0]      # start point
    MN = pos[-1]     # end point

    # determine direction of movement
    hm, vm = find_direction(OO,MN)
    # if reporting:
    #     print(f'   Horizontal movement: {-1*hm}')
    #     print(f'   Vertical movement: {-1*vm}')

    if reporting:
        print('Extracting neighbors...')

    # extract neighbors in direction from A to B
    if reporting:
        print('   Extracting A->B neighbors...')
    neighborsAB = {}
    if hm == -1 and vm == -1:
        for key in neighbors:
            neighborsAB[key] =  [value for value in neighbors[key] if value[0] >= key[0] and value[1] >= key[1]]
    elif hm == -1 and vm == 1:
        for key in neighbors:
            neighborsAB[key] =  [value for value in neighbors[key] if value[0] >= key[0] and value[1] <= key[1]]
    elif hm == 1 and vm == -1:
        for key in neighbors:
            neighborsAB[key] =  [value for value in neighbors[key] if value[0] <= key[0] and value[1] >= key[1]]
    elif hm == -1 and vm == -1:
        for key in neighbors:
            neighborsAB[key] =  [value for value in neighbors[key] if value[0] <= key[0] and value[1] <= key[1]]

    # useful note:
            # notice that the neighborsAB are always arranged vertical, horizontal, diagonal
    if reporting:
        print('   Neighbors from A to B extracted.')

    # extract neighbors in direction from B to A
    if reporting:
        print('   Extracting B->A neighbors...')
    neighborsBA = {}
    if hm == -1 and vm == -1:
        for key in neighbors:
            neighborsBA[key] =  [value for value in neighbors[key] if value[0] <= key[0] and value[1] <= key[1]]
    elif hm == -1 and vm == 1:
        for key in neighbors:
            neighborsBA[key] =  [value for value in neighbors[key] if value[0] <= key[0] and value[1] >= key[1]]
    elif hm == 1 and vm == -1:
        for key in neighbors:
            neighborsBA[key] =  [value for value in neighbors[key] if value[0] >= key[0] and value[1] <= key[1]]
    elif hm == -1 and vm == -1:
        for key in neighbors:
            neighborsBA[key] =  [value for value in neighbors[key] if value[0] >= key[0] and value[1] >= key[1]]

    # useful note:
            # notice that the neighborsBA are always arranged diagonal, horizontal, vertical
    if reporting:
        print('   Neighbors from B to A extracted.')

    # # # # # # # # # # # # # # # # # # # # # # # #
    # get flipped btm data (for case 2)
    if reporting:
        print('Generating horizontally flipped bathymetry map (for case 2)...')
    data['x'] = data['pos'].apply(lambda x: x[0])  # Extract y-component from 'pos'
    data['y'] = data['pos'].apply(lambda x: x[1])  # Extract y-component from 'pos' 
    data['y2'] = max(data['y']) - data['y']

    btm_dict = data.set_index('pos')['btm'].to_dict()
    lon_dict = data.set_index('pos')['lon'].to_dict()
    lat_dict = data.set_index('pos')['lat'].to_dict()

    data['lon2'] = data.apply(lambda row: lon_dict[(row['x'], row['y2'])], axis=1)
    data['lat2'] = data.apply(lambda row: lat_dict[(row['x'], row['y2'])], axis=1)
    data['btm2'] = data.apply(lambda row: btm_dict[(row['x'], row['y2'])], axis=1)

    if reporting:
        print('***Grid forming done***')
        print('')

    return data, lons, lats, M, N, A, B, slope, pos, neighbors, neighborsAB, neighborsBA
