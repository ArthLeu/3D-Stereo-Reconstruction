% meshprocessing.m 
%
% mesh processing script by Anthony Liu
% uses nbr_smooth provided to smooth out surfaces
% then output vertices and tri to .ply file with mesh_2_ply.m
% 
% use nbr_smooth and mesh_2_ply with permission
% CS117 Spring 2018 @ UCI
%

time = fix(clock);
fprintf('System time: %02d:%02d:%02d\n\n', time(4),  time(5),  time(6))

fprintf('Start processing Python mesh result.\nLoad mesh.mat.\n');
load ../cache/mesh.mat
fprintf('Grab number %d\n', GRAB)

tri = tri+1;
trimsh = trimsh+1;

fprintf('Performing NBR Smooth...\n');
X = nbr_smooth(tri, X, NBR_PASS);
fprintf('NBR Smooth done.\n');

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

% call mesh_2_ply.m
mesh_2_ply( X,xColor,trimsh,[SCANDIR sprintf('mesh%d.ply',GRAB)])
fprintf('Mesh (.ply) successfully saved in source scan folder. DONE!\n');
time = fix(clock);
fprintf('System time: %02d:%02d:%02d\n', time(4),  time(5),  time(6))