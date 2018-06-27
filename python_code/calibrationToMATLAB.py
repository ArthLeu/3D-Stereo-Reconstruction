# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 05:15:48 2018

@author: Anthony

This script is only to assist transferring from Python calibration
to MATLAB meshing etc.

Run calibrate.py first
"""
import pickle
import scipy.io
import cv2

with open("../cache/C0_CALIB.pkl", "rb") as c0: #right cam
    mtxR, rvecR, tvecR, distR = pickle.load(c0)
    
with open("../cache/C1_CALIB.pkl", "rb") as c1: #left cam
    mtxL, rvecL, tvecL, distL = pickle.load(c1)
    
SCAN_NUM = 0

def rotationVecToMat(rvec):
    # this selects the first rotation vector by default
    # and output the first variable from cv2.Rodrigues()
    return cv2.Rodrigues(rvec[SCAN_NUM])[0]

def translationVecToT(r, tvec):
    # return cam.t according to https://piazza.com/class/jfk6khu5u8m5b9?cid=269
    return (-r).dot(tvec)
    
def camMatUnpack(mtx):
    fx, fy, cx, cy = mtx[0,0], mtx[1,1], mtx[0,2], mtx[1,2]
    return ((fx+fy)/2,[cx,cy])

fR, cR = camMatUnpack(mtxR)
fL, cL = camMatUnpack(mtxL)
rR = rotationVecToMat(rvecR)
rL = rotationVecToMat(rvecL)
tR = translationVecToT(rR, tvecR[SCAN_NUM])
tL = translationVecToT(rL, tvecL[SCAN_NUM])

camR = {"f":fR,'c':cR,'R':rR,'t':tR}
camL = {"f":fL,'c':cL,'R':rL,'t':tL}


undistorted = input("Are you calibrating with undistorted image sets? (Y/N): ")
FILEPATH = ""

if undistorted == "Y":
    FILEPATH = "../calibrations/calib_undistorted.mat"
elif undistorted == "N":
    FILEPATH = "../calibrations/calib_distorted.mat"
else:
    exit(0)
    
scipy.io.savemat(FILEPATH, mdict={"camL":camL, "camR":camR,})
print("\nCalibration data successfully saved as '{}'".format(FILEPATH))
   
