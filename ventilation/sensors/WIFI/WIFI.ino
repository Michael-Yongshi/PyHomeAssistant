/*
 This example connects to an unencrypted WiFi network.
 Then it prints the MAC address of the WiFi module,
 the IP address obtained, and other network details.
 */

///////////////////////////////////////////////////////////////////////////////////////////
// Libraries
///////////////////////////////////////////////////////////////////////////////////////////
////////////// Wifi
#include <SPI.h>
#include <WiFiNINA.h>

#include "wifi_secrets.h" 

////////////// Humidity sensor
#include <DHT.h>

///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Wifi
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the WiFi radio's status

////////////// Fan speed
int FanSpeed = 0;               // variable to store fan speed

////////////// Motion sensor
const int DIG_PIN_MOTION = 8;   // the pin that OUTPUT pin of sensor is connected to
int MotionStateCurrent   = LOW; // current state of pin
int MotionStatePrevious  = LOW; // previous state of pin

////////////// Humidity sensor
DHT dht(2, DHT11);

////////////// Led
int red_light_pin= 11;
int green_light_pin = 10;
int blue_light_pin = 9;

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
  
  ////////////// Wifi 
  // check the network connection:
  printCurrentNet();

  ////////////// Fan Speed
  // Get current fan speed
  // change led accordingly
  determineLedChange();
  
  ////////////// Humidity
  // Reading temperature or humidity takes about 250 milliseconds!
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

  ////////////// Motion
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
  
  ////////////// delay for a second before running again
  delay(2000);

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

////////////// Humidity

////////////// Motion
