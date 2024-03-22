//AT+SETTING=DEFPERIPHERAL

int const nMotor = 8;
int motorPowerList[nMotor];
int motorIdx;
bool recordMessage = false;
bool checkMessage = false;
void setup() {
  Serial.begin(115200);
  
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
      bool messagePass = true;
      for(int iM=0; iM<nMotor;iM++){
        if(motorPowerList[iM]<0){
          messagePass = false;
        }
      }
      if(messagePass){
        for(int iM=0; iM<nMotor;iM++){
          Serial.print(motorPowerList[iM]);
          Serial.print(' ');
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
}
