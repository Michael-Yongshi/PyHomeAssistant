/*
 This example connects to an unencrypted WiFi network.
 Then it prints the MAC address of the WiFi module,
 the IP address obtained, and other network details.
 */

///////////////////////////////////////////////////////////////////////////////////////////
// Libraries
///////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////
// Parameters
///////////////////////////////////////////////////////////////////////////////////////////

////////////// Motion sensor
const int DIG_PIN_MOTION = 8;   // the pin that OUTPUT pin of sensor is connected to
int MotionStateCurrent   = LOW; // current state of pin
int MotionStatePrevious  = LOW; // previous state of pin

////////////// Light
const int light_pin = 11;

////////////// Delay
const long interval = 900000; // (15 minutes x 60 = 900 seconds = 900 000 milliseconds)
unsigned long previousMillis = 0;

///////////////////////////////////////////////////////////////////////////////////////////
// Set up
///////////////////////////////////////////////////////////////////////////////////////////
void setup() {

  //Initialize serial:
  Serial.begin(9600);
   
  ////////////// Motion
  pinMode(DIG_PIN_MOTION, INPUT);

  ////////////// Light
  pinMode(light_pin, OUTPUT);

}

///////////////////////////////////////////////////////////////////////////////////////////
// Loop
///////////////////////////////////////////////////////////////////////////////////////////
void loop() {
    
  ////////////// Motion
  MotionStatePrevious = MotionStateCurrent; // store old state
  MotionStateCurrent = digitalRead(DIG_PIN_MOTION);   // read new state
  Serial.println("MotionStateCurrent: ");
  Serial.println(MotionStateCurrent);
  
  // set current time
  unsigned long currentMillis = millis();

  // If movement is detected
  if (MotionStatePrevious == LOW && MotionStateCurrent == HIGH) {

    Serial.println("Motion detected!");
    Serial.println();

    // turn on light
    digitalWrite(light_pin, HIGH); // Turns ON light

    // register when the light was last turned on
    previousMillis = currentMillis;

  }

  ////////////// Delay
  // avoid having delays in loop, we'll use the strategy from BlinkWithoutDelay
  // see: File -> Examples -> 02.Digital -> BlinkWithoutDelay for more info

  // if last registered motion was longer ago then the interval
  if (currentMillis - previousMillis >= interval) {

    digitalWrite(light_pin, LOW); // Turns OFF light

  }

}

///////////////////////////////////////////////////////////////////////////////////////////
// Other functions
///////////////////////////////////////////////////////////////////////////////////////////