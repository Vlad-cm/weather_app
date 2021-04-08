//YL-40 AD-DC Converter

#include "Arduino.h"
#include "PCF8591.h"
#define PCF8591_I2C_ADDRESS 0x48
String command;
long timetodelay = 2500;

PCF8591 pcf8591(PCF8591_I2C_ADDRESS);

void setup()
{
	Serial.begin(115200);
	pcf8591.begin();
}

void loop()
{ 
  pcf8591.analogWrite(255);
  if(Serial.available()){
        command = Serial.readStringUntil('\n');
        if (command.toInt() != 0) {
          timetodelay = command.toInt();  
        }
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
