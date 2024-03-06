 function [vOutput] = filter_butter (Hz,vInput)
% filter_butter   Butterworth low-pass filter with linear extrapolation. 
%   filter_butter(hZ, varargin) Filters and returns input vector with a 
%   Butterworth low-pass filter using standard VENLab parameters and 
%   sample rate hZ. Extrapolates first and last 0.5 sec to avoid transient 
%   at either end. 

% Filter both x and y independently.

% Created by Henry Harrison, 2010
% Modified by Kevin Rio, 2013
% Modified by Gregory Dachner, 2017 / gdachner@gmail.com
% Brown University

% Compute parameters
cutoff = (0.6); % standard VENLab parameters

[B,A] = butter(4,cutoff/(Hz/2));

% Determine how many time-steps to use for extrapolation (default = 30)
if length(vInput) > 30
    pad = 30;
else
    pad = length(vInput);
end

% Pad data with timesteps to extrapolate into
tot_time = 1:((length(vInput))+(pad*8));

extrap_pre = 1:pad*4;
extrap_post = length(tot_time)-120+1:length(tot_time);

exist_data_location = (length(extrap_pre)+1):(extrap_post(1)-1);
exist_data_location = exist_data_location';

toExtrap = vertcat(extrap_pre',extrap_post');

% Extrapolate
outExtrap = interp1(exist_data_location,vInput,toExtrap,'linear','extrap');
outExtended = vertcat((outExtrap(1:length(outExtrap)/2)),(vInput),(outExtrap((length(outExtrap)/2)+1:end)));

% Apply butterworth filter and return input to original size
outFiltered = filtfilt(B,A,outExtended); 
vOutput = outFiltered((pad*4)+1:(end-pad*4));

