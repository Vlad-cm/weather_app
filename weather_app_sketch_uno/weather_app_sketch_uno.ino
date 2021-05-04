#include <ArduinoJson.h>

#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

long timetodelay = 5000;
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

#define AVG_SIZE 300
float temperatureAvg;
float humidityAvg;
float hicAvg;

int i = 0;

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
      float temperature = dht.readTemperature();
      float humidity = dht.readHumidity();
      if (isnan(humidity) || isnan(temperature)) {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
      }
      float hic = dht.computeHeatIndex(temperature, humidity, false);
    
      String output;
      StaticJsonDocument<96> doc;
      doc["action"] = "weather_data";

      JsonObject data = doc.createNestedObject("data");
      data["temperature"] = formatFloat(temperature);
      data["humidity"] = formatFloat(humidity);
      data["heatindex"] = formatFloat(hic);
      data["code"] = "200";
      serializeJson(doc, output);
      
      Serial.println(output);
    
      temperatureAvg += temperature;
      humidityAvg += humidity;
      hicAvg += hic;

      i += 1;
      if (i >= AVG_SIZE) {
        String output;
        StaticJsonDocument<96> doc;
        doc["action"] = "weather_data_avg";
        JsonObject data = doc.createNestedObject("data");
        data["temperature"] = formatFloat(temperatureAvg / AVG_SIZE);
        data["humidity"] = formatFloat(humidityAvg / AVG_SIZE);
        data["heatindex"] = formatFloat(hicAvg / AVG_SIZE);
        data["code"] = "200";
        serializeJson(doc, output);
        Serial.println(output);
        temperatureAvg = 0;
        humidityAvg = 0;
        hicAvg = 0;
        i = 0;
      }
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

String formatFloat(float f_val) {
  static char outstr[7];
  dtostrf(f_val, 5, 2, outstr);
  return String(outstr);
}
