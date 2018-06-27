# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 17:27:45 2018

@author: Anthony Liu

implementation assisted by 
http://opencv-python-tutroals.readthedocs.io/
en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html

This Python program is to compute calibration data for stereo cameras 
C0 (right) and C1 (left). It is also available in MATLAB from previous
assignments.
"""

import cv2
import numpy as np
import pickle
#from matplotlib import pyplot as plt

# lengths in mm
calibSquareWidth = 27.75
chessboardSize= (8,6)

# generate object points
objPts = np.zeros((8*6, 3), np.float32)
objPts[:,:2] = np.mgrid[0:8, 0:6].T.reshape(-1,2)
objPts[:,1] = objPts[:,1] * -1;
objPts = objPts*calibSquareWidth

# corner refinement termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.0001)


def calibrate(imageprefix, suffix, start, stop):
    # arrays to store 3D and 2D coordinates
    imgPoints = []
    objPoints = []
    
    for frame in range(start,stop+1):
        # skip the (14th undistorted) and 16th calib images
        if frame == 14 or frame == 16:
            continue
        
        # read images     
        filename = "%s%02d%s" % (imageprefix, frame, suffix)
        try:
            img = cv2.imread(filename, cv2.IMREAD_COLOR)
        except:
            print("Cannot open file! Check calibration file path and name.")
    			
        print(filename)
        
        
        # find chessboard corners
        ret, corners = cv2.findChessboardCorners(img, chessboardSize, None)
        
        # if points found, then append to image points array
        if ret == True:
            # improving detection result (must use grayscale src img)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            
            # save results
            objPoints.append(objPts)
            imgPoints.append(corners)
            
            # Draw and display corners
            img = cv2.drawChessboardCorners(img,chessboardSize, corners, ret)
            cv2.imshow('img',img)
            cv2.waitKey(200)
    
    cv2.destroyAllWindows()
    
    # perform calibration
    objPoints = np.array(objPoints)
    
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objPoints, imgPoints, img.shape[:-1], None, None)
    
    # compute re-projection error
    total_err = 0
    
    for i in range(len(objPoints)):
        imgPoints2, _ = cv2.projectPoints(objPoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgPoints[i], imgPoints2, cv2.NORM_L2)/len(imgPoints2)
        total_err += error


    print("averaged error: ", total_err/len(objPoints))

    return (mtx, rvecs, tvecs, dist)

	
def run_calibrate():
    undistorted = input("Are you calibrating with undistorted image sets? (Y/N): ")
    c0_prefix, c1_prefix, suffix = "", "", ""

    if undistorted == "N":
        c0_prefix = "../scans/calib/frame_C0_"
        c1_prefix = "../scans/calib/frame_C1_"
        suffix = ".png"
    elif undistorted == "Y":
        c0_prefix = "../scans_undistort/calib_jpg_u/frame_C0_"
        c1_prefix = "../scans_undistort/calib_jpg_u/frame_C1_"
        suffix = ".jpg"
    else:
        exit(0)

    
    C0_calib = calibrate(c0_prefix, suffix, 1, 21)
    # tested mean error at 0.04469492272459442
    
    C1_calib = calibrate(c1_prefix, suffix, 1, 21)
    # tested mean error at 0.04525924361345942
    
    # save variables to files
    print("Saving calibration data in .pkl files under cache folder")
	
    with open('../cache/C0_CALIB.pkl', 'wb') as c0:
        pickle.dump(list(C0_calib), c0)
        
    with open('../cache/C1_CALIB.pkl', 'wb') as c1:
        pickle.dump(list(C1_calib), c1)
		
    return 0


if __name__ == "__main__":
	run_calibrate()
