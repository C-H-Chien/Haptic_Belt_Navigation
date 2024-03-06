// AT+SETTING=DEFCENTRAL
// this bluno attaches to Cyberman and sends the message along to the belt over bluetooth


void setup() {
  Serial.begin(115200);
}

void loop() {
  //sensorValue = analogRead(rotatorPin);
  //sensorValue = map(sensorValue, 0, 1023, 0, 255);
  //analogWrite(ledPin, sensorValue);
  //Serial.write(200);
  if (Serial.available()) {      // If anything comes in Serial (USB),
    int value = Serial.read();
    Serial.write(value);   // read it and send it out Serial1 (pins 0 & 1)
  }
  //delay(100 ); //can not be set as too fast, or the serial port would collapse
}
