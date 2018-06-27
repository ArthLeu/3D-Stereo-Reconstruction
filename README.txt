####################################
Instruction on how to use this 3D reconstruction pipeline
Revised 06/14/2018
by Anthony Liu
University of California, Irvine

-----------
Caution: If you want the best reconstruction result: DO AS MANY AS POSSIBLE SCANS!
	MR. TEAPOT HAS WARNED YOU!!!
-----------

############################################################
Directory Information
- cache/: Python cache files for calibrations and file exchange with MATLAB
	|-- *.pkl: intermediate cache files consisted of calibration data
	|-- mesh.mat: intermediate cache files transferring data to meshprocessing.m
	|-- reconstructed.mat: intermediate cache files transferring data to reconstruct_view.m
	|
- calibrations/: calibration data for both undistorted and distorted image sets
	|-- *.mat: calibration data files for MATLAB pipeline
	|
- matlab_code/: mesh functions running solely using MATLAB and MeshLab (no calibration)
	|-- *: NONE
	|
- python_code/: calibration AND mesh program incorporated Python for faster running time
	|-- calibrate.py: run alone or call function for calibration script
	|-- calibrationToMATLAB: generate .mat file with calibration data
	|-- decode.py: decode gray code images
	|-- demo.py: run mesh.m with parameters set in demo
	|-- mesh.py: run mesh cleaning algorithms and map color
	|-- reconstruct.py: reconstruct 3D point cloud with 2D image points
	|-- triangulate.py: compute triangulation from 2D image points to 3D points
	|-- mesh_2_ply.m: convert mesh result to .ply file for MeshLab
	|-- meshprocessing.m: carry mesh from mesh.py, run nbr_smooth, and run mesh_2_ply
	|-- nbr_smooth.m: compute neighbor smoothing algorithm
	|-- reconstructed_view.m: view Python reconstruct.py result
	|
- scans/: scans with distortion not corrected
	|-- calib/: calibration images with distortion
- scans_undistort/: scans with distortion corrected
	|-- calib_jpg_u/: calibration images without distortion
	|-- couple/: individual scan grabs in grab_n_u/*.png (removed to save space), meshes of each grab grab_n_u/mesh<n>.ply, 
		final mesh couple_final.ply, and MeshLab project file mesh.mlp
	|-- teapot/: individual scan grabs grab_n_u/*.png (removed to save space), meshes of each grab grab_n_u/mesh<n>.ply,
		final mesh teapot_final.ply, and MeshLab project file teapot.mlp

########################################################
#
# FOR TAs or Readers,
#
# I removed all scans for uploading purposes,
# you need to restore them in the right directory before running the script
# meshes generated from my program were retained (but >50mb saved to cloud)
# so that you can use directly with MeshLab without spending time with
# mesh.py and meshprocessing.m
# 
# .mlp is project file
# .ply are meshes (either aligned or individual)
#
############################################################

INSTRUCTION MANUAL


0. Place scans in scans_undistort/<object>/grab_n_u/ or scans/<object>/grab_n/
1. Open Anaconda->Spyder or other Python scientific IDE
	make sure you have NumPy, Scipy, Matplotlib, OpenCV Python, and pickle libraries installed
2. Open file python_code/calibrate.py
3. Run calibrate.py and type 'Y' for undistorted scans or 'N' for distorted
4. Choose environment you want to run the program in: 
	MATLAB for better data visualization: go to ../matlab_code/ folder
	Python for faster running time (10x faster est.)

-------------------------
For Python users aiming for runtime efficiency:
5. Open mesh.py with scientific IDE
5a. in the first section you will see parameters, if you do not know what to set
	set the scan directory (SCANDIR) first and run to see the effect.
	To know what the bounding box should be, run reconstruct.py alone
	If you want to check the triangulation result with more versatility, run
	reconstructed_view.m in MATLAB session under the same folder

5b. you would visually see if the whole object scanned is included in the meshing result once run
6. After adjusting the parameters, run mesh.py thoroughly.
7. You will be notified once mesh is done, this should take only around 15 seconds.
8. Meshing result will be saved under ../cache/mesh.mat for smoothing and outputting in MATLAB,
	you will not need to move this .mat file to anywhere else
9. Open MATLAB once you are done running mesh.py, open meshprocessing.m
10. Run the script. The parameter for NBR is automatically passed from Python to MATLAB.
11. Continue to step 12.

-------------------------------
For MATLAB users for better viewing experience:
5. Go to ../matlab_code/ folder and open mesh.m file with MATLAB
5a. Adjust the parameters as needed, if unsure, run once and you will be able to see how
	well they perform
6. Run the script. After reconstruction, a window will pop up showing the bounding box vertices.
	Make change to the boudning box parameters if the object is not in the box. After
	checking with the bounding box, press 'Enter' to continue
7. Once the process is done, about 45 seconds every run, your mesh is saved. Go to step 12.
--------------------------------

...
12. Your mesh generated by the programs will be stored exactly where your original scans are
	### IN EACH GRAB FOLDER, NOT OBJECT FOLDER ###
13. Install and open MeshLab, drag the individual mesh you generated for each face to the program
14. Click on Edit->Align or the round A button.
15. Choose one base layer, set it as base layer, and glue it
16. Select other layers and click on "Point Align"
16a. choose 4 or more corresponding points between both meshes, uncheck "false color" if you need to
	view the color texture for better selecting. After selecting, click on 'OK'
16b. If you are unsatisfied with the "Point align" function, that's very normal. Buggy software, let's
	improve this by using the "Manual rough align" function.
17. Once you align all the meshes, click on 'Process' and you mesh alignment will be improved further.
18. Close the align window once processed. Now there are holes and missing faces on our model, so
	we will have to reconstruct the surface using "Screen Poisson Surface Reconstruction" tool
19. Go to 'Filters'->'Remeshing...'->'Screen Poisson Reconstruction'. Select the options at wish,
	there will be no universal best configurations so try with multiple times. Click on 'Apply'
19a. In some circumstances, MeshLab shows error "Filter requires per-vertex normals", try 
	Filter->Cleaning...->Remove Isolated Pieces to solve this.
20. Our 3D model has been reconstructed! Enjoy it at your time. The final result depends on many factors
	such as scanner distortion, alignment accuracy, noise removal etc.


In the end, thank you for reading this and using my 3D reconstruction toolset.


