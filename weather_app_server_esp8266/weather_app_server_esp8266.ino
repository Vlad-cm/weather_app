#include "Arduino.h"
#include "PCF8591.h"
#define PCF8591_I2C_ADDRESS 0x48

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#ifndef STASSID
#define STASSID "you_ssid"
#define STAPSK  "you_password"
#endif

//=========ADC==========
long timeToDelaySendData = 2500;
long timeToDelayGetState = 1000;
bool greenDiode = false;
unsigned long timing_one;
unsigned long timing_two;
const int relay = D2;

PCF8591 pcf8591(PCF8591_I2C_ADDRESS);
//======================
String previousState = "False";

const char* ssid = STASSID;
const char* password = STAPSK;

ESP8266WebServer server(80);

//======================
const char* host = "vlad-weather-application.herokuapp.com";
const int httpsPort = 443;

// Use web browser to view and copy
// SHA1 fingerprint of the certificate
const char fingerprint[] PROGMEM = "94 FC F6 23 6C 37 D5 E7 92 78 3C 0B 5F AD 0C E4 9E FD 9E A8";
//======================

void handleRoot() {
  server.send(200, "text/plain", "use setdelay?delay=\"you_delay\" for set a delay for sending temperature data");
}

void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}

void setDelay() { 
  String message = "";
  if (server.arg("delay") == "") {
    message = "{\n    \"message\": \"Delay not specified!\",\n    \"code\": 404\n}";
  } else {
    message = "{\n    \"message\": \"set a delay for sending temperature data\",\n    \"value\": ";
    message += server.arg("delay");
    message += ",\n    \"code\": 200\n}";
    
    timeToDelaySendData = server.arg("delay").toInt();
  }
  server.send(200, "text/plain", message);
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
  pcf8591.begin();
}

void loop(void) {
  server.handleClient();
  MDNS.update();
  if (millis() - timing_one > timeToDelaySendData){
    blink();
    timing_one = millis(); 
    double a = pcf8591.analogRead(AIN1);
    double temp = (1 / (0.003354016 + (0.000253165)*log((1000 * a)/(256 - a)/5150))) - 273.15;
    int bright = pcf8591.analogRead(AIN0);
    sendData(temp, bright);
    Serial.print("temp:");  
    Serial.print(temp);
    Serial.print(" bright:");
    Serial.println(bright);   
  }
  
  if (millis() - timing_two > timeToDelayGetState){
    timing_two = millis();
    String state = getLampState();
    state.trim();
    if (!state.equals(previousState)){
      previousState = state;
      if (state.equals("True")) {
        digitalWrite(relay, HIGH);
        Serial.println("Lamp on!");
      } else {
        digitalWrite(relay, LOW);
        Serial.println("Lamp off!");
      }        
    }
  }
}

void blink(){
   if (greenDiode) {
      pcf8591.analogWrite(0);
      greenDiode = false;
   } else {
      pcf8591.analogWrite(255);
      greenDiode = true;
   }
}

void sendData(double temp, int bright){
  WiFiClientSecure client;
  client.setFingerprint(fingerprint);
  if (!client.connect(host, httpsPort)) {
    return;
  }
  String url = url + "/send-data?temp=" + temp + "&bright=" + bright;
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

String getLampState() {
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
  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") {
      break;
    }
  }
  client.readStringUntil('\n');
  return client.readStringUntil('\n');
}
