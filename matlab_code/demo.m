% demo.m
% Run calibrate.py with Python first for calibration data
%
% Note: This meshing is NOT an automated process for every meshes
%       since each reconstruction result needs to be manually
%       meshed and reviewed for appropriate (best) parameters.
%       Doing so in a for loop will not be good for readjusting
%       those params. In this case, I have manually saved meshes 
%       to files for selected objects, in each grab_n folder.
%
%       At the end, mesh_2_ply.m will be called for 3D mesh saving.
%
%       For TAs: Please make sure that all grab files are in
%                ../scans_undistort/<object>/grab_n/ folder
%                and edit the filepaths as needed
%                so that this demo will be able to illustrate mesh.m etc.
%       See instructions.txt for detail use
%               

clear


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set configurations for each individual modelview
% settings: (followed by default)
% 1. grab, decode thresh, scan directory, smooth passes
GRAB = 0;                  %% CHANGE THIS BEFORE MESHING EACH GRAB
SCANDIR = sprintf('../scans_undistort/teapot/grab_%d_u/',GRAB);
UNDISTORTED = true;          % if use images with distortion flip this value
THRESH = 0.020; 

% 2. setting bounding box - x_max, x_min, y_max, y_min, z_max, z_min
x_max = 300;
x_min = 0;
y_max = 0;
y_min = -300;
z_max = 500;
z_min = 200;

XRANGE = [x_max x_min y_max y_min z_max z_min];

% 3. Triangle edge threshold for part 2
TRITHRESH = 12; %10
% 4. nbr_smooth round
NBR_PASS = 3;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

mesh(GRAB,SCANDIR,UNDISTORTED,THRESH,XRANGE,TRITHRESH,NBR_PASS);

fprintf("Demo done\n")
