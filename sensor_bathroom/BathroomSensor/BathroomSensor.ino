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

////////////// Motion sensor
const int DIG_PIN_MOTION = 8;   // the pin that OUTPUT pin of sensor is connected to
int MotionStateCurrent   = LOW; // current state of pin
int MotionStatePrevious  = LOW; // previous state of pin

////////////// Humidity sensor
DHT dht(2, DHT11);

////////////// Fan speed
int FanSpeed = 0;               // variable to store fan speed

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

  ////////////// Humidity
  dht.begin();
  
  ////////////// Led
  pinMode(red_light_pin, OUTPUT);
  pinMode(green_light_pin, OUTPUT);
  pinMode(blue_light_pin, OUTPUT);


  
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

    ////////////// Change LED
    changeLed();
  
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

////////////// RGB Led based on Fan speed
void changeLed() {
  
  if (FanSpeed == 0) {
    Serial.println("Fan is currently offline!");

    // set light off
    analogWrite(red_light_pin, 0);
    analogWrite(green_light_pin, 0);
    analogWrite(blue_light_pin, 0);
  }

  else
  if (FanSpeed == 1) {
    Serial.println("Fan is currently on speed 1!");

    // set lightblue / white
    analogWrite(red_light_pin, 255);
    analogWrite(green_light_pin, 255);
    analogWrite(blue_light_pin, 255);
  }

  else
  if (FanSpeed == 2) {
    Serial.println("Fan is currently on speed 2!");

    // set purple
    analogWrite(red_light_pin, 255);
    analogWrite(green_light_pin, 0);
    analogWrite(blue_light_pin, 255);
  }

  else
  if (FanSpeed == 3) {
    Serial.println("Fan is currently on speed 3!");

    // set red
    analogWrite(red_light_pin, 255);
    analogWrite(green_light_pin, 0);
    analogWrite(blue_light_pin, 0);
  }
}

////////////// DHT11 sensor for Humidity & Temperature
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
