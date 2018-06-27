
function [C,goodpixels] = decode(imageprefix,start,stop,threshold)

% function [C,goodpixels] = decode(imageprefix,start,stop,threshold)
%
%
% Input:
%
% imageprefix : a string which is the prefix common to all the images.
%
%                  for example, pass in the prefix '/home/fowlkes/left/left_'  
%
%                  to load the image sequence   '/home/fowlkes/left/left_01.png' 
%                                               '/home/fowlkes/left/left_02.png'
%                                               '/home/fowlkes/left/left_03.png'
%                                                          etc.
%
%  start : the first image # to load
%  stop  : the last image # to load
% 
%  threshold : the pixel brightness should vary more than this threshold between the positive
%             and negative images.  if the absolute difference doesn't exceed this value, the 
%             pixel is marked as undecodeable.
%
% Output:
%
%  C : an array containing the decoded values (0..1023)  for 10bit values
%
%  goodpixels : a binary image in which pixels that were decodedable across all images are marked with a 1.

% some error checking
if (stop<=start)
  error('stop frame number should be greater than start frame number');
end
   
bit = 1;
H = 0; W = 0;

for i = start:2:stop
  % read two images
  img1_name = [imageprefix sprintf('%02d.png',i)]; 
  img2_name = [imageprefix sprintf('%02d.png',i+1)]; 
  
  try
    img1 = imread(img1_name);
    img2 = imread(img2_name);
  catch
    warning('Image not found! Is the file path correct?');
  end
  
  if size(img1, 3) == 3
      img1 = rgb2gray(img1);
      img2 = rgb2gray(img2);
  end
  
  img1 = im2double(img1);
  img2 = im2double(img2);
  
  % set height, width, and goodpixels
  if i == start
    H = size(img1,1);
    W = size(img1,2);
    goodpixels = ones(H,W);
  end
  
  % G is the graycode (not binary) array
  G(:,:,bit) = (img1 - img2) > 0; %store the bits of the gray code
  goodpixels = goodpixels & (abs(img1-img2) > threshold);

  % visualize as we walk through the images
  figure(1); clf;
  subplot(1,2,1); imagesc(G(:,:,bit)); axis image; title(sprintf('bit %d',bit));
  subplot(1,2,2); imagesc(goodpixels); axis image; title('goodpixels');
  drawnow;

  bit = bit + 1;
end

% convert from gray to bcd
%   remember that MSB is bit #1
BCD = zeros(H,W,10);
BCD(:,:,1) = G(:,:,1);

for bit = 2:10
    BCD(:,:,bit) = xor(BCD(:,:,bit-1), G(:,:,bit));
end

% convert from BCD to standard decimal
C = zeros(H,W);

for pow = 1:10
    C(:,:) = C(:,:) + BCD(:,:,pow)*(2^(10-pow));
end

% visualize final result
figure(1); clf;
subplot(1,2,1); imagesc(C.*goodpixels); axis image; title('decoded');
subplot(1,2,2); imagesc(goodpixels); axis image; title('goodpixels');
drawnow;

