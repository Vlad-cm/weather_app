#include <ArduinoJson.h>

#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

long timetodelay = 2500;
unsigned long timing;
String inputString = "";
boolean stringComplete = false;

void setup()
{
    pinMode(13, OUTPUT);
    digitalWrite(13, LOW);
    Serial.begin(115200);
    dht.begin();
}

void loop()
{  
    if (stringComplete) {
        if (inputString.toInt() != 0) {
        timetodelay = inputString.toInt();
        } else {
            if (inputString.equals("light_on")) {
                digitalWrite(13, HIGH);
            } else if (inputString.equals("light_off")) {
                digitalWrite(13, LOW);
            }
        }
        inputString = "";
        stringComplete = false;
    }
    if (millis() - timing > timetodelay){
      timing = millis(); 
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();
      if (isnan(humidity) || isnan(temperature)) {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
      }
      float hic = dht.computeHeatIndex(temperature, humidity, false);
      String output;
      StaticJsonDocument<48> doc;
      doc["humidity"] = humidity;
      doc["temperature"] = temperature;
      doc["heatindex"] = hic;
      doc["code"] = "200";
      serializeJson(doc, output);
      Serial.println(output);
    };
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
