/*
 * Haptic Belt Controller Script
/*
 * Haptic Belt Controller Scipt [8-Motor Belt]
 */

int inData = 0;                        // incoming serial data
int motors[8] = {12,11,10,9,8,7,6,5} ; //order of the motors on the belt, also labeled on the belt in sharpie
const int numMotors = 8 ; 

int motorsToFireI10 = 0 ;                //iterator for motorsToFire10
int motorsToFireI8 = 0 ;                 //iterator for motorsToFire8
int motorsToFireI6 = 0 ;                 //iterator for motorsToFire6
int motorsToFireI4 = 0 ;                 //iterator for motorsToFire4
int motorsToFireI2 = 0 ;                 //iterator for motorsToFire2

bool readyToWrite = false;
bool store10 = false;
bool store8 = false;
bool store6 = false;
bool store4 = false;
bool store2 = false;

int motorsToFire10[numMotors] ;          //array of what motors should be fired on HIGH
int motorsToFire8[numMotors] ;           //array of what motors should be fired on 80%
int motorsToFire6[numMotors] ;           //array of what motors should be fired on 60%
int motorsToFire4[numMotors] ;           //array of what motors should be fired on 40%
int motorsToFire2[numMotors] ;           //array of what motors should be fired on 20%

unsigned long startMillis = 0 ;



// NOTE: Data comes in as motor,motor,...,0,time1,time2

/*
 * The main idea behind setup is to set up the pinMode for the motors to be able to write to each pin.
 * We also set each element in motorsToFire10/8/6 to 0. If a motor is to be fired:
 * (a) at intensity 10: it will be added to motorsToFire10
 * (b) at intensity 8: it will be added to motorsToFire10 and motorsToFire8
 * (c) at intensity 6: it will be added to motorsToFire10 and motorsToFire6
 */

void setup() {
  // Initially, all motors in motorsToFire are set to 0
  for(int i = 0 ;i < numMotors ; i ++){
    pinMode(motors[i],OUTPUT) ;
    motorsToFire10[i] = 0 ;
    motorsToFire8[i] = 0 ;
    motorsToFire6[i] = 0 ;
  }
  startMillis = millis() ;
  Serial.begin(115200);       //Baud rate meant for bluetooth, maybe also 9600 works? I didn't try and it doenst really matter
  while (!Serial) { /*some device need time for Serial to load */ }
}

/* The main idea behind the loop script is to receive and process in-data that comes in the form 255,X,X,X,...254,X,X,X,...,253,X,X,X,..,252,X,X,...,251,X,X,...,250
 * 
 * All numbers AFTER 255 and BEFORE 254 are motors to fire at intensity 10.
 * All numbers AFTER 254 and BEFORE 254 are motors to fire at intensity 8.
 * All numbers AFTER 253 and BEFORE 252 are motors to fire at intensity 6.
 * All numbers AFTER 252 and BEFORE 251 are motors to fire at intensity 4.
 * All numbers AFTER 251 and BEFORE 250 are motors to fire at intensity 2.
 * 
 * The motorsToFire10 list contains all motors that will be fired (regardless of intensity).
 * The motorsToFire8 list contains all motors that will be fired at intensity 8.
 * The motorsToFire6 list contains all motors that will be fired at intensity 6.
 * The same logic is applied to motorsToFire4 and motorsToFire2.
 * Thus, all motors not in motorsToFire8 and motorsToFire6 are fired at intensity 10 by default.
 * 
 * motorsToFireI10/8/6/4/2 represent iterators for the above 5 lists.
 * 
 * Booleans store10 / store8 / store6 / store4 / store2 are true when we are adding motors to 
 * their respective lists respectively. 
 * 
 * The boolean readyToWrite is only set to true after 250 is received. After this point, 
 * the belt will vibrate given the gesture received until a new serial input is received.
 * At this time, when 255 (the start number of a new sequence) is received, readyToWrite
 * is set again to false until the new motorsToFire10/8/6/4/2 lists are populated.
 * 
 */
void loop(){

  if (Serial.available() > 0){

      inData = Serial.read();
      /*
       * 255 indicates the start of the sequence. 
       * readyToWrite is set to false and all iterators and 
       * the motorsToFire10/8/6 lists are set to zeros.
       */
      if (inData == 255) {
        readyToWrite = false ; 
        store10 = true ; store8 = false ; store6 = false ; store4 = false ; store2 = false ;
        motorsToFireI10 = 0 ;
        motorsToFireI8 = 0 ;
        motorsToFireI6 = 0 ;
        motorsToFireI4 = 0 ; 
        motorsToFireI2 = 0 ;
        for(int i = 0 ; i < numMotors ; i++) {
          motorsToFire10[i] = 0 ;
          motorsToFire8[i] = 0 ;
          motorsToFire6[i] = 0 ;
          motorsToFire4[i] = 0 ;
          motorsToFire2[i] = 0 ;
        }
      }

      else if (inData == 254) {
        store10 = false ;
        store8 = true ; 
      }

      else if (inData == 253) {
        store8 = false ;
        store6 = true ;
      }

      else if (inData == 252) {
        store6 = false ;
        store4 = true ;
      }

      else if (inData == 251) {
        store4 = false ;
        store2 = true ;
      }

       /*
       * 250 indicates the end of the sequence. 
       * All iterators are set to 0 and readyToWrite is set to true.
       */
      else if (inData == 250) {
        store2 = false ; store4 = false ;store6 = false ; store8 = false ; store10 = false ;
        motorsToFireI10 = 0 ;
        motorsToFireI8 = 0 ; 
        motorsToFireI6 = 0 ;
        motorsToFireI4 = 0 ;
        motorsToFireI2 = 0 ;
        readyToWrite = true ;
      }

      else if(store10) {
        motorsToFireI10++ ;
        motorsToFire10[motorsToFireI10-1] = inData ;
      }

      else if (store8) {
        motorsToFireI10++ ;
        motorsToFireI8++ ;
        motorsToFire10[motorsToFireI10-1] = inData ;
        motorsToFire8[motorsToFireI8-1] = inData ;
      }

      else if (store6) {
        motorsToFireI10++ ;
        motorsToFireI6++ ;
        motorsToFire10[motorsToFireI10-1] = inData ;
        motorsToFire6[motorsToFireI6-1] = inData ;
      }

      else if (store4) {
        motorsToFireI10++ ;
        motorsToFireI4++ ;
        motorsToFire10[motorsToFireI10-1] = inData ;
        motorsToFire4[motorsToFireI4-1] = inData ;
      }

      else if (store2) {
        motorsToFireI10++ ;
        motorsToFireI2++ ;
        motorsToFire10[motorsToFireI10-1] = inData ;
        motorsToFire2[motorsToFireI2-1] = inData ;
      }
  }

  /*
   * This segment of code is only activated when readyToWrite holds true (after receiving a "250" from Serial)
   * All motors in the motorsToFire10 list are fired. 
   * After 6 milliseconds, motors in the motorsToFire6 list are then turned to LOW. 
   * After 8 milliseconds, motors in the motorsToFire8 list are then turned to LOW. 
   * After a 2 millisecond pause, this repeats.
   */

  else if (readyToWrite) {
    for (int i = 0 ; i < numMotors && motorsToFire10[i] > 0 ; i++) digitalWrite(motors[motorsToFire10[i] - 1], HIGH) ;
    delay(4) ;
    for (int i = 0 ; i < numMotors && motorsToFire2[i] > 0 ; i++) digitalWrite(motors[motorsToFire2[i] - 1], LOW) ;
    delay(4) ;
    for (int i = 0 ; i < numMotors && motorsToFire4[i] > 0 ; i++) digitalWrite(motors[motorsToFire4[i] - 1], LOW) ;
    delay(4) ;
    for (int i = 0 ; i < numMotors && motorsToFire6[i] > 0 ; i++) digitalWrite(motors[motorsToFire6[i] - 1], LOW) ;
    delay(4) ;
    for (int i = 0 ; i < numMotors && motorsToFire8[i] > 0 ; i++) digitalWrite(motors[motorsToFire8[i] - 1], LOW) ;
    delay(4) ;
    for (int i = 0 ; i < numMotors && motorsToFire10[i] > 0 ; i++) digitalWrite(motors[motorsToFire10[i] - 1], LOW) ;
  }
  
  /* 
   *  This segment of code refreshes the serial line every 5 seconds. 
   *  Here, we flush the serial output and restart the serial line at 115200 
   *  every 5 seconds and restart the timer (startMillis). This ensures that there 
   *  is no buffer overflow in the cache.
   */
  if (millis() - startMillis > 5000) {
    Serial.flush() ;
    Serial.end() ;
    Serial.begin(115200) ;
    while (!Serial) {}
    startMillis = millis() ;
    Serial.println("restarted") ;
  }
}
