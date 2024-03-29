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
const int dht_pin = 2;
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
  
    ////////////// DHT11 sensor for Humidity & Temperature
    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)

    // read from sensor (Celcius is the default)
    float humidity = dht.readHumidity();
    float temp = dht.readTemperature();

    // Check if any reads failed and exit if it did
    if (isnan(humidity) || isnan(temp)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }

    // Compute heat index in Celsius (isFahreheit = false)
    float heatindex = dht.computeHeatIndex(temp, humidity, false);

    // print to serial connection
    Serial.print(F("Humidity: "));
    Serial.print(humidity);
    Serial.println(F("%, "));
    Serial.print(F("Temperature: "));
    Serial.print(temp);
    Serial.println(F("°C, "));
    Serial.print(F("Heat index: "));
    Serial.print(heatindex);
    Serial.println(F("°C "));

    // flush the serial output
    Serial.flush();
  }
}
