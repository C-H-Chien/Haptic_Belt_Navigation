clearvars; close all;
load matlabColors;
%% Create the plot scaffold
figure(1); clf; hold on;
nMotor = 12;
motorPower = rand(nMotor,1);

% belt shape
aBelt = 1;
bBelt = 0.5;
thetaBelt = linspace(0,2*pi);
belt = aBelt*cos(thetaBelt) + 1j*bBelt*sin(thetaBelt);

% motor locations
% angleOffset = 0;%pi/nMotor;
% thetaMotor = wrapToPi(linspace(2/3*pi,2/3*pi+2*pi,nMotor+1)+angleOffset);
% thetaMotor = thetaMotor(1:end-1);
% motors = aBelt*cos(thetaMotor) + 1j*bBelt*sin(thetaMotor);

angleOffset = 90; % matlab 0 is at right. Vizard, 0 is straight ahead
firstAng = 0;%360/nMotor;
thetaMotor = wrapTo180(linspace(firstAng,firstAng+360,nMotor+1)+angleOffset);
thetaMotor = thetaMotor(1:end-1)*pi/180;
motors = aBelt*cos(thetaMotor) + 1j*bBelt*sin(thetaMotor);

% Plot it
plot(belt,'Color',mlc.orange);
plot(motors,'o','Color',mlc.orange,'MarkerFaceColor',mlc.orange);
axis image;
axis([-2 2 -2 2]);
%%
% motor strengths plot entities
for iM = 1:nMotor
    strLine =[motors(iM) motors(iM) + motorPower(iM)*exp(1j*thetaMotor(iM))];
    hm(iM) = plot(real(strLine),imag(strLine),'Color',mlc.orange);
%     text(real(strLine(1)),imag(strLine(1)),num2str(iM+1))
%     ang = wrapToPi(thetaMotor(iM)-pi/2)*180/pi;
%     text(real(strLine(1)),imag(strLine(1)),num2str(ang))
end




%% Comms and update plot
s = serialport('COM6',115200);
dataList = [];
tic;
while 1
    data = readline(s);
    dataNum = str2num(data);
    dataList = [dataNum];
    if ~isempty(dataNum)
%         disp(dataList)
%         motorList = dataList(1:end-2);
%         motorPower = dataList(end)/100;
        for iM = 1:nMotor
            motorPower = dataList(iM)/255;
            strLine =[motors(iM) motors(iM) + motorPower*exp(1j*thetaMotor(iM))];
            hm(iM).XData = real(strLine);
            hm(iM).YData = imag(strLine);
        end
        dataList = [];
    end
% readline(s)
end