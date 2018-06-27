# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:25:27 2018

@author: Anthony

demo.py

Run calibrate.py with Python first for calibration data

Note: This meshing is NOT an automated process for every meshes
      since each reconstruction result needs to be manually
      meshed and reviewed for appropriate (best) parameters.
      Doing so in a for loop will not be good for readjusting
      those params. In this case, I have manually saved meshes 
      to files for selected objects, in each grab_n folder.

      *Run meshprocessing.m for generating .ply file for
      MeshLab alignment and Poisson reconstruction*

      For TAs: Please make sure that all grab files are in
               ../scans_undistort/<object>/grab_n/ folder
               and edit the filepaths as needed
               so that this demo will be able to illustrate mesh.py etc.
      See instructions.txt for detailed use
"""       
import mesh as ms
import calibrate as cb

''' Run calibration for other (non-demonstration) purposes ONLY '''
# cb.run_calibrate()


''' Set configurations for each individual modelview
    settings: (followed by default)
    1. grab, decode thresh, scan directory, smooth round
	Remeber to toggle UNDISTORTED to false if using distorted scans
'''

GRAB = 0
SCANDIR = "../scans_undistort/teapot/grab_%d_u/" % GRAB
UNDISTORTED = True
THRESH = 0.015

''' 2. Bound box limit for meshing part 1 '''
x_up_limit = 250  #250
x_low_limit = 0   #-250
y_up_limit = 0    #250
y_low_limit = -270   #-250
z_up_limit = 400     #600
z_low_limit = 200    #0

XRANGE = [x_up_limit, x_low_limit, y_up_limit, y_low_limit, z_up_limit, z_low_limit]

''' 3. Triangle max edge limit for part 2 '''
TRITHRESH = 15 #10
''' 4. NBR smoothing round (in MATLAB) '''
NBR_PASS = 3


''' Run meshing function '''

ms.mesh(GRAB,SCANDIR,UNDISTORTED,THRESH,XRANGE,TRITHRESH,NBR_PASS)


