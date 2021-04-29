#include "DHTesp.h"
DHTesp dht;
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#define STASSID "your_ssid"
#define STAPSK  "your_password"

long timeToDelaySendData = 2500;
long timeToDelayGetState = 1000;
unsigned long timing_one;
unsigned long timing_two;
const int relay = D2;
bool previousState = false;
const char* ssid = STASSID;
const char* password = STAPSK;

ESP8266WebServer server(80);

const char* host = "vlad-weather-application.herokuapp.com";
const int httpsPort = 443;

const char fingerprint[] PROGMEM = "94 FC F6 23 6C 37 D5 E7 92 78 3C 0B 5F AD 0C E4 9E FD 9E A8";

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

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

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
  dht.setup(0, DHTesp::DHT11);
}

void loop(void) {
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

    sendData(temperature, humidity, hic);

    String output;
    StaticJsonDocument<96> doc;
    doc["humidity"] = humidity;
    doc["temperature"] = temperature;
    doc["heatindex"] = hic;
    doc["code"] = "200";
    serializeJson(doc, output);
    Serial.println(output);
  }

  if (millis() - timing_two > timeToDelayGetState){
    timing_two = millis();
    bool state = getLampState();
    if (state != previousState){
      previousState = state;
      if (state) {
        digitalWrite(relay, HIGH);
        Serial.println("Lamp on!");
      } else {
        digitalWrite(relay, LOW);
        Serial.println("Lamp off!");
      }
    }
  }
}

void sendData(double temperature, double humidity, double heatIndex){
  WiFiClientSecure client;
  client.setFingerprint(fingerprint);
  if (!client.connect(host, httpsPort)) {
    return;
  }
  String url = url + "/send-data?temp=" + temperature + "&humidity=" + humidity + "&heatindex=" + heatIndex;
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "User-Agent: Arduino WiFi Shield\r\n" +
               "Connection: close\r\n\r\n");
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      break;
    }
  }
}

bool getLampState() {
  WiFiClientSecure client;
  client.setFingerprint(fingerprint);
  if (!client.connect(host, httpsPort)) {
    return "Connection error!";
  }
  String url = url + "/lamp-state";
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "User-Agent: Arduino WiFi Shield\r\n" +
               "Connection: close\r\n\r\n");
  String line = "";
  while (client.connected()) {
    line = client.readStringUntil('\n');
    if (line.equals("{")) {
      break;
    }
  }

  StaticJsonDocument<64> doc;
  String input = line + client.readStringUntil('}') + '}';
  DeserializationError error = deserializeJson(doc, input);
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return previousState;
  }

  bool lamp_on = doc["lamp_on"];
  int code = doc["code"];
  if (code == 200) {
    return lamp_on;
  } else {
    return previousState;
  }
}