clear
clc
% Excel file has x values in first column, y values in 2nd, z values in 3rd
% and experimental values in 4th column 
readmatrix('subcrit_room_gamma_doserate.xlsx');
A = readmatrix('subcrit_room_gamma_doserate.xlsx'); % read the file you selected

% assign to seperate variables for clarity

xmin = min(A(:,1));
ymin = min(A(:,2));
zmin = min(A(:,3));
xmax = max(A(:,1));
ymax = max(A(:,2));
zmax = max(A(:,3));
xrange = xmax-xmin +1;
yrange = ymax-ymin +1;
zrange = zmax-zmin +1;

x = zeros(1,xrange);
y = zeros(1,yrange);
z = zeros(1,zrange);

x = A(:,1);
y = A(:,2);
z = A(:,3);

v = zeros(xrange,yrange,zrange);
% build a multidimensional array (again, may not be the most efficient approach)
% https://www.mathworks.com/help/matlab/math/multidimensional-arrays.html
for i=1:length(A)
    x1 = xmax - x(i) +1;
    y1 = y(i);
    z1 = z(i) - zmin +1;
    v(x1,y1,z1) = A(i,4); 
end

% 2D plotting


f = figure;
subplot(1,2,1)
s = surf(v,'FaceAlpha','0.8')  % number value is transparency of plot
% s.EdgeColor = 'none';
s.LineStyle = ":"; % different ways to draw grid lines: none : - -- 
s.FaceColor = 'interp'; % Smooth vs blocky look? interp texturemap
colormap(f,jet); %Color schemes: jet hot hsv parula
colorbar;
set(gca,'color',[0.7 0.7 0.7])
zlim([0.000 999999]); % lower and upper limits for "z" value of data (4th column of excel data)
ylim([0 12]);