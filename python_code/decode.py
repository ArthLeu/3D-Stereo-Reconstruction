# -*- coding: utf-8 -*-
"""
Created on Sun Jun 03 02:13:45 2018

@author: Anthony Liu
"""

import cv2
import numpy as np

print(cv2.__version__)


def im2double(im):
    '''https://stackoverflow.com/questions/29100722/equivalent-im2double-function-in-opencv-python'''
    info = np.iinfo(im.dtype) # Get the data type of the input image
    return im.astype(np.float) / info.max # Divide all values by the largest possible value in the datatype


def decode(imageprefix, start, stop, threshold):
    if stop <= start:
        raise(ValueError,"stop frame number less than start number")
    
    # compute graycode array
    (G, goodpixels, H, W, bit) = _readGrayCodeBits(imageprefix, 
        start, stop, threshold)
    
    # convert gray to binary coded decimals
    BCD = [G[0]]
    
    for i in range(1,bit):
        BCD.append( np.bitwise_xor(BCD[i-1], G[i]) )
    
    # convert from BCD to standard decimals
    C = np.zeros((H, W))
    
    for p in range(1,bit+1):
        C = C + BCD[p-1]*(pow(2,(10-p)))
    
    return (C, goodpixels)


    
def _readGrayCodeBits(imageprefix, start, stop, threshold):
    bit = 0
    H = 0
    W = 0
    goodpixels = [];
    G = [] # returning graycode bits in 3D matrix
    
    for i in range(start, stop, 2):
        # read images
        I1_name = "%s%02d.png" % (imageprefix, i)
        I2_name = "%s%02d.png" % (imageprefix, (i+1))
        
        try:
            I1 = im2double( cv2.imread(I1_name, cv2.IMREAD_GRAYSCALE) )
            I2 = im2double( cv2.imread(I2_name, cv2.IMREAD_GRAYSCALE) )
        except:
            import sys
            print("Cannot open file: %s" % I1_name)
            sys.exit(0)
        
        # set bitmap array sizes (H, W), goodpixels
        if i == start:
            print(I1_name)
            H = np.shape(I1)[0]
            W = np.shape(I1)[1]
            goodpixels = np.ones((H,W))
        
        # G as the graycode returning array
        G.append( I1 > I2 )
        goodpixels = np.logical_and(goodpixels, cv2.absdiff(I1,I2) > threshold)
        
        # increment bit counter
        bit += 1
        
    return (G, goodpixels, H, W, bit)




if __name__ == "__main__":
    print("This is a testing function")
    thresh = 0.00001
    decode('../scans/gray/',0,19,thresh)
    decode('../scans/gray/',20,39,thresh)