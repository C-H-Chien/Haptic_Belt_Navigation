//AT+SETTING=DEFPERIPHERAL


#include "SoftPWM.h"

// define the channels we'll being using the softPWM library to run. Maybe there's a 'prettier' way to do this initialization by hiding in another file

//SOFTPWM_DEFINE_CHANNEL(0, DDRD, PORTD, PORTD0);  //Arduino pin 0
//SOFTPWM_DEFINE_CHANNEL(1, DDRD, PORTD, PORTD1);  //Arduino pin 1
SOFTPWM_DEFINE_CHANNEL(2, DDRD, PORTD, PORTD2);  //Arduino pin 2
SOFTPWM_DEFINE_CHANNEL(3, DDRD, PORTD, PORTD3);  //Arduino pin 3
SOFTPWM_DEFINE_CHANNEL(4, DDRD, PORTD, PORTD4);  //Arduino pin 4
SOFTPWM_DEFINE_CHANNEL(5, DDRD, PORTD, PORTD5);  //Arduino pin 5
SOFTPWM_DEFINE_CHANNEL(6, DDRD, PORTD, PORTD6);  //Arduino pin 6
SOFTPWM_DEFINE_CHANNEL(7, DDRD, PORTD, PORTD7);  //Arduino pin 7
SOFTPWM_DEFINE_CHANNEL(8, DDRB, PORTB, PORTB0);  //Arduino pin 8
SOFTPWM_DEFINE_CHANNEL(9, DDRB, PORTB, PORTB1);  //Arduino pin 9
SOFTPWM_DEFINE_CHANNEL(10, DDRB, PORTB, PORTB2);  //Arduino pin 10
SOFTPWM_DEFINE_CHANNEL(11, DDRB, PORTB, PORTB3);  //Arduino pin 11
SOFTPWM_DEFINE_CHANNEL(12, DDRB, PORTB, PORTB4);  //Arduino pin 12
SOFTPWM_DEFINE_CHANNEL(13, DDRB, PORTB, PORTB5);  //Arduino pin 13
//SOFTPWM_DEFINE_CHANNEL(14, DDRC, PORTC, PORTC0);  //Arduino pin A0
//SOFTPWM_DEFINE_CHANNEL(15, DDRC, PORTC, PORTC1);  //Arduino pin A1
//SOFTPWM_DEFINE_CHANNEL(16, DDRC, PORTC, PORTC2);  //Arduino pin A2
//SOFTPWM_DEFINE_CHANNEL(17, DDRC, PORTC, PORTC3);  //Arduino pin A3
//SOFTPWM_DEFINE_CHANNEL(18, DDRC, PORTC, PORTC4);  //Arduino pin A4
//SOFTPWM_DEFINE_CHANNEL(19, DDRC, PORTC, PORTC5);  //Arduino pin A5

SOFTPWM_DEFINE_OBJECT_WITH_PWM_LEVELS(14, 256); // arg1 is number of channels. Needs to go to at least 14 since we using pin 13. Not sure why it works this way. arg2 is PWM lvls

int const nMotor = 12;
int motorPowerList[nMotor];
//int motorPin[nMotor] = {13,12,11,10,9,8,7,6,5,4,3,2}; // for 12 motor belt only
//int motorPin[nMotor] = {10,9,8,7,6,5,4,3,2,13,12,11}; // for 12 motor belt only, rotated 90 deg CW
int motorPin[nMotor] = {10,11,12,13,2,3,4,5,6,7,8,9}; // for 12 motor belt only, rotate 90 cw
int motorIdx;
bool recordMessage = false;
bool checkMessage = false;
void setup() {
  Serial.begin(115200);

  // begin with 100Hz pwm frequency
  Palatis::SoftPWM.begin(100);
  // print interrupt load for diagnostic purposes
  Palatis::SoftPWM.printInterruptLoad();
  
}

void loop() {
  while (Serial.available() > 0) {
    int data = Serial.read(); // read a byte serial line

    if(data==254){ // means the message is complete and it's time to validate
      recordMessage = false;
      checkMessage = true;
    }
    
    if(recordMessage){
      if(motorIdx<nMotor){ // if motorIdx>nMotor then something has gone wrong and we shouldnt assign outside of size of array
        motorPowerList[motorIdx] = data;
        motorIdx++; //increment so the next time thru the loop stores the next motor value
      }
    }

    if(checkMessage){
      bool messagePass = true; // assume the message passed until we show otherwise
      for(int iM=0; iM<nMotor;iM++){
        if(motorPowerList[iM]<0){
          messagePass = false; // if any of the values are negative, something went wrong
        }
      }
      if(messagePass){ // if the message passed, write to the motors and print to serial line
        for(int iM=0; iM<nMotor;iM++){
          Serial.print(motorPowerList[iM]);
          Serial.print(' ');
          //write message to motors
          int8_t thisPin = motorPin[iM]; // I'm not sure if this variable needs to be int8_t rather than int. Mostly superstition, should test.
          Palatis::SoftPWM.set(thisPin, motorPowerList[iM]); // use software pwm library to write to the motor pins
        }
        Serial.println(' ');
        checkMessage = false; // we just checked it so let's be done
      }
    }

    if(data==255){ // 255 means the message is about to begin. This block needs to be after the record message block otherwise we'll record 255 in the power list
      recordMessage = true;
      for(int iM=0; iM<nMotor; iM++){ // clear motorPowerList in prep for new message
        motorPowerList[iM] = -10; // set negative for now so we know if something went wrong later
      }
      motorIdx = 0;
    }
  }
  //debugg
  //uint8_t i = 11;
  //Palatis::SoftPWM.set(i, 255);
  delay(0); // possibly needed for softPWM library. A superstition, should test.
}
