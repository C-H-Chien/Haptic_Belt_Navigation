%%
% This program is used to analyze locomotion experiments in VR with the
% haptic belt.

% Currently only works for one subject's data
% Currently assumes continuous presentations
% Currently assumes 12 motor belt.

clearvars; close all;

plotTrials = false;
plotSegments = false;

trimReorientation = true;

%% find all subject data folders
% dataSuperFolder = 'DataFiles_haptic';
dataSuperFolder = 'DataFiles_opticFlow';
subjectFolders = dir(dataSuperFolder);
subjectFolders = subjectFolders(3:end); % get rid of '.' and '..' folders
nSub = length(subjectFolders);

subList = 1:nSub;
% subList = 2;

for iSub = subList
    %% find our files
    % dataFolder = 'DataFiles/Viktor032621/'; % 16 8 12
    %     dataFolder = 'DataFiles/Helen050421/'; % 12 16 8
    dataFolder = [dataSuperFolder '/' subjectFolders(iSub).name '/'];
    
    dataFiles = dir(dataFolder);
    dataFiles = dataFiles(3:end); % get rid of '.' and '..' folders
    
    for iTrial = 1:length(dataFiles)
       
        subjectFile = [dataFolder dataFiles(iTrial).name];
        
        if contains(subjectFile,'warmup') || contains(subjectFile,'Paths_')
            break; % don't look at warmup files
        end
        
        % find trial conditions from file name
        if contains(subjectFile,'control')
            condition = 'control';
        elseif contains(subjectFile,'gaussian')
            condition = 'gaussian';
        elseif contains(subjectFile,'single')
            condition = 'single';
        else
            error('whatisthis')
        end
        k = strfind(subjectFile,'sub');
        subjectNumber = subjectFile(k+3:k+4); % need to find the subject file number since that isn't actually how this program works and subject number doesn't matter
        
        if contains(subjectFile,'8mtr')
            belt = 8;
            pathsFile = [dataFolder 'Paths_sub' subjectNumber '_8mtr.txt'];
        elseif contains(subjectFile,'12mtr')
            belt = 12;
            pathsFile = [dataFolder 'Paths_sub' subjectNumber '_12mtr.txt'];
        elseif contains(subjectFile,'16mtr')
            belt = 16;
            pathsFile = [dataFolder 'Paths_sub' subjectNumber '_16mtr.txt'];
        end
        
        
        % read data from text file
        M = dlmread(pathsFile);
        MM = dlmread(subjectFile);
        
        
        expData(iSub,iTrial).condition = condition;
        expData(iSub,iTrial).belt = belt;
        
        % find path number from file name
        k = strfind(subjectFile,'path');
        kEnd = strfind(subjectFile,'.txt');
        pathN = str2num(subjectFile(k+4:kEnd));
        expData(iSub,iTrial).pathNumber = pathN;
        
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
        
        pathTime = MM(3,1);
        
        expData(iSub,iTrial).pathTime = pathTime;
        expData(iSub,iTrial).pathLength = sum(abs(diff(sub_c)));
        
        %     figure(1); clf; hold on;
        %     plot(x,z)
        %     plot(wx,wz,'x')
        %
        %% separate the trial into segments
        
        segmentIndices = [];
        rW = 0.30;%0.25;
        
        lastInd = 1;
        
        if plotTrials
            figure(2); clf; hold on;
        end
        
        whatsLeft = sub_c;
        for ii = 1:length(way_c)-1
            expData(iSub,iTrial).segments.wayStart{ii} = way_c(ii);
            expData(iSub,iTrial).segments.wayEnd{ii} = way_c(ii+1);
            
            minIStart = 1;
            [~,minIEnd] = min(abs(whatsLeft-way_c(ii+1)));
            for jj = 1:length(whatsLeft)
                if abs(whatsLeft(jj)-way_c(ii+1))<rW
                    minIEnd = jj;
                    break;
                end
            end
            
            expData(iSub,iTrial).segments.sub_c{ii} = whatsLeft(minIStart:minIEnd);
            if trimReorientation
                dFromStart = abs(expData(iSub,iTrial).segments.sub_c{ii}- expData(iSub,iTrial).segments.wayStart{ii});
                [~,minInd] = min(abs(dFromStart-1)); % find index when person is x meters from the start
                expData(iSub,iTrial).segments.sub_c{ii} = expData(iSub,iTrial).segments.sub_c{ii}(minInd:end);
            end
            whatsLeft = whatsLeft(minIEnd+1:end);
            
            if plotTrials
                h = plot(real([way_c(ii) way_c(ii+1)]),imag([way_c(ii) way_c(ii+1)]),'--o');
                plot(expData(iSub,iTrial).segments.sub_c{ii},'color',h.Color)
                titleStr = {[num2str(belt) ' ' condition]; ...
                    ['Path length ' num2str(expData(iSub,iTrial).pathLength)];...
                    ['Path time ' num2str(expData(iSub,iTrial).pathTime)]};
                title(titleStr)
            end
            
        end
        if plotTrials
            pause;
        end
        expData(iSub,iTrial).segments.nSeg = length(way_c)-1;
        
        %% find mean deviation from straight line on each segment
        if plotSegments
            figure(3); clf; hold on;
        end
        for iS = 1:expData(iSub,iTrial).segments.nSeg
            
            v1 = [real(expData(iSub,iTrial).segments.wayStart{iS}) imag(expData(iSub,iTrial).segments.wayStart{iS}) 0];
            v2 = [real(expData(iSub,iTrial).segments.wayEnd{iS}) imag(expData(iSub,iTrial).segments.wayEnd{iS}) 0];
            
            clear d headingError heading;
            for ii = 1:length(expData(iSub,iTrial).segments.sub_c{iS})
                % calculate position error from straightline path to waypoint from start
                pt = [real(expData(iSub,iTrial).segments.sub_c{iS}(ii)) imag(expData(iSub,iTrial).segments.sub_c{iS}(ii)) 0];
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
            % calculate heading error from direct heading to waypoint
            z = expData(iSub,iTrial).segments.sub_c{iS};
            xFilt = filter_butter(20,real(z)');
            yFilt = filter_butter(20,imag(z)');
            z = xFilt + 1j*yFilt;
            dz = diff(z);
            for iz = 1:length(dz)
                heading(iz) = angle(dz(iz));
                correctheading = angle( expData(iSub,iTrial).segments.wayEnd{iS} - z(iz) );
                headingError(iz) = (wrapToPi(heading(iz)-correctheading));
            end
            expData(iSub,iTrial).segments.error{iS} = headingError;
            expData(iSub,iTrial).segments.meanError{iS} = std(headingError);
            % calculate distance to waypoint
            distanceToWaypoint = abs(z- expData(iSub,iTrial).segments.wayEnd{iS});
            
            
            % find strong corrections near waypoint
            window = 20;
            strongCorrection = false;
            clear iStrongCorrection
            correctionStrength = 0;
            for ih = round(length(heading)*.75):length(heading)-window
                correction = abs(wrapToPi(heading(ih)-heading(ih+window)));
                if correction>60*pi/180
                    strongCorrection = true;
                    if correction>correctionStrength
                        correctionStrength = correction;
                        iStrongCorrection = ih;
                    end
                end
            end
             expData(iSub,iTrial).segments.strongCorrection{iS} = strongCorrection;
             if strongCorrection
                expData(iSub,iTrial).segments.correctionStrength{iS} = correctionStrength;
                expData(iSub,iTrial).segments.correctionStrength{iS} = mean(abs(headingError(iStrongCorrection-60:iStrongCorrection-10)));
             else
                expData(iSub,iTrial).segments.correctionStrength{iS} = nan;
             end
            
            if plotSegments
                clf;
                subplot(1,2,1);  hold on;
                h = plot(real([expData(iSub,iTrial).segments.wayStart{iS} expData(iSub,iTrial).segments.wayEnd{iS}]),imag([expData(iSub,iTrial).segments.wayStart{iS} expData(iSub,iTrial).segments.wayEnd{iS}]),'--o');
                plot(real([expData(iSub,iTrial).segments.wayEnd{iS}]),imag([expData(iSub,iTrial).segments.wayEnd{iS} ]),'x','Linewidth',5);
                plot(expData(iSub,iTrial).segments.sub_c{iS},'color',h.Color)
                axis image;
                titleStr = ['Trial: ' num2str(iTrial) ' Segement: ' num2str(iS)];
                title(titleStr);
                
                subplot(1,2,2); hold on;
%                 plot(expData(iSub,iTrial).segments.error{iS})
%                 plot(distanceToWaypoint(1:end-1),heading*180/pi,'x')
                plot(headingError*180/pi)
                grid on;
                if strongCorrection
                plot([iStrongCorrection, iStrongCorrection+window],heading([iStrongCorrection, iStrongCorrection+window])*180/pi,'x','Linewidth',3)
                end
                title(['Mean error: ' num2str(expData(iSub,iTrial).segments.meanError{iS}) 'meters']);
                title(num2str(correctionStrength*180/pi));
                xlabel('Time stamps')
                ylabel('Heading (deg)');
                grid on;
                pause;
            end
        end
        
        
        
    end
end

%% Go thru our data once more to plot error as function of condition
% this section is atrocious and can be written better, I'm sure
controlError = [];
singleError = [];
gaussianError = [];
m8Error = [];
m12Error = [];
m16Error = [];


controlTime = [];
singleTime = [];
gaussianTime = [];
m8Time = [];
m12Time = [];
m16Time = [];

controlLength = [];
singleLength = [];
gaussianLength = [];
m8Length = [];
m12Length = [];
m16Length = [];

controlPathNumber = [];
singlePathNumber = [];
gaussianPathNumber =[];
m8PathNumber = [];
m12PathNumber = [];
m16PathNumber = [];

controlSC = []; % strong corrections
singleSC = [];
gaussianSC =[];
m8SC = [];
m12SC = [];
m16SC = [];

controlCS = []; % correction strength
singleCS = [];
gaussianCS =[];
m8CS = [];
m12CS = [];
m16CS = [];

for iSub = subList
    for iTrial = 1:length(expData(iSub,:))
        if strcmp(expData(iSub,iTrial).condition,'control')
            controlError = [controlError cell2mat(expData(iSub,iTrial).segments.meanError)];
            controlTime = [controlTime expData(iSub,iTrial).pathTime];
            controlLength = [controlLength expData(iSub,iTrial).pathLength];
            controlPathNumber = [controlPathNumber expData(iSub,iTrial).pathNumber];
            
            controlSC = [controlSC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            controlCS = [controlCS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        elseif strcmp(expData(iSub,iTrial).condition,'single')
            singleError = [singleError cell2mat(expData(iSub,iTrial).segments.meanError)];
            singleTime = [singleTime expData(iSub,iTrial).pathTime];
            singleLength = [singleLength expData(iSub,iTrial).pathLength];
            singlePathNumber = [singlePathNumber expData(iSub,iTrial).pathNumber];
            
            singleSC = [singleSC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            singleCS = [singleCS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        elseif strcmp(expData(iSub,iTrial).condition,'gaussian')
            gaussianError = [gaussianError cell2mat(expData(iSub,iTrial).segments.meanError)];
            gaussianTime = [gaussianTime expData(iSub,iTrial).pathTime];
            gaussianLength = [gaussianLength expData(iSub,iTrial).pathLength];
            gaussianPathNumber = [gaussianPathNumber expData(iSub,iTrial).pathNumber];
            
            gaussianSC = [gaussianSC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            gaussianCS = [gaussianCS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        end
        
        if expData(iSub,iTrial).belt==8 && ~strcmp(expData(iSub,iTrial).condition,'control')
            m8Error = [m8Error cell2mat(expData(iSub,iTrial).segments.meanError)];
            m8Time = [m8Time expData(iSub,iTrial).pathTime];
            m8Length = [m8Length expData(iSub,iTrial).pathLength];
            m8PathNumber = [m8PathNumber expData(iSub,iTrial).pathNumber];
            
            m8SC = [m8SC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            m8CS = [m8CS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        elseif expData(iSub,iTrial).belt==12 && ~strcmp(expData(iSub,iTrial).condition,'control')
            m12Error = [m12Error cell2mat(expData(iSub,iTrial).segments.meanError)];
            m12Time = [m12Time expData(iSub,iTrial).pathTime];
            m12Length = [m12Length expData(iSub,iTrial).pathLength];
            m12PathNumber = [m12PathNumber expData(iSub,iTrial).pathNumber];
            
            m12SC = [m12SC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            m12CS = [m12CS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        elseif expData(iSub,iTrial).belt==16 && ~strcmp(expData(iSub,iTrial).condition,'control')
            m16Error = [m16Error cell2mat(expData(iSub,iTrial).segments.meanError)];
            m16Time = [m16Time expData(iSub,iTrial).pathTime];
            m16Length = [m16Length expData(iSub,iTrial).pathLength];
            m16PathNumber = [m16PathNumber expData(iSub,iTrial).pathNumber];
            
            m16SC = [m16SC cell2mat(expData(iSub,iTrial).segments.strongCorrection)];
            m16CS = [m16CS cell2mat(expData(iSub,iTrial).segments.correctionStrength)];
        end
        
        
    end
end
%% plot by presentation condition (control,
% figure(4); clf; hold on;
% histogram(controlError)
% histogram(gaussianError)
% histogram(singleError)

% plot position error bar
figure(5); clf; hold on;
x = [0 1 2];
data = [mean(controlError) mean(singleError) mean(gaussianError)];
err = [std(controlError) std(singleError) std(gaussianError)];
bar(x,180/pi*data)
hErr = errorbar(x,180/pi*data,180/pi*err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'Control','Single','Gaussian'};
ylabel('Std in heading error (deg)')
title('PATH ERROR')

% plot trial time bar
figure(6); clf; hold on;
x = [0 1 2];
data = [mean(controlTime) mean(singleTime) mean(gaussianTime)];
err = [std(controlTime) std(singleTime) std(gaussianTime)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'Control','Single','Gaussian'};
ylabel('Mean path time (seconds)')
title('PATH TIME');

% plot trial length bar
figure(7); clf; hold on;
data = [mean(controlLength) mean(singleLength) mean(gaussianLength)];
err = [std(controlLength) std(singleLength) std(gaussianLength)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'Control','Single','Gaussian'};
ylabel('Mean path length (meters)')
title('PATH LENGTH');

% plot number of strong corrections
figure(21); clf; hold on;
data = [sum(controlSC) sum(singleSC) sum(gaussianSC)];
% err = [std(m8SC) std(m12SC) std(m16SC)];
bar(x,data)
foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'Control','Single','Gaussian'};
ylabel('Number of corrections');

% plot correction strength
figure(24); clf; hold on;
controlCS(isnan(controlCS)) = [];
singleCS(isnan(singleCS)) = [];
gaussianCS(isnan(gaussianCS)) = [];
data = 180/pi*[mean(controlCS) mean(singleCS) mean(gaussianCS)];
err = 180/pi*[std(controlCS) std(singleCS) std(gaussianCS)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'Control','Single','Gaussian'};
% ylabel('Mean correction strength (deg)')
% title('Correction Strength');
ylabel('Error (deg)')
title('Error 1 second before large correction');

%% by motor number

% plot position error bar
figure(8); clf; hold on;
x = [0 1 2];
data = [mean(m8Error) mean(m12Error) mean(m16Error)];
err = [std(m8Error) std(m12Error) std(m16Error)];
bar(x,180/pi*data)
hErr = errorbar(x,180/pi*data,180/pi*err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';
foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'8 Motor','12 Motor','16 Motor'};
ylabel('Std in  heading error (deg)')
title('PATH ERROR')

% plot trial time bar
figure(9); clf; hold on;
x = [0 1 2];
data = [mean(m8Time) mean(m12Time) mean(m16Time)];
err = [std(m8Time) std(m12Time) std(m16Time)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'8 Motor','12 Motor','16 Motor'};
ylabel('Mean path time (seconds)')
title('PATH TIME');

% plot trial length bar
figure(10); clf; hold on;
data = [mean(m8Length) mean(m12Length) mean(m16Length)];
err = [std(m8Length) std(m12Length) std(m16Length)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'8 Motor','12 Motor','16 Motor'};
ylabel('Mean path length (meters)')
title('PATH LENGTH');

% plot number of strong corrections
figure(22); clf; hold on;
data = [sum(m8SC) sum(m12SC) sum(m16SC)];
% err = [std(m8SC) std(m12SC) std(m16SC)];
bar(x,data)
% hErr = errorbar(x,data,err);
% hErr.Color = [0 0 0];
% hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'8 Motor','12 Motor','16 Motor'};
ylabel('Number of strong corrections');

% plot correction strength
figure(23); clf; hold on;
m8CS(isnan(m8CS)) = [];
m12CS(isnan(m12CS)) = [];
m16CS(isnan(m16CS)) = [];
data = 180/pi*[mean(m8CS) mean(m12CS) mean(m16CS)];
err = 180/pi*[std(m8CS) std(m12CS) std(m16CS)];
bar(x,data)
hErr = errorbar(x,data,err);
hErr.Color = [0 0 0];
hErr.LineStyle = 'none';

foo = gca;
foo.XTick = [0,1,2];
foo.XTickLabel = {'8 Motor','12 Motor','16 Motor'};
% ylabel('Mean correction strength (deg)')
% title('Correction Strength');
ylabel('Error (deg)')
title('Error 1 second before large correction');


%% plot path time by trial number
ip = 1:36;
figure(82); clf; hold on;
for iSub = subList
    pathN = [expData(iSub,ip).pathNumber];
    pTime = [expData(iSub,ip).pathTime];
    [sortedPathN,sortInd] = sort(pathN);
    sortedPathTime = pTime(sortInd);
    
    color = [];
    iC = 1;
    for ii=sortInd
        if expData(iSub,ii).belt==8
            color(iC,:) = [1 0 0 ];
        elseif expData(iSub,ii).belt==12
            color(iC,:) = [0 1 0 ];
        elseif expData(iSub,ii).belt==16
            color(iC,:) = [0 0 1 ];
        end
        if strcmp(expData(iSub,ii).condition,'control')
            color(iC,:) = [0 0 0 ];
        end
        iC = iC+1;
    end
    
    
    scatter(sortedPathN,sortedPathTime,25,color,'filled')
    
    % fit linear to it
    p = polyfit(sortedPathN(7:end),sortedPathTime(7:end),1);
    plot(sortedPathN(7:end),polyval(p,sortedPathN(7:end)));
end
xlabel('Path number');
ylabel('Path time (s)');

















