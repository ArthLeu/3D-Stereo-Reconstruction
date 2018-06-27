function [] = mesh(GRAB,SCANDIR,UNDISTORTED,THRESH,XRANGE,TRITHRESH,NBR_PASS)
    % mesh.m - compute meshing with triangulated points
    % Input: parameters from demo.m
    % Output: None, directly to .ply files
    % 

    % Unpack bound box limit for part 1
    x_max = XRANGE(1);  %250
    x_min = XRANGE(2);  %-250
    y_max = XRANGE(3); %250
    y_min = XRANGE(4); %-250
    z_max = XRANGE(5); %600
    z_min = XRANGE(6); %0

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % reconstruct surface
    fprintf('Reconstruction started...\n');
    reconstruct(UNDISTORTED, SCANDIR, THRESH);
    load reconstruction.mat
    fprintf("Reconstruction done\n");

    % view reconstructed points
    clf; plot3(X(1,:),X(2,:),X(3,:),'.');
    axis image; axis vis3d; grid on;
    hold on;
    plot3(camL.t(1),camL.t(2),camL.t(3),'go')
    plot3(camR.t(1),camR.t(2),camR.t(3),'go')

    % plot bounding box vertices
    plot3(x_min,y_min,z_min,'r*')
    plot3(x_min,y_min,z_max,'r*')
    plot3(x_min,y_max,z_min,'r*')
    plot3(x_min,y_max,z_max,'r*')
    plot3(x_max,y_min,z_min,'r*')
    plot3(x_max,y_min,z_max,'r*')
    plot3(x_max,y_max,z_min,'r*')
    plot3(x_max,y_max,z_max,'r*')

    axis([x_min-200 200+x_max y_min-200 200+y_max z_min-200 200+z_max])
    set(gca,'projection','perspective')
    xlabel('X-axis');
    ylabel('Y-axis');
    zlabel('Z-axis');

    fprintf(" verify the bounding box vertices\n press 'Enter' to continue..\n")
    pause;   
    fprintf("Bounding box verified, continuing.\n")


    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    % cleaning step 1: remove points outside known bounding box
    %
    fprintf("Meshing started.\n")

    goodind = find((X(1,:)<x_max) & (X(1,:)>x_min) & (X(2,:)<y_max) & (X(2,:)>y_min) & (X(3,:)<z_max) & (X(3,:)>z_min));

    % check if no points found
    assert(size(goodind,2) >= 3, "Error: no points found within range. Consider expanding bounding box.");

    %
    % drop bad points from both 2D and 3D list
    %

    X = X(:,goodind);
    xL = xL(:,goodind);
    xR = xR(:,goodind);

    tri = delaunay(xR(1,:), xR(2,:));

    fprintf('.');

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    % cleaning step 2: remove triangles which have long edges
    %
    goodtri = zeros(1,size(tri,1));
    k = 0;

    for i = 1:size(tri,1)
        % acquire point coordinates
        A = X(:,tri(i,1));
        B = X(:,tri(i,2));
        C = X(:,tri(i,3));

        % compute edge lengths
        AB = sqrt( (A(1)-B(1))^2 + (A(2)-B(2))^2 + (A(3)-B(3))^2 );
        BC = sqrt( (B(1)-C(1))^2 + (B(2)-C(2))^2 + (B(3)-C(3))^2 );
        CA = sqrt( (C(1)-A(1))^2 + (C(2)-A(2))^2 + (C(3)-A(3))^2 );

        if max([AB, BC, CA]) < TRITHRESH
            k = k + 1;
            goodtri(k) = i;
        end
    end
    fprintf('.');
    % shrink goodtri and remove bad triangles
    goodtri = goodtri(1:k);
    tri = tri(goodtri,:); 


    % remove unreferenced points which don't appear in any triangle

    ptind = unique(reshape(tri,1,[])); % retrieve points of triangles

    % remap indices to new range
    X = X(:,ptind); 
    xR = xR(:,ptind);
    xL = xL(:,ptind);

    % remap triangle vertex indices with 2D for loop
    fprintf('.');

    for i = 1:size(tri,1)
        for j = 1:size(tri,2)
            tri(i,j) = find(ptind==tri(i,j));
        end

        if rem(i, 20000) == 0
            fprintf('.');
        end
    end

    fprintf('\nMeshing done.\n');

    fprintf('nbr_smooth\n');
    X = nbr_smooth(tri, X, NBR_PASS);
    fprintf('nbr_smooth done.\n');

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    % display results
    %

    figure(1); clf;
    h = trisurf(tri,X(1,:),X(2,:),X(3,:));
    set(h,'edgecolor','none');
    set(gca,'projection','perspective');
    xlabel('X-axis');
    ylabel('Y-axis');
    zlabel('Z-axis');
    axis image; axis vis3d;


    % rotate the view around so we see from
    % the front  (can also do this with the mouse in the gui)
    camorbit(45,0);
    camorbit(0,-120);
    camroll(-8);

    % prepare output savings
    fprintf('Saving mesh...\n');
    colorCount = size(xR, 2);
    xColor = zeros(3,colorCount);

    for i = 1:colorCount
        xr = xR(1,i);
        yr = xR(2,i);
        xl = xL(1,i);
        yl = xL(2,i);
        xColor(1,i) = 0.5*(R_color(yr,xr,1) + L_color(yl,xl,1));
        xColor(2,i) = 0.5*(R_color(yr,xr,2) + L_color(yl,xl,2));
        xColor(3,i) = 0.5*(R_color(yr,xr,3) + L_color(yl,xl,3));
    end

    % this is to invert the surface normals for MeshLab
    tri_MeshLab = zeros(size(tri));

    for i = 1:size(tri,1)
        tri_MeshLab(i,1) = tri(i,1);
        tri_MeshLab(i,2) = tri(i,3);
        tri_MeshLab(i,3) = tri(i,2);
    end

    % call mesh_2_ply.m
    mesh_2_ply( X,xColor,tri_MeshLab,[SCANDIR sprintf('mesh%d.ply',GRAB)])
    fprintf('Mesh successfully saved. DONE!\n');

end

