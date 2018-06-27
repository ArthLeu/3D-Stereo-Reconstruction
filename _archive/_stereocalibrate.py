# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 17:27:45 2018

@author: Anthony Liu

implementation assisted by 
https://github.com/sourishg/stereo-calibration/blob/master/calib_stereo.cpp

!! C0 is the RIGHT camera, while C1 is the LEFT camera
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



#def createBoardPointPositions():
#    ''' function to generate object points based on square width '''
#    for i in range(chessboardSize[1]):
#        for j in range(chessboardSize[0]):
#            objPts.append([j*calibSquareWidth, i*calibSquareWidth, 0.0])



def calibrate(imageprefixL, imageprefixR, start, stop):
    # arrays to store 3D and 2D coordinates
    imgPointsL = []
    imgPointsR = []
    objPoints = []
    
    for frame in range(start,stop+1):
        # skip the 14th and 16th calib images
        if frame == 14 or frame == 16:
            continue
        
        # read images     
        filenameL = "%s%02d.png" % (imageprefixL, frame)
        imgL = cv2.imread(filenameL, cv2.IMREAD_COLOR)
        print("left: " + filenameL)
        
        filenameR = "%s%02d.png" % (imageprefixR, frame)
        imgR = cv2.imread(filenameR, cv2.IMREAD_COLOR)
        print("right: " + filenameR)
        
        # find chessboard corners
        retL, cornersL = cv2.findChessboardCorners(imgL, chessboardSize, None)
        retR, cornersR = cv2.findChessboardCorners(imgR, chessboardSize, None)
        
        # if points found, then append to image points array
        if retL and retR:
            # improving detection result (must use grayscale src img)
            grayL = cv2.cvtColor(imgL,cv2.COLOR_BGR2GRAY)
            cornersL = cv2.cornerSubPix(grayL, cornersL, (11,11), (-1,-1), criteria)
            grayR = cv2.cvtColor(imgR,cv2.COLOR_BGR2GRAY)
            cornersR = cv2.cornerSubPix(grayR, cornersR, (11,11), (-1,-1), criteria)
            
            # save results
            objPoints.append(objPts)
            imgPointsL.append(cornersL)
            imgPointsR.append(cornersR)
            
            # Draw and display corners
            imgL = cv2.drawChessboardCorners(imgL,chessboardSize, cornersL, retL)
            cv2.imshow('left img',imgL)
            cv2.waitKey(200)
    
    cv2.destroyAllWindows()
    
    # perform intrinsic calibration
    objPoints = np.array(objPoints)
    
    retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera(
            objPoints, imgPointsL, imgL.shape[:-1], None, None)
    
    retR, mtxR, distR, rvecsR, tvecsR = cv2.calibrateCamera(
            objPoints, imgPointsR, imgR.shape[:-1], None, None)
    
    # compute re-projection error
    total_err_L = 0
    for i in range(len(objPoints)):
        imgPointsLP, _ = cv2.projectPoints(objPoints[i], rvecsL[i], tvecsL[i], mtxL, distL)
        error = cv2.norm(imgPointsL[i], imgPointsLP, cv2.NORM_L2)/len(imgPointsLP)
        total_err_L += error
        
    print("total error (left): ", total_err_L/len(objPoints))
    
    total_err_R = 0
    for i in range(len(objPoints)):
        imgPointsRP, _ = cv2.projectPoints(objPoints[i], rvecsR[i], tvecsR[i], mtxR, distR)
        error = cv2.norm(imgPointsR[i], imgPointsRP, cv2.NORM_L2)/len(imgPointsRP)
        total_err_R += error
        
    print("total error (right): ", total_err_R/len(objPoints))
    
    # save variables to files
    with open('C0_CALIB.pkl', 'wb') as c0: # C0 is right camera
        pickle.dump(list([mtxR, rvecsR, tvecsR, distR]), c0)
    
    with open('C1_CALIB.pkl', 'wb') as c1: # C1 is left camera
        pickle.dump(list([mtxL, rvecsL, tvecsL, distL]), c1)
        
    

    
    
    # Now start stereo calibration
    print("start stereo calibration")
    
    ret, MTX1, DIST1, MTX2, DIST2, R, T, E, F = cv2.stereoCalibrate(
            objPoints, imgPointsL, imgPointsR, 
            mtxL, distL, mtxR, distR, np.shape(imgL)[:-1])
    
    SC = (MTX1, DIST1, MTX2, DIST2, R, T, np.shape(imgL)[:-1])
    
    with open('STR_Calib.pkl', 'wb') as sc:
        pickle.dump(list(SC), sc)
        
    print("stereo calibration ended")
    
    return SC


def rectification(calibration_data):
    print("starting rectification")
    MTX1, DIST1, MTX2, DIST2, R, T, img_size = calibration_data
    
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
            MTX1, DIST1, MTX2, DIST2, img_size, R, T)
    
    return (R1, R2, P1, P2, Q, roi1, roi2)

if __name__ == "__main__":
    SC = calibrate("../scans/calib/frame_C1_", "../scans/calib/frame_C0_", 1, 21)
    # tested intrinsic mean error at ~ 0.04469492272459442
    
    SR = rectification(SC)
    
    with open('STR_Rect.pkl', 'wb') as sr:
        pickle.dump(list(SR), sr)
    print("stereo rectification ended")
    
    
#    

