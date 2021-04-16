//YL-40 AD-DC Converter

#include "Arduino.h"
#include "PCF8591.h"
#define PCF8591_I2C_ADDRESS 0x48
long timetodelay = 2500;
String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete

PCF8591 pcf8591(PCF8591_I2C_ADDRESS);

void setup()
{
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
	Serial.begin(115200);
	pcf8591.begin();
}

void loop()
{  
  pcf8591.analogWrite(255);
  if (stringComplete) {
    if (inputString.toInt() != 0) {
      timetodelay = inputString.toInt();  
    } else {
      if (inputString.equals("light_on")){
        digitalWrite(13, HIGH);
      } else if (inputString.equals("light_off")){
        digitalWrite(13, LOW);
      }
    }    
    inputString = "";
    stringComplete = false;
  }

	PCF8591::AnalogInput ai = pcf8591.analogReadAll();
  double a = ai.ain1;
  double r6 = (1000 * a)/(256 - a);
  double c = r6/5150;
  double temp = (1 / (0.003354016 + (0.000253165)*log(c))) - 273.15;
	Serial.print("temp:");  
  Serial.print(temp);
	Serial.print(" bright:");
	Serial.println(ai.ain0);
  delay(500);
  pcf8591.analogWrite(0);
  delay(timetodelay);
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar != '\n' && inChar != '\r') {
      inputString += inChar;
    }
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
