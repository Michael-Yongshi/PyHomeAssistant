/*
 *  Simple HTTP get webclient test
 */

///////////////////////////////////////////////////////////////////////////////////////////
// Libraries
///////////////////////////////////////////////////////////////////////////////////////////
////////////// Secrets
#include "secrets.h" 

////////////// Wifi
#include <ESP8266WiFi.h>

///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Wifi
//const char ssid[] = SECRET_WIFI_SSID;        // your network SSID (name)
//const char pass[] = SECRET_WIFI_PASS;    // your network password (use for WPA, or use as key for WEP)

const char* ssid     = SECRET_WIFI_SSID;
const char* password = SECRET_WIFI_PASS;

const char* host = "wifitest.adafruit.com";



void setup() {

  // pin for onboard led
  pinMode(0, OUTPUT);

  //start serial connection
  Serial.begin(115200);
  delay(100);

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// set addition values
int value = 0;

// loop
void loop() {

  // give a delay to avoid spamming
  ++value;

  // blink the led
  Serial.print("blinking...\n");
  digitalWrite(0, LOW);
  delay(5000);
  digitalWrite(0, HIGH);

  // print wifi details
  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 80;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }
  
  // We now create a URI for the request
  String url = "/testwifi/index.html";
  Serial.print("Requesting URL: ");
  Serial.println(url);
  
  // This will send the request to the server
  client.print(String("GET ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" + 
               "Connection: close\r\n\r\n");
  delay(500);
  
  // Read all the lines of the reply from server and print them to Serial
  while(client.available()){
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }
  
  Serial.println();
  Serial.println("closing connection");
}
