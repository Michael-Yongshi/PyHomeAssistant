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

////////////// MQTT
#include <PubSubClient.h>

///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Wifi
const char* ssid     = SECRET_WIFI_SSID;
const char* password = SECRET_WIFI_PASS;
const char* host = "wifitest.adafruit.com";

////////////// MQTT
const char mqtt_broker[] = SECRET_MQTT_BROKER;
const int mqtt_port = 1883;

const char mqtt_user[] = SECRET_MQTT_USER;
const char mqtt_password[] = SECRET_MQTT_PASS;

const char outTopicDoorbell[] = "doorbell/status";

////////////// Pins
const int buttonPin= 4;
const int outPin= 0;

////////////// Delay
const int WAIT_TIME= 5000;

////////////// Global attributes
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

bool buttonPressed = false;
unsigned long lastTrigger = millis();

///////////////////////////////////////////////////////////////////////////////////////////
// Set up
///////////////////////////////////////////////////////////////////////////////////////////
void setup() {

  //start serial connection
  Serial.begin(115200);
  delay(100);

  ////////////// Wifi

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

  ////////////// MQTT
  mqttClient.setServer(mqtt_broker, mqtt_port);
  mqttClient.connect("Adafruit_Doorbell", mqtt_user, mqtt_password);

  if (mqttClient.connected()) {
    Serial.println("MQTT connection established!");
  }
  else {
    Serial.println("MQTT connection failed! Error code = ");
  }

  ////////////// Pins
  // Pin for button
  pinMode(buttonPin, INPUT_PULLUP); // pullup if you have a GPIO - button - GND set up. This sets the GPIO pin to high
  // pin for onboard led
  pinMode(outPin, OUTPUT);

  // set onboard led to off
  digitalWrite(outPin, HIGH);

}


///////////////////////////////////////////////////////////////////////////////////////////
// Loop
///////////////////////////////////////////////////////////////////////////////////////////
void loop() {

  // light led for 5 sec if button is pressed

  if (!buttonPressed && digitalRead(buttonPin) == LOW) // button is pressed when its grounded low in a GPIO - button - GND set up
  {
    Serial.println("Button pressed...\n");
    boolean rc = mqttClient.publish(outTopicDoorbell, "Ringing");
    digitalWrite(outPin, LOW);
    buttonPressed = true;

    lastTrigger = millis();
  }

  if (buttonPressed && lastTrigger + WAIT_TIME < millis()){
    boolean rc = mqttClient.publish(outTopicDoorbell, "Waiting");
    digitalWrite(outPin, HIGH);
    buttonPressed = false;
  }

}
