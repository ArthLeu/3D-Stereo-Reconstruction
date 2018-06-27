load ../cache/reconstructed.mat

clf; plot3(X(1,:),X(2,:),X(3,:),'.');
axis image; axis vis3d; grid on;
hold on;
axis([0 250 -300 -50 200 500])
set(gca,'projection','perspective')
xlabel('X-axis');
ylabel('Y-axis');
zlabel('Z-axis');