/*
 This example prints the DHT data to serial connection (USB)
 */

///////////////////////////////////////////////////////////////////////////////////////////
// Libraries
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Humidity sensor
#include <DHT.h>

///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Humidity sensor
const dht_pin = 2;
DHT dht(dht_pin, DHT11, 15);

////////////// Delay
const long interval = 1000;
unsigned long previousMillis = 0;

///////////////////////////////////////////////////////////////////////////////////////////
// Set up
///////////////////////////////////////////////////////////////////////////////////////////
void setup() {

  //Initialize serial:
  Serial.begin(9600);

  ////////////// Humidity
  dht.begin();
  
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

    Serial.println();
      
    // save the last time a message was sent
    previousMillis = currentMillis;
  
    ////////////// Humidity
    // Reading temperature or humidity takes about 250 milliseconds!
    // print to serial connection
    publishDHT11();

  }

}

///////////////////////////////////////////////////////////////////////////////////////////
// Other functions
///////////////////////////////////////////////////////////////////////////////////////////

////////////// DHT11 sensor for Humidity & Temperature
void publishDHT11() {
  
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
  Serial.println(F("%, "));
  Serial.print(F("Temperature: "));
  Serial.print(temp);
  Serial.println(F("°C, "));
  Serial.print(F("Heat index: "));
  Serial.print(heatindex);
  Serial.println(F("°C "));

  // publishMQTT("bathroom/humidity", humidity);
  // publishMQTT("bathroom/temperature", temp);

}
