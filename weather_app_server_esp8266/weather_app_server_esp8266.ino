
#if !defined(ESP8266)
#error This code is intended to run only on the ESP8266 boards ! Please check your Tools->Board setting.
#endif

#define _WEBSOCKETS_LOGLEVEL_     1
#include <WebSocketsClient_Generic.h>
#include "DHTesp.h"
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

long timeToDelaySendData = 5000;
unsigned long timing_one;
const int relay = D5;
const int touchSensor = D6;
bool touchState = false;

const char* ssid = "your_ssid";
const char* password = "your_password";

DHTesp dht;
ESP8266WebServer server(80);
WebSocketsClient webSocket;

#define USE_SSL true

#define WS_SERVER "wbskt.weather.oncook.top"

#if USE_SSL
#define WS_PORT 443
#else
#define WS_PORT 80
#endif

bool alreadyConnected = false;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length)
{
  switch (type)
  {
    case WStype_DISCONNECTED:
      if (alreadyConnected)
      {
        Serial.println("[WSc] Disconnected!");
        alreadyConnected = false;
      }

      break;
    case WStype_CONNECTED:
      {
        alreadyConnected = true;
        Serial.print("[WSc] Connected to url: ");
        Serial.println((char *) payload);
      }
      break;
    case WStype_TEXT:
    {
      StaticJsonDocument<128> doc;
      DeserializationError error = deserializeJson(doc, payload);
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }
      if (doc["type"] == "lampstate") {
        if (doc["lamp_on"]) {
          digitalWrite(relay, HIGH);
        } else {
          digitalWrite(relay, LOW);
        }
      }
    }
    break;
    case WStype_BIN:
      break;
    case WStype_PING:
      break;
    case WStype_PONG:
      break;
    case WStype_ERROR:
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
      break;
    default:
      break;
  }
}

void handleRoot() {
  server.send(200, "text/html", "<!DOCTYPE html><html lang=\"en\"><head><title>esp8266</title></head><body><p>use <b>server.name/setdelay?delay=\"you_delay\"</b> for set a delay for sending temperature data</p></body></html>");
}

void handleNotFound() {
  String output = "";
  StaticJsonDocument<192> doc;
  doc["message"] = "File Not Found";
  doc["URI"] = server.uri();
  doc["method"] = (server.method() == HTTP_GET) ? "GET" : "POST";
  JsonObject arguments = doc.createNestedObject("arguments");
  arguments["count"] = server.args();
  for (uint8_t i = 0; i < server.args(); i++) {
    arguments[server.argName(i)] = server.arg(i);
  }
  doc["code"] = 404;
  serializeJson(doc, output);
  server.send(404, "application/json", output);
}

void setDelay() {
  String output;
  StaticJsonDocument<128> doc;
  if (server.arg("delay") == "") {
    doc["message"] = "Delay not specified!";
    doc["value"]  = "none";
    doc["code"] = "400";
  } else {
    doc["message"] = "Set a delay for sending temperature data.";
    doc["value"] = server.arg("delay");
    doc["code"] = "200";
    timeToDelaySendData = server.arg("delay").toInt();
  }
  serializeJson(doc, output);
  server.send(200, "application/json", output);
}


void setup(void) {
  pinMode(relay, OUTPUT);
  digitalWrite(relay, LOW);
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }

  server.on("/", handleRoot);
  server.on("/setdelay", setDelay);
  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("HTTP server started");

  #if USE_SSL
  webSocket.beginSSL(WS_SERVER, WS_PORT);
  #else
  webSocket.begin(WS_SERVER, WS_PORT, "/");
  #endif

  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  webSocket.enableHeartbeat(15000, 3000, 2);
  Serial.print("Connected to WebSockets Server @ IP address: ");
  Serial.println(WS_SERVER);
 
  dht.setup(4, DHTesp::DHT11); //D2 pin
}

#define AVG_SIZE 300
float temperatureAvg;
float humidityAvg;
float hicAvg;

int i = 0;

void loop(void) {
  webSocket.loop();
  server.handleClient();
  MDNS.update();
  if (millis() - timing_one > timeToDelaySendData){
    timing_one = millis();
    float humidity = dht.getHumidity();
    float temperature = dht.getTemperature();
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }
    float hic = dht.computeHeatIndex(temperature, humidity, false);
    sendWeatherData("weather_data", formatFloat(temperature), formatFloat(humidity),formatFloat(hic));
    temperatureAvg += temperature;
    humidityAvg += humidity;
    hicAvg += hic;
    
    i++;
    if (i >= AVG_SIZE) {
      sendWeatherData("weather_data_avg", formatFloat(temperatureAvg/AVG_SIZE), formatFloat(humidityAvg/AVG_SIZE), formatFloat(hicAvg/AVG_SIZE));
      temperatureAvg = 0;
      humidityAvg = 0;
      hicAvg = 0;
      i = 0;
    }
  }

  if (digitalRead(touchSensor) == HIGH && !touchState){
    touchState = !touchState;
    digitalWrite(relay, HIGH);
    sendLampState(true);
  } else if (digitalRead(touchSensor) == LOW && touchState) {
    touchState = !touchState;
    digitalWrite(relay, LOW);
    sendLampState(false);
  }
}

void sendWeatherData(String action, String temperature, String humidity, String heatindex) { 
  String output;
  StaticJsonDocument<144> doc;
  doc["action"] = action;
  JsonObject data = doc.createNestedObject("data");
  data["temperature"] = temperature;
  data["humidity"] = humidity;
  data["heatindex"] = heatindex;
  data["code"] = "200";
  serializeJson(doc, output);       
  webSocket.sendTXT(output);
}

void sendLampState(bool state) {
  String output;
  StaticJsonDocument<64> doc;
  doc["action"] = "lampstate";
  doc["lamp_on"] = state;
  serializeJson(doc, output);  
  webSocket.sendTXT(output);    
}

String formatFloat(float f_val) {
  static char outstr[7];
  dtostrf(f_val, 5, 2, outstr);
  return String(outstr);
}