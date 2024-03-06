% Uses the Quest+ adaptive staircase method
% OG paper: https://link.springer.com/article/10.3758/BF03202828. Using
% Example 1 here.
% MATLAB implementation: https://github.com/petejonze/QuestPlus
%                        https://openresearchsoftware.metajnl.com/articles/10.5334/jors.195/
clearvars; close all;

simExp = false;

%% setup some serial stuff to talk to belt
if ~simExp
    s = serialport('COM3',115200);
    %%
    mL = 250;
    mR = 250;
    messageOn = makeMessage(mL,mR);
    messageOff = makeMessage(0,0);
    disp('No vibrations should be present...');
    write(s,messageOn,'uint8');
    pause(3);
    write(s,messageOff,'uint8');
    pause(1);
    
    mL = 250;
    mR = 250;
    messageOn = makeMessage(mL,mR);
    disp('Both motors vibrating...');
    write(s,messageOn,'uint8');
    pause(3);
    write(s,messageOff,'uint8');
    pause(1);
    
    mL = 250;
    mR = 0;
    messageOn =  makeMessage(mL,mR);
    disp('Left motor vibrating...');
    write(s,messageOn,'uint8');
    pause(3);
    write(s,messageOff,'uint8');
    pause(1);
    
    mL = 0;
    mR = 250;
    messageOn =  makeMessage(mL,mR);
    disp('Right motor vibrating...');
    write(s,messageOn,'uint8');
    pause(3);
    write(s,messageOff,'uint8');
end

% set reference strength;
ref_strn = 0.5;

% set model
PF = @(x,threshold)(.5+(1-.5-.02)*cdf('wbl',10.^(x/20),10.^(threshold/20),3.5));
PF_pre = @(x,threshold,slope,guess,lapse) guess+(1-guess-lapse)*cdf('wbl',10.^(x/20),10.^(threshold/20),slope) ;
slope = 3.5;
guess = 0.5;
lapse = 0.02;
PF = @(x,threshold) PF_pre(x,threshold,slope,guess,lapse);
% set true param(s)
threshold = -5;
trueParams = {threshold};
% create QUEST+ object
stimDomain      = -40:0.5:6;
paramDomain     = -40:0.5:6;
respDomain      = [0 1];
stopRule     	= 'entropy';
stopCriterion 	= 2.5;
minNTrials     	= 32;
maxNTrials     	= 512;
QP = QuestPlus(PF, stimDomain, paramDomain, respDomain, stopRule, stopCriterion, minNTrials, maxNTrials);
% initialise priors/likelihoods
QP.initialise();
% run
startGuess_mean = QP.getParamEsts('mean');
startGuess_mode = QP.getParamEsts('mode');
correctHist = [];

while ~QP.isFinished()
    targ = QP.getTargetStim();
    
    % do some conversions to get motor strength in pwm
    ratio = 10^(targ/20);
    pm = [-1 1];
    pm = pm(randi(2)); % get a random plus minus
    stim_strn = ref_strn + pm * ref_strn*ratio;
%     stim_strn = ref_strn * ratio;
    ref_pwm = round(255*ref_strn);
    stim_pwm = round(255*stim_strn);
    
    % decide left and right motor instensiy
    referenceIsLeft = rand()<0.5;
    if referenceIsLeft
        mL = ref_pwm;
        mR = stim_pwm;
    else
        mL = stim_pwm;
        mR = ref_pwm;
    end
    mL;
    mR;
    
    anscorrect = rand() < PF(targ,trueParams{:});
    
    if ~simExp
        % compose message for belt
        messageOn =  makeMessage(mL,mR);
        messageOff =  makeMessage(0,0);
        write(s,messageOn,'uint8');
        pause(1);
        write(s,messageOff,'uint8');
        
        % ask user for their response
        disp('Check dialog box...');
        answer = questdlg('Is the left or right vibration stronger?', ...
            '.', ...
            'Left','Right','Left');
        
        % check correct answer
        if mL>mR
            correct_answer = 'Left';
        else
            correct_answer = 'Right';
        end
        % see if the subject got it right
        anscorrect = strcmp(answer,correct_answer);   

    end
    correctHist = [correctHist; anscorrect];
    QP.update(targ, anscorrect);
end
% get final parameter estimates
endGuess_mean = QP.getParamEsts('mean');
endGuess_mode = QP.getParamEsts('mode');

%%
% work some magic on the history of responses
stimCount = 0*stimDomain;
idxList = cell(1,length(stimDomain));
percCorr = 0*stimDomain;
for iS = 1:length(stimDomain)
    for iH = 1:length(QP.history_stim)
        if QP.history_stim(iH)==stimDomain(iS)
            stimCount(iS) = stimCount(iS) + 1;
            
            idxList{iS} = [idxList{iS}; iH];
            
        end
    end
end
for iS = 1:length(stimDomain)
    idxs = idxList{iS};
    if isempty(idxs)
        percCorr(iS) = nan;
    else
        percCorr(iS) = sum(QP.history_resp(idxs))/length(QP.history_resp(idxs));
    end
end
colors = [];
for iR = 1:length(correctHist)
    if correctHist(iR)==1
        colors = [colors; [0 1 0]];
    else
        colors = [colors; [1 0 0]];
    end
end



% plot
nTrials = length(QP.history_stim)
rf1 = 0.025 - 0.05*rand(1,nTrials);
rf2 = 0.025 - 0.05*rand(1,nTrials);

figure(); hold on;
muBest = endGuess_mean;
PF_eval = PF(stimDomain,muBest);
plot(stimDomain,PF_eval);
nStim = length(QP.history_stim);
%                     plot(QP.history_stim+(1-2*rand(1,nStim)),ones(1,nStim),'*');
stimCount(stimCount==0) = nan;
scatter(stimDomain,percCorr,5*stimCount);
scatter(QP.history_stim(:)+rf1',QP.history_resp(:)+0*rf2',15,colors,'filled');

xlabel('Contrast (dB)');
ylabel('Probability');

%%
ratioBest = 10^(muBest/20);
% pwmDiff = ref_pwm*ratioBest - ref_pwm;
pwmDiff = ref_pwm*ratioBest;
powerDiff = pwmDiff / ref_pwm * 100;

titleStr = {['Threshold is ' num2str(muBest) 'dB'];...
            ['Ratio is ' num2str(ratioBest)];...
            ['PWM difference is ' num2str(pwmDiff) ' with reference ' num2str(ref_pwm) 'PWM'];...
            ['or ' num2str(powerDiff) '\% of the reference']};
title(titleStr);

subjectNum = 1;
fileStr = ['relIntTask_subject' num2str(subjectNum) '_' date];
if isfile([fileStr '.mat'])
    subjectNum = subjectNum+1;
end
save(['relIntTask_subject' num2str(subjectNum) '_' date]); % save everything to disk to look at it later.

%% idk
% display generic status report
QP.disp(); % show QUEST+ info

% compare estimates to 'ground truth' (known exactly, since
% simulated)
n = length(startGuess_mean);
fprintf('\n-------------------------------------------------\n');
for i = 1:n
    fprintf('Parameter %i of %i\n', i, n);
    fprintf(' True Value = %1.2f\n', trueParams{i});
    fprintf('Start Guess = %1.2f (mean), %1.2f (mode)\n', startGuess_mean(i), startGuess_mode(i));
    fprintf('  End Guess = %1.2f (mean), %1.2f (mode)\n', endGuess_mean(i), endGuess_mode(i));
end
fprintf('-------------------------------------------------\n\n\n');


function message = makeMessage(mL,mR)
%     message = [255, 0, 0, mR, mL, 0,0,0,0,0,0,0,0,254]; % clip centered belt
    message = [255, mL, 0, 0, 0, 0,0,0,0,0,0,0,mR,254]; % rotate 90 deg belt
end
