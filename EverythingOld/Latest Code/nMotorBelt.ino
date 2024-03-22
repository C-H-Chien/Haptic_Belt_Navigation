/*
 * Haptic Belt Controller Script [n-Motor Belt]
 */

int inData = 0; // incoming serial data
int motors[12] = {13,12,11,10,9,8,7,6,5,4,3,2} ; //order of the motors on the belt, also labeled on the belt in sharpie
const int numMotors = 12; 
int motorData[numMotors]; //Stores the incoming motor ID's - gets sorted before writing to the belt
int intensities[numMotors]; //Stores the incoming motor intensities - gets sorted before writing to the belt
int prevMotorData[numMotors]; //Stores the previous data for writing while new data comes in 
int prevIntensities[numMotors]; //Stores the previous data for writing while new data comes in 
int motorCounter = 0; //Counter for reading 
int motorCounterWrite = 0; //Counter for writing 
int msgStart = 1; //Represents the start of a new data stream
int msgEnd = 2; //Represents the end of a data stream
int state = 0; //Defines state of system: 0 - standby, 1 - read
unsigned long startMillis = 0 ; //Stores the start time 


void setup() {
  // Initialize pins
  for(int i = 0 ;i < numMotors ; i ++){
    pinMode(motors[i],OUTPUT) ;
  }

  startMillis = millis() ;
  Serial.begin(115200);       //Baud rate meant for bluetooth, maybe also 9600 works? I didn't try and it doenst really matter
  while (!Serial) { /*some device need time for Serial to load */ }
}


void loop(){
  
  //When new data is available, standby or read depending on state of system
  if (Serial.available() > 0){
    
      //Read data from serial
      inData = Serial.read();
      
      
      //In 'standby' state, reset motorCounter
      if (state == 0) {
        motorCounter = 0;
        
        //Check for start of message
        if (inData == msgStart) {
          state = 1; //Change to 'read' state
        }  


        //In 'read' state, save incoming intensity data to an array
      } else if (state == 1) {
        
        //If message is too long go straight to standby state
        if (motorCounter > numMotors) {
            state = 0; 

        //Check for end of message
        } else if (inData == msgEnd){
          
          //If message is not of right length, change back to standby state
          if (motorCounter != numMotors) {
            state = 0; //Change to standby state because data was not of right length


          //Otherwise, sort data and latch it for writing
          } else { 

            //Sort data using bubble sort - need intensitites to be ordered (in descending order)for writing to motors 
            for (int i = 0; i < numMotors-1; i++) {
              for (int j = 0; j < numMotors-1; j++) {
                
                int int1 = intensities[j];
                int int2 = intensities[j+1];
                
                if (int2 > int1) {
                  
                  //Swap elements AND keep track of motor ID 
                  intensities[j] = int2;
                  intensities[j+1] = int1;
                  int tempID = motorData[j];
                  motorData[j] = motorData[j+1];
                  motorData[j+1] = tempID;  
                }
              
              }
            }
    
            //Latch data for writing
            for (int i=0; i<numMotors; i++) {
              prevIntensities[i] = intensities[i];
              prevMotorData[i] = motorData[i]; 
            }
            

            //Reset state to begin reading next message 
            state = 0;
          }    

          
        //Save the incoming data   
        } else {
          motorData[motorCounter] = motorCounter;
          intensities[motorCounter] = inData; 

          //The counter acts as the index for the motor matrix and is used to ensure that the message is of correct length
          motorCounter++; 
        }
      }        
  }
 
 //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
 //The following code runs constantly regardless of the serial line
 

    /*
     * Writing to the motors - activate motors as needed based on the sorted intensity data. There are a maximum of 256 intensities (could have an arbitrary number no?)
     * The loop always runs completely giving a total period of 256*40us = 10.24ms per vibration.  
     * The highest intensity motors get fired first followed by the lowest intensity motors. Appropriate delays are left between intensity increments to create a PWM signal of  
     * the desired duty cycle. 
     * Once the full period is finished and all motors have been fired. Each motor is turned off in preparation for the next data stream. 
     */
    motorCounterWrite = 0; 
    for (int intensityCounter = 255; intensityCounter >= 0; intensityCounter--) {
      
      //If all motors have been fired or intensity of next motor is 0, break loop
      if (motorCounterWrite == numMotors) {
        delayMicroseconds(40); 
        
      //Check if intensity iterator matches the next motor's intensity
      } else if (prevIntensities[motorCounterWrite] == intensityCounter) {
        digitalWrite(motors[prevMotorData[motorCounterWrite]],HIGH); //Activate associated motor
        motorCounterWrite++; intensityCounter++; //Increment both counters to move onto next motor but stay at same intensity (multiple motors could have same intensity)

      //Otherwise, delay and enter next iteration of loop
      } else {
        delayMicroseconds(40); 
      }
      
    }
    
    //Turn off all motors before next message is read 
    for (int i = 0; i < numMotors; i++) {
      digitalWrite(motors[i], LOW) ;
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


}
