/*
 This example connects to an unencrypted WiFi network.
 Then it prints the MAC address of the WiFi module,
 the IP address obtained, and other network details.
 */

///////////////////////////////////////////////////////////////////////////////////////////
// Libraries
///////////////////////////////////////////////////////////////////////////////////////////
#include "secrets.h" 

////////////// Wifi
#include <SPI.h>
#include <WiFiNINA.h>

////////////// MQTT
#include <ArduinoMqttClient.h>

////////////// Humidity sensor
#include <DHT.h>

///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Wifi
const char ssid[] = SECRET_WIFI_SSID;        // your network SSID (name)
const char pass[] = SECRET_WIFI_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the WiFi radio's status

////////////// MQTT
const char mqtt_broker[] = SECRET_MQTT_BROKER;
const int port = 1883;

const char mqtt_user[] = SECRET_MQTT_USER;
const char mqtt_password[] = SECRET_MQTT_PASS;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

////////////// Fan speed
int FanSpeed = 0;               // variable to store fan speed

////////////// Motion sensor
const int DIG_PIN_MOTION = 8;   // the pin that OUTPUT pin of sensor is connected to
int MotionStateCurrent   = LOW; // current state of pin
int MotionStatePrevious  = LOW; // previous state of pin

////////////// Humidity sensor
DHT dht(2, DHT11);

////////////// Led
const int red_light_pin= 11;
const int green_light_pin = 10;
const int blue_light_pin = 9;

////////////// Delay
const long interval = 1000;
unsigned long previousMillis = 0;


///////////////////////////////////////////////////////////////////////////////////////////
// Set up
///////////////////////////////////////////////////////////////////////////////////////////
void setup() {

  //Initialize serial:
  Serial.begin(9600);

  ////////////// Wifi 
  // wait for port to open:
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // set hostname
  WiFi.setHostname("ard-bath");
  
  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.print("You're connected to the network");
  printCurrentNet();
  printWifiData();

  ////////////// MQTT

  mqttClient.setId("Bathroom-Arduino");
  mqttClient.setUsernamePassword(mqtt_user, mqtt_password);

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(mqtt_broker);

  if (!mqttClient.connect(mqtt_broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  ////////////// Fan speed
  // FanSpeed = result get fan speed
  
  ////////////// Led
  pinMode(red_light_pin, OUTPUT);
  pinMode(green_light_pin, OUTPUT);
  pinMode(blue_light_pin, OUTPUT);

  ////////////// Humidity
  dht.begin();
  
  ////////////// Motion
  pinMode(DIG_PIN_MOTION, INPUT); // set arduino pin to input mode to read value from OUTPUT pin of sensor

}

///////////////////////////////////////////////////////////////////////////////////////////
// Loop
///////////////////////////////////////////////////////////////////////////////////////////
void loop() {
  
  ////////////// Delay
  // avoid having delays in loop, we'll use the strategy from BlinkWithoutDelay
  // see: File -> Examples -> 02.Digital -> BlinkWithoutDelay for more info
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;


    ////////////// Wifi 
    // check the network connection:
    printCurrentNet();
  
    ////////////// MQTT
    // call poll() regularly to allow the library to send MQTT keep alives which
    // avoids being disconnected by the broker
    mqttClient.poll();

    ////////////// Fan Speed
    // Get current fan speed
    // change led accordingly
    determineLedChange();
  
    ////////////// Motion
    readMotion();

    ////////////// Humidity
    // Reading temperature or humidity takes about 250 milliseconds!
    readDHT11();

  }

}

///////////////////////////////////////////////////////////////////////////////////////////
// Other functions
///////////////////////////////////////////////////////////////////////////////////////////
////////////// Wifi 
void printWifiData() {
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  Serial.println(ip);

  // print your MAC address:
  byte mac[6];
  WiFi.macAddress(mac);
  Serial.print("MAC address: ");
  printMacAddress(mac);
}

void printCurrentNet() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:
  byte bssid[6];
  WiFi.BSSID(bssid);
  Serial.print("BSSID: ");
  printMacAddress(bssid);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

  // print the encryption type:
  byte encryption = WiFi.encryptionType();
  Serial.print("Encryption Type:");
  Serial.println(encryption, HEX);
  Serial.println();
}

void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}

//// void postString(String EventType, String PostData) {
//void Post(String PostData) {
//
//  String MqttTopic = "Humidity";
//
//  IPAddress server(192,168,178,37);
//  int port = 8123;
//
//  if (client.connect(server, port)) {
//    client.println("POST /api/states/" + EventType + " HTTP/1.1");
//    client.println("Host: 192.168.178.37");
//    // client.println("User-Agent: Arduino/1.0");
//    // client.println("Connection: close");
//    client.print("Content-Length: ");
//    client.println(PostData.length());
//    client.println();
//    client.println(PostData);
//  }
//}

void publishMQTT(String topic, float data) {
    Serial.print("Sending message to topic: ");
    Serial.println(topic);
    Serial.println(data);

    // send message, the Print interface can be used to set the message contents
    mqttClient.beginMessage(topic);
    mqttClient.print(data);
    mqttClient.endMessage();

    Serial.println();
}

////////////// Led based on Fan speed
void determineLedChange() {
  
  if (FanSpeed == 0) {
    Serial.println("Fan is currently offline!");
    RGB_color(0, 0, 0); // Off
  }
  else
  if (FanSpeed == 1) {
    Serial.println("Fan is currently on speed 1!");
    RGB_color(255, 255, 255); // Lightblue
  }
  else
  if (FanSpeed == 2) {
    Serial.println("Fan is currently on speed 2!");
    RGB_color(255, 0, 255); // Purple
  }
  else
  if (FanSpeed == 3) {
    Serial.println("Fan is currently on speed 3!");
    RGB_color(255, 0, 0); // Red
  }
}

////////////// increment Fan speed
void incrementFanSpeed() {

  FanSpeed = ++FanSpeed;
  if (FanSpeed >= 4) {
    Serial.println("Fan speed exceeded 3! Returning to 1!");
    FanSpeed = 1;
  }
}

////////////// LED
void RGB_color(int red_light_value, int green_light_value, int blue_light_value)
 {
  analogWrite(red_light_pin, red_light_value);
  analogWrite(green_light_pin, green_light_value);
  analogWrite(blue_light_pin, blue_light_value);
}

////////////// Motion
void readMotion() {

  MotionStatePrevious = MotionStateCurrent; // store old state
  MotionStateCurrent = digitalRead(DIG_PIN_MOTION);   // read new state
  Serial.println("MotionStateCurrent: ");
  Serial.println(MotionStateCurrent);
  
  // If movement is detected, up fan speed and immediately show led change
  if (MotionStatePrevious == LOW && MotionStateCurrent == HIGH) {
    incrementFanSpeed();
    Serial.println("Motion detected! Fanspeed changed to ");
    Serial.println(FanSpeed);
    determineLedChange();
  }
}

////////////// Humidity & Temperature
void readDHT11() {
  
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float humidity = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float temp = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temp)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Celsius (isFahreheit = false)
  float heatindex = dht.computeHeatIndex(temp, humidity, false);

  Serial.print(F("Humidity: "));
  Serial.print(humidity);
  Serial.print(F("%, "));
  Serial.print(F("Temperature: "));
  Serial.print(temp);
  Serial.print(F("°C, "));
  Serial.print(F("Heat index: "));
  Serial.print(heatindex);
  Serial.print(F("°C "));

  publishMQTT("bathroom/humidity", humidity);
  publishMQTT("bathroom/temperature", temp);

}
