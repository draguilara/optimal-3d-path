# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# import libraries

import matplotlib.pyplot as plt
from scipy.interpolate import griddata

import numpy as np
import pandas as pd


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# some functions

# 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def plotRoute(data, reporting, seq, ucost, M, N, btmA, btmB, suptitle, save, name, plot2D, plot3D, levels, msize):
    if reporting:
        if plot2D | plot3D:
            print('_____________Step 4: Plot Route______________')
        else:
            print('No plotting requested.')

    # # # # # # # # # # # # # # # # # # # # # # #
    # plot results
    if plot2D | plot3D:
        btm_2Dcolor = 'twilight_shifted'
        btm_3Dcolor = 'bone'

        x = data['x']
        y = data['y']
        z = data['btm']      
        lon = data['lon']
        lat = data['lat']

        btm_mn = min(z)
        btm_mx = max(z)
        btm_avg = 0.5*(btm_mn+btm_mx)
        btm0_mn = btm_avg
        btm0_mx = -btm_avg

        ulon = seq['lon'].to_list()
        ulat = seq['lat'].to_list()
        upos = [(int(arr[0]), int(arr[1])) for arr in seq['pos'].to_list()]
        ux, uy = zip(*upos)
        uz = [data[(data['x'] == ux) & (data['y'] == uy)]['btm'].values[0] for ux, uy in upos]

        # define grid.
        lons = np.linspace(lon.min(), lon.max(), len(lon.unique()))
        lats = np.linspace(lat.min(), lat.max(), len(lat.unique()))
        lons, lats = np.meshgrid(lons, lats)

    if plot2D:
        if reporting:
            print('Plotting 2D ....')

        fig = plt.figure(figsize=(10, 7))
        ax = plt.axes()    

        # plot optimal path
        plt.plot(ulon,ulat, 'red')

        # Interpolate unstructured D-dimensional data.
        grid = griddata((lon, lat), z, (lons, lats), method='cubic', )

        # Create contour plot.
        plt.contourf(lons, lats, grid, cmap = btm_2Dcolor, norm=plt.Normalize(vmin=btm0_mn, vmax=btm0_mx), levels = levels)
        plt.colorbar(label='Bathymetry (m)')


        # plot labels
        plt.xlabel('Longitue (°W)')
        plt.ylabel('Latitude (°N)')
        plt.title(f'Total distance: {ucost:.0f} m')
        plt.suptitle(suptitle)

        fig1 = plt.gcf()       

        plt.show()

    if plot3D:
        if reporting:
            print('Plotting 3D ....')

        # initialize plot
        fig = plt.figure(figsize=(10, 7))
        ax = plt.axes(projection="3d")

        # scatter plot
        scat = ax.scatter3D(x, y, z, c=z, cmap=btm_3Dcolor,marker='s',alpha = 0.2, norm=plt.Normalize(btm_mn, btm_mx*8), s=msize)

        # colorbar
        cbar = plt.colorbar(scat, shrink=0.5)
        cbar.set_label('Bathymetry (m)')

        # path plot
        ax.plot(ux, uy, uz, color='r', linewidth = 2)
        ax.plot([ux[0],ux[0]], [uy[0],uy[0]], [0, btmA], color='r', linewidth = 2)
        ax.plot([ux[-1],ux[-1]], [uy[-1],uy[-1]], [0, btmB], color='r', linewidth = 2)      
        
        # plot labels
        plt.xlabel('Longitue (°W)')
        plt.ylabel('Latitude (°N)')
        plt.title(f'Total distance: {ucost:.0f} m')
        plt.suptitle(suptitle)

        # set ticks
        nticks = 3
        xticks = np.linspace(min(x), max(x), nticks)
        yticks = np.linspace(min(y), max(y), nticks)

        ax.set_xticks(xticks)
        ax.set_xticklabels(np.round(np.linspace(min(lon),max(lon),nticks),5))
        ax.xaxis.set_tick_params(pad=10)
        ax.xaxis.labelpad = 15

        ax.set_yticks(yticks)
        ax.set_yticklabels(np.round(np.linspace(min(lat),max(lat),nticks),5)) 
        ax.yaxis.set_tick_params(pad=10)
        ax.yaxis.labelpad = 15

        # viewwing angle
        # first angle is rotation along a horizontal axis
        # second angle is rotation along a vertical axis
        # ax.view_init(80, 280)
        ax.view_init(20, 140)

        fig2 = plt.gcf()         
                
        plt.show()

    # # # # # # # # # # # # # # # # # # # # # # #
    # save results
    if save:
        # save plots
        if reporting:
                print('Saving plots...')
        if plot2D:
            fig1_name = name + '2D.png'
            fig1.savefig(fig1_name, dpi=1000)
            if reporting:
                print('2D plot saved.')
        
        if plot3D:
            fig2_name = name + '3D.png'
            fig2.savefig(fig2_name, dpi=1000)
            if reporting:
                print('3D plot saved.')

        
