# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 03:48:48 2018

@author: Anthony Liu

"""

import cv2
import numpy as np


def triangulate(xL, xR, camL, camR):
    print("Triangulating points..\n")
    
    assert(len(xL) == 2 and len(xR) == 2)
    assert(len(xL[0]) == len(xR[0]))
    
    # set pts count and load calibration result
    npts = len(xL[0])
    Lmat, Lrv, lL = camL[:]
    Rmat, Rrv, rL = camR[:]
    
    # convert rvec to rotation matrix
    Lrot = cv2.Rodrigues(Lrv)[0]
    Rrot = cv2.Rodrigues(Rrv)[0]
	
    # convert translation vector to our format
    Rtrl = (-Rrot).dot(rL)
    Ltrl = (-Lrot).dot(lL)
    
    
    qL = np.ones((3,npts), np.float32)
    qL[0,:] = (xL[0,:] - Lmat[0,2]) / Lmat[0,0] # camL.cx and camL.fx
    qL[1,:] = (xL[1,:] - Lmat[1,2]) / Lmat[1,1] # camL.cy and camL.fy
    
    qR = np.ones((3,npts), np.float32)
    qR[0,:] = (xR[0,:] - Rmat[0,2]) / Rmat[0,0] # camR.cx and camR.fx
    qR[1,:] = (xR[1,:] - Rmat[1,2]) / Rmat[1,1] # camR.cy and camR.fy
    
    # compute rotation and translation of right camera
    # making left camera as the origin of coord system
    Rt = np.matmul(np.linalg.inv(Lrot), Rrot)
    tl = np.matmul(np.linalg.inv(Lrot), (Rtrl - Ltrl))
    
    # solve LSQ
    XL = np.zeros((3, npts))
    XR = np.zeros((3, npts))
    
    for i in range(0, npts):
        front = np.array([qL[:,i]]).transpose()
        qR_transposed = np.array([qR[:,i]]).transpose()
        A = np.hstack((front, np.matmul(-Rt, qR_transposed) ))
        Z = np.linalg.lstsq(A,tl, rcond=None)[0]
        
        XL[:,i] = qL[:,i]*Z[0]
        XR[:,i] = qR[:,i]*Z[1]
        
    # finally, map both back to world coordinates
    Xa = np.zeros((3, npts))
    Xb = np.zeros((3, npts))
    
    Xa = Lrot.dot(XL) + Ltrl
    Xb = Rrot.dot(XR) + Rtrl
      
    # return the midpoint of left and right estimates
    X = 0.5*(Xa+Xb)
    
    return X
    
    