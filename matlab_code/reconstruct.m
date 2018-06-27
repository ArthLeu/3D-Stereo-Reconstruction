function [] = reconstruct(undistorted, scandir, thresh)

%
% reconstruct.m
%
% 1. retrieves points from decode.m
% and connect left and right points
% with identical code
%
% 2. send connected xL and xR to
% triangulate.m (provided) to compute
% triangulation.
%
% 3. save 3D points to file
%

    % load calibration data 
    if undistorted
        load ../calibrations/calib_undistorted.mat
    else
        load ../calibrations/calib_distorted.mat
    end

    % begin scan

    [L_h,L_h_good] = decode([scandir 'frame_C1_'],0,19,thresh);
    [L_v,L_v_good] = decode([scandir 'frame_C1_'],20,39,thresh);
    [R_h,R_h_good] = decode([scandir 'frame_C0_'],0,19,thresh);
    [R_v,R_v_good] = decode([scandir 'frame_C0_'],20,39,thresh);

    %
    % visualize the masked out horizontal and vertical
    % codes for left and right camera
    %
    figure(1); clf;
    subplot(2,2,1); imagesc(R_h.*R_h_good); axis image; axis off;title('right camera, h coord');
    subplot(2,2,2); imagesc(R_v.*R_v_good); axis image; axis off;title('right camera,v coord');
    subplot(2,2,3); imagesc(L_h.*L_h_good); axis image; axis off;title('left camera,h coord');  
    subplot(2,2,4); imagesc(L_v.*L_v_good); axis image; axis off;title('left camera,v coord');  
    colormap jet

    %
    % combine horizontal and vertical codes
    % into a single code and a single mask.
    %

    L_h_shifted = bitshift(L_h, 10);
    R_h_shifted = bitshift(R_h, 10);
    L_C = bitor(L_h_shifted, L_v);
    R_C = bitor(R_h_shifted, R_v);

    L_good = and(L_v_good, L_h_good);
    R_good = and(R_v_good, R_h_good);


    % apply background subtraction (procedure 1)
    R_color = im2double(imread([scandir 'color_C0_01.png']));
    R_background = im2double(imread([scandir 'color_C0_00.png']));
    L_color = im2double(imread([scandir 'color_C1_01.png']));
    L_background = im2double(imread([scandir 'color_C1_00.png']));

    R_colormap = abs(R_color-R_background).^2 > thresh;
    L_colormap = abs(L_color-L_background).^2 > thresh;

    R_ok = or(R_colormap(:,:,1), R_colormap(:,:,2));
    R_ok = or(R_colormap(:,:,3), R_ok);
    L_ok = or(L_colormap(:,:,1), L_colormap(:,:,2));
    L_ok = or(L_colormap(:,:,3), L_ok);

    R_good = and(R_ok, R_good);
    L_good = and(L_ok, L_good);

    %
    % now find those pixels which had matching codes
    % and were visible in both the left and right images
    %

    R_sub = find(R_good);   % find the indicies of pixels that were succesfully decoded
    L_sub = find(L_good);

    R_C_good = R_C(R_sub);  % pull out the code values for those good pixels
    L_C_good = L_C(L_sub);

    %intersect the list codes of good pixels in the left and right image to find matches
    [matched,iR,iL] = intersect(R_C_good,L_C_good); 

    R_sub_matched = R_sub(iR);  % get the pixel indicies of the pixels that were matched
    L_sub_matched = L_sub(iL);
    [xx,yy] = meshgrid(1:size(L_good,2),1:size(L_good,1)); % create arrays containing the pixel coordinates
    xR(1,:) = xx(R_sub_matched); % pull out the x,y coordinates of the matched pixels 
    xR(2,:) = yy(R_sub_matched); 
    xL(1,:) = xx(L_sub_matched); 
    xL(2,:) = yy(L_sub_matched);

    %
    % now triangulate the matching pixels using the calibrated cameras
    %
    X = triangulate(xL,xR,camL,camR);

    %
    % save the results of reconstruction
    %
    save('reconstruction.mat','X','xL','xR','camL','camR','L_color','R_color');

end


