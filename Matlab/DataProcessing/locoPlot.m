clearvars; close all;

subjectFile = 'Loc_control_sub1_path2.txt';
pathsFile = 'Paths_sub1_12mtr.txt';

M = dlmread(pathsFile);
MM = dlmread(subjectFile);

k = strfind(subjectFile,'path');
pathN = str2num(subjectFile(k+4));

%% process weird data format...

% waypoint locations
wx = M(pathN,1:3:end);
wy = M(pathN,2:3:end);
wz = M(pathN,3:3:end);

way_c = wx + 1j*wz; 
way_c(way_c==0) = []; % there's some phantom 0 waypoitns at the end
way_c = [0 way_c]; % add back the origin as the first waypoint

% subject data
x = MM(1,1:3:end);
y = MM(1,2:3:end);
z = MM(1,3:3:end);

sub_c = x + 1j*z;

pit = MM(2,1:3:end);
rol = MM(2,2:3:end);
yaw = MM(2,3:3:end);

pathtime = MM(3,1);

figure(1); clf; hold on;
plot(x,z)
plot(wx,wz,'x')

%% separate the trial into segments

segmentIndices = [];
rW = 0.25;

lastInd = 1;


figure(2); clf; hold on;

whatsLeft = sub_c;
for ii = 1:length(way_c)-1
    segments.wayStart{ii} = way_c(ii);
    segments.wayEnd{ii} = way_c(ii+1);
   
    minIStart = 1;
    [~,minIEnd] = min(abs(whatsLeft-way_c(ii+1)));
    for jj = 1:length(whatsLeft)
        if abs(whatsLeft(jj)-way_c(ii+1))<rW
            minIEnd = jj;
            break;
        end
    end
    
    segments.sub_c{ii} = whatsLeft(minIStart:minIEnd);
    whatsLeft = whatsLeft(minIEnd+1:end);
    
    h = plot(real([way_c(ii) way_c(ii+1)]),imag([way_c(ii) way_c(ii+1)]),'--o');
    plot(segments.sub_c{ii},'color',h.Color)

end
segments.n = length(way_c)-1;

%% find mean deviation from straight line on each segment
figure(3); clf; hold on;
for iS = 1:segments.n
    
    v1 = [real(segments.wayStart{iS}) imag(segments.wayStart{iS}) 0];
    v2 = [real(segments.wayEnd{iS}) imag(segments.wayEnd{iS}) 0];
    
    clear d;
    for ii = 1:length(segments.sub_c{iS})
        pt = [real(segments.sub_c{iS}(ii)) imag(segments.sub_c{iS}(ii)) 0];
        a = v1-v2;
        b = pt-v2;
        dL = norm(cross(a,b)) / norm(a); % distance to this line (not line segment)
        d1 = norm(pt-v1); % distance to start of line segment
        d2 = norm(pt-v2); % distance to end of line segmetn
        
        
        if d1^2 + d2^2 - 2* dL <norm(v1-v2)^2 % geometry condition to check if dL is to a point outside line segment
            d(ii) = dL;
        else
            d(ii) = min([d1 d2]); % minimum distaance to this line segment
        end
        
        
    end
    segments.error{iS} = d;
    segments.meanError{iS} = mean(d);
    
    clf;
    subplot(1,2,1);  hold on;
    h = plot(real([segments.wayStart{iS} segments.wayEnd{iS}]),imag([segments.wayStart{iS} segments.wayEnd{iS}]),'--o');
    plot(segments.sub_c{iS},'color',h.Color)
    axis image;
    
    subplot(1,2,2); hold on;
    plot(segments.error{iS})
    title(['Mean error: ' num2str(segments.meanError{iS}) 'meters']);
    
    pause;
end




























