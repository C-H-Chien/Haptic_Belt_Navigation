//AT+SETTING=DEFPERIPHERAL


#include "SoftPWM.h"

//Define the channels we'll being using the softPWM library to run
SOFTPWM_DEFINE_CHANNEL(0, DDRD, PORTD, PORTD0);  //Arduino pin 0
SOFTPWM_DEFINE_CHANNEL(1, DDRD, PORTD, PORTD1);  //Arduino pin 1
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
SOFTPWM_DEFINE_CHANNEL(14, DDRC, PORTC, PORTC0);  //Arduino pin A0
SOFTPWM_DEFINE_CHANNEL(15, DDRC, PORTC, PORTC1);  //Arduino pin A1
SOFTPWM_DEFINE_CHANNEL(16, DDRC, PORTC, PORTC2);  //Arduino pin A2
SOFTPWM_DEFINE_CHANNEL(17, DDRC, PORTC, PORTC3);  //Arduino pin A3
SOFTPWM_DEFINE_CHANNEL(18, DDRC, PORTC, PORTC4);  //Arduino pin A4
SOFTPWM_DEFINE_CHANNEL(19, DDRC, PORTC, PORTC5);  //Arduino pin A5

SOFTPWM_DEFINE_OBJECT_WITH_PWM_LEVELS(18, 256); // arg1 is number of channels. Needs to go to at least 18 since we using pin 17. Not sure why it works this way. arg2 is PWM lvls

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//Define variables
int const nMotor = 12;
int motorPowerList[nMotor];
int motorIdx;
bool recordMessage = false;
bool checkMessage = false;
int msgStart = 1; //Represents the start of a new data stream
int msgEnd = 2; //Represents the end of a data stream
unsigned long startMillis = 0 ; //Stores the start time 

//Define the pinlayout (all 3 pinouts are stated for simplicity sake, just comment out the two that are not being used)
//int motorPin[8] = {5,6,7,8,9,10,11,12}; // for 8 motor belt only
int motorPin[12] = {13,12,11,10,9,8,7,6,5,4,3,2}; // for 12 motor belt only
//int motorPin[16] = {2,3,4,5,6,7,8,9,10,11,12,13,A0,A1,A2,A3}; // for 16 motor belt only

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

    if(data==msgEnd){ // means the message is complete and it's time to validate
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
          //write message to motors
          int8_t thisPin = motorPin[iM]; // I'm not sure if this variable needs to be int8_t rather than int. Mostly superstition, should test.
          Palatis::SoftPWM.set(thisPin, motorPowerList[iM]); // use software pwm library to write to the motor pins
        }
        checkMessage = false; // we just checked it so let's be done
      }
    }

    if(data==msgStart){ // 255 means the message is about to begin. This block needs to be after the record message block otherwise we'll record 255 in the power list
      recordMessage = true;
      for(int iM=0; iM<nMotor; iM++){ // clear motorPowerList in prep for new message
        motorPowerList[iM] = -10; // set negative for now so we know if something went wrong later
      }
      motorIdx = 0;
    }
  }

    /* 
   *  Here, we flush the serial output and restart the serial line at 115200 
   *  every 5 seconds and restart the timer (startMillis). This ensures that there 
   *  is no buffer overflow in the cache.
   */
  if (millis() - startMillis > 5000) {
    Serial.println(" ");
    Serial.flush() ;
    Serial.end() ;
    Serial.begin(115200) ;
    while (!Serial) {}
    startMillis = millis() ;
    Serial.println("restarted") ;
  }
  
  delay(0); // possibly needed for softPWM library. A superstition, should test.
}
