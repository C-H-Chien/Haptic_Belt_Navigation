clearvars; close all; clc;
load relIntTask_subjectViktor_26-Mar-2021
% load relIntTask_subjectViktor2_26-Mar-2021
% load relIntTask_subjectViktor3_26-Mar-2021

%% plot
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
