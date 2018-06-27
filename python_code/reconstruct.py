# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 04:51:31 2018

@author: Anthony Liu

reconstruct.py

using intersect_mtlb() function to replace intersect in matlab
adapted from https://stackoverflow.com/questions/45637778/
                how-to-find-intersect-indexes-and-values-in-python
                
-- numpy.isin() requires numpy version 1.13

thank you!

"""
import cv2
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle


import decode as dc
import triangulate as tr


def reconstruct(scandir='../scans_undistort/manny/grab_0_u/', thresh = 0.015):
    
    def _intersect_matlab(a, b):
        a1, ia = np.unique(a, return_index=True)
        b1, ib = np.unique(b, return_index=True)
        aux = np.concatenate((a1, b1))
        aux.sort()
        c = aux[:-1][aux[1:] == aux[:-1]]
        return c, ia[np.isin(a1, c)], ib[np.isin(b1, c)]
    
    
    def _find_index_good(goodpixels):
        assert(np.shape(goodpixels) == (H,W))
        # return a 1D index array of goodpixels
        ret = [[],[]]
        
        for i in range(H):
            for j in range(W):
                if goodpixels[i][j]:
                    ret[0].append(j)
                    ret[1].append(i)
                    
        return np.array(ret)
    
    # read calibration data saved from last calibration run
    with open("../cache/C0_CALIB.pkl", "rb") as c0: # right
        R_mat, R_rvec, R_tvec, R_dist = pickle.load(c0)
        
    with open("../cache/C1_CALIB.pkl", "rb") as c1: # left
        L_mat, L_rvec, L_tvec, L_dist = pickle.load(c1)  
    
    # set calibration data selection index
    SELECT = 2    
    
    ######################################################
    # start reconstruction
    R_h,R_h_good = dc.decode(scandir+'frame_C0_', 0, 19, thresh)
    R_v,R_v_good = dc.decode(scandir+'frame_C0_', 20, 39, thresh)
    L_h,L_h_good = dc.decode(scandir+'frame_C1_', 0, 19, thresh)
    L_v,L_v_good = dc.decode(scandir+'frame_C1_', 20, 39, thresh)
    
    
    # save image size info
    assert(np.shape(R_h) == np.shape(L_v))
    H, W = np.shape(R_h)
    

    # combine horizontal and vertical by bit shift + and operation
    L_h_shifted = np.left_shift(L_h.astype(int), 10)
    R_h_shifted = np.left_shift(R_h.astype(int), 10)
    L_C = np.bitwise_or(L_h_shifted, L_v.astype(int))
    R_C = np.bitwise_or(R_h_shifted, R_v.astype(int))
    
    
    L_good = np.logical_and(L_v_good, L_h_good)
    R_good = np.logical_and(R_v_good, R_h_good)
    
    # now perform background substraction
    R_color = dc.im2double( cv2.imread(scandir+'color_C0_01.png', cv2.IMREAD_COLOR) )
    R_background = dc.im2double( cv2.imread(scandir+'color_C0_00.png', cv2.IMREAD_COLOR) )
    L_color = dc.im2double( cv2.imread(scandir+'color_C1_01.png', cv2.IMREAD_COLOR) )
    L_background = dc.im2double( cv2.imread(scandir+'color_C1_00.png', cv2.IMREAD_COLOR) )
    
    R_colormap = abs(R_color-R_background)**2 > thresh
    L_colormap = abs(L_color-L_background)**2 > thresh
    
    
    R_ok = np.logical_or(R_colormap[:,:,0], R_colormap[:,:,1])
    R_ok = np.logical_or(R_colormap[:,:,2], R_ok)
    L_ok = np.logical_or(L_colormap[:,:,0], L_colormap[:,:,1])
    L_ok = np.logical_or(L_colormap[:,:,2], L_ok)
    
    R_good = np.logical_and(R_ok, R_good)
    L_good = np.logical_and(L_ok, L_good)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15,20))
    ax1.imshow(L_C*L_good, cmap = 'jet')
    ax1.set_title('Left')
    ax2.imshow(R_C*R_good, cmap = 'jet')
    ax2.set_title('Right')
    plt.show()
    
    
    # find coordinates of pixels that were successfully decoded
    # R_coord, L_coord in 1D indices
    R_coord = _find_index_good(R_good)
    L_coord = _find_index_good(L_good)
    
    # pull out CODE values at successful pixels
    # (notice this is a little bit different from MATLAB)
    R_C_good = R_C[R_good]
    L_C_good = L_C[L_good]
    
    # perform intersection
    matched, iR, iL = _intersect_matlab(R_C_good, L_C_good)
    
    # get pixel coordinates of pixels matched
    # change R_coord, L_coord to 2D first
    xR = R_coord[:,iR]
    xL = L_coord[:,iL]
    
    
    # Now, triangulate the matched pixels using the first calibration result
    camL = (L_mat, L_rvec[SELECT], L_tvec[SELECT])
    camR = (R_mat, R_rvec[SELECT], R_tvec[SELECT])
    
    X = tr.triangulate(xL, xR, camL, camR)
    
    # Display triangulation result
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(X[0,:], X[1,:], X[2,:])
    ax.view_init(45,0)
    
    ax.set_xlabel('x axis')
    ax.set_ylabel('y axis')
    ax.set_zlabel('z axis')
    
    plt.show()
    
    # save to MATLAB file for easier 3D viewing
    import scipy.io
    scipy.io.savemat('../cache/reconstructed.mat', mdict={'X':X})
    
    # return reconstruction result for meshing
    return [X, xL, xR, L_color, R_color]
                    

if __name__ == "__main__":
    scandir = input("scan directory? ")
    threshold = input("threshold? ")
    print("Running reconstruct.py separately..")
    if not scandir or not threshold: raise ValueError("No blank input allowed")
    reconstruct(scandir,float(threshold))

    