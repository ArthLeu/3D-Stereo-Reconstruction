# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 10:06:23 2018

@author: Anthony

mesh.py

create meshes for pipeline processing
running using demo.py for conveniency
"""
import math
import numpy as np
import scipy.io
from scipy.spatial import Delaunay

import reconstruct as rc


def mesh(GRAB,SCANDIR,UNDISTORTED,THRESH,XRANGE,TRITHRESH,NBR_PASS):
    ''' generate mesh and save as .mat for smoothing and MeshLab '''
    
    ''' 2. Unpack box limit for meshing part 1 '''
    x_up_limit = XRANGE[0]  #250
    x_low_limit = XRANGE[1]    #-250
    y_up_limit = XRANGE[2]     #250
    y_low_limit = XRANGE[3]    #-250
    z_up_limit = XRANGE[4]      #600
    z_low_limit = XRANGE[5]    #0
    
    
    # run reconstruction script
    print("\nReconstruction started...")
    X, xL, xR, L_color, R_color = rc.reconstruct(SCANDIR, THRESH)
    print("Reconstruction done. Meshing started..")
    
    
    ####################################################
    #
    # step 1: remove points outside known bounding box
    #
    npts = np.shape(X)[1]
    goodidx = []
            
    for i in range(npts):
        x_ok = X[0,i] < x_up_limit and X[0,i] > x_low_limit
        y_ok = X[1,i] < y_up_limit and X[1,i] > y_low_limit
        z_ok = X[2,i] < z_up_limit and X[2,i] > z_low_limit
        
        if x_ok and y_ok and z_ok:
            goodidx.append(i)
    
    # check if no index found
    assert(len(goodidx) >= 3), "Error: no points found within range, consider expand boudning box"
    
    # drop the bad points from both 2D and 3D list
    X = X[:,goodidx]
    xL = xL[:,goodidx]
    xR = xR[:,goodidx]
    
    # optional: switch xR with xL
    tri = Delaunay(xR.transpose())
    tridx = tri.simplices
    print('..', end='')
    
    ####################################################
    #
    # step 2: remove triangles with edges longer than threshold
    #
    goodtri = []
    k = 0
    
    for i in range(np.shape(tridx)[0]):
        # get vertex coordinates
        A = X[:,tridx[i,0]]
        B = X[:,tridx[i,1]]
        C = X[:,tridx[i,2]]
        
        # compute edge lengths
        AB = math.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2)
        BC = math.sqrt((B[0]-C[0])**2 + (B[1]-C[1])**2 + (B[2]-C[2])**2)
        AC = math.sqrt((A[0]-C[0])**2 + (A[1]-C[1])**2 + (A[2]-C[2])**2)
        
        if max([AB,BC,AC]) < TRITHRESH:
            k = k+1
            goodtri.append(i)
    
    print('..', end='')
    # shrink goodtri and remove bad trianagles
    goodtri = goodtri[:k]
    tridx = tridx[goodtri,:]
    
    
    # remove unreferenced points not apperaing in any triangles
    ptind = np.unique(np.reshape(tridx, (1,-1)))
    
    # remap indices to the new range
    X = X[:,ptind]
    xR = xR[:,ptind]
    xL = xL[:,ptind]
    
    # remap triangle vertex indices with 2D for loop
    idxmap = dict()
    for i,j in enumerate(ptind):
        idxmap[j] = i
    
    for i in range(np.shape(tridx)[0]):
        for j in range(np.shape(tridx)[1]):
            tridx[i,j] = idxmap[tridx[i,j]]
        
        if (i % 20000) == 0:
            print('..', end='')
    
    print("\nMeshing done.")
    
    
    ###########################################################
    
    # colorize result
    # CAUTION: cv2.imread use BGR color space
    #           MATLAB uses RGB
    print("Computing colors.")
    
    colorCount = np.shape(X)[1]
    xColor = np.zeros((3,colorCount))
    
    for i in range(colorCount):
        rx, ry = xR[:,i]
        lx, ly = xL[:,i]
        xColor[2,i] = 0.5*(R_color[ry,rx,0] + L_color[ly,lx,0]) #B
        xColor[1,i] = 0.5*(R_color[ry,rx,1] + L_color[ly,lx,1]) #G
        xColor[0,i] = 0.5*(R_color[ry,rx,2] + L_color[ly,lx,2]) #R
    
    
    # inverting normal for MeshLab
    print("Inverting surface normals for MeshLab.")
    trimsh = np.zeros(np.shape(tridx))
    
    for i in range(np.shape(tridx)[0]):
        trimsh[i,0] = tridx[i,0]
        trimsh[i,1] = tridx[i,2]
        trimsh[i,2] = tridx[i,1]
        
        
    ############################################################
    # save to MATLAB file for 3D viewing, smoothing, and mesh_2_ply
    print("Done! Use meshprocessing.m with MATLAB to view, process, and convert mesh results")
    scipy.io.savemat('../cache/mesh.mat', mdict={'X':X,"xColor":xColor,"tri":tridx.astype(float),"trimsh":trimsh.astype(float),"NBR_PASS":float(NBR_PASS),"SCANDIR":SCANDIR,"GRAB":GRAB,})
    print("Grab number %d" % GRAB)


    return 0







