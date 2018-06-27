function [] = mesh_2_ply( X,xColor,tri,filePath)
%
% Code from Omar Santiago (CS117, spring class of 2015)
%
%converts mesh file to ply files using paramaters saved during
%reconstruction
%
%   X is 3 x N matrix containing containing x,y and z cordinates
%   xColor is the entensity of the pixels
%   tri triangulation of the mesh
%   filepath of the file to be writen and name
%
%
    if nargin<4
        error('Function takes 4 arguments');
    end
    if(size(X,1) ~= 3)
        error('X must be a 3 by N matrix')
    end
    if(size(tri,2) ~= 3)
        error('triangualtion must contain 3 vertices');
    end
    fid = fopen(filePath,'w');
    fprintf(fid,'ply\n');
    fprintf(fid,'format ascii 1.0\n');
    fprintf(fid,'element vertex %i\n',size(X,2));
    fprintf(fid,'property float x\n');
    fprintf(fid,'property float y\n');
    fprintf(fid,'property float z\n');
    fprintf(fid,'property uchar red\n');
    fprintf(fid,'property uchar green\n');
    fprintf(fid,'property uchar blue\n');
    fprintf(fid,'element face %d\n',size(tri,1));
    fprintf(fid,'property list uchar int vertex_indices\n');
    fprintf(fid,'end_header\n');
    
    %Loop to write data points to file
    for j = 1:size(X,2)
        fprintf(fid,'%f ',X(1,j));
        fprintf(fid,'%f ',X(2,j));
        fprintf(fid,'%f ',X(3,j));
        fprintf(fid,'%u ',uint8((xColor(1,j)*255)));
        fprintf(fid,'%u ',uint8((xColor(2,j)*255)));
        fprintf(fid,'%u ',uint8((xColor(3,j)*255)));
        fprintf(fid,'\n');
    end
    for j = 1:size(tri,1)
        fprintf(fid,'%d ',3);
        fprintf(fid,'%d ',tri(j,1)-1);
        fprintf(fid,'%d ',tri(j,2)-1);
        fprintf(fid,'%d ',tri(j,3)-1);
        fprintf(fid,'\n');
    end
    fclose(fid);
    
end