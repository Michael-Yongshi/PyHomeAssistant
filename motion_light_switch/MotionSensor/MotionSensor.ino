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
const int motion_pin = 8;   // the pin that OUTPUT pin of sensor is connected to
int MotionStateCurrent   = LOW; // current state of pin
int MotionStatePrevious  = LOW; // previous state of pin

////////////// Relay
const int relay_pin = 4;

////////////// Delay
const long interval = 60000; // (15 minutes x 60 = 900 seconds, x 1000 = 900 000 milliseconds)
unsigned long previousMillis = 0;

///////////////////////////////////////////////////////////////////////////////////////////
// Set up
///////////////////////////////////////////////////////////////////////////////////////////
void setup() {

  //Initialize serial:
  Serial.begin(9600);
   
  ////////////// Motion
  pinMode(motion_pin, INPUT);

  ////////////// Relay
  pinMode(relay_pin, OUTPUT);

}

///////////////////////////////////////////////////////////////////////////////////////////
// Loop
///////////////////////////////////////////////////////////////////////////////////////////
void loop() {
    
  ////////////// Motion
  MotionStatePrevious = MotionStateCurrent; // store old state
  MotionStateCurrent = digitalRead(motion_pin);   // read new state
  Serial.println("MotionStateCurrent: ");
  Serial.println(MotionStateCurrent);
  
  // set current time
  unsigned long currentMillis = millis();

  // If movement is detected
  if (MotionStatePrevious == LOW && MotionStateCurrent == HIGH) {

    Serial.println("Motion detected!");

    // turn on light
    digitalWrite(relay_pin, HIGH); // Turns ON light

    // register when the light was last turned on
    previousMillis = currentMillis;

  }

  ////////////// Delay
  // avoid having delays in loop, we'll use the strategy from BlinkWithoutDelay
  // see: File -> Examples -> 02.Digital -> BlinkWithoutDelay for more info

  // set timer
  unsigned long differenceMillis = millis();
  differenceMillis = currentMillis - previousMillis;
  
  Serial.print("Current time: ");
  Serial.println(currentMillis);
  Serial.print("Previous time: ");
  Serial.println(previousMillis);
  Serial.print("Timer: ");
  Serial.println(differenceMillis);
  
  // if last registered motion was longer ago then the interval
  if (differenceMillis >= interval) {

    digitalWrite(relay_pin, LOW); // Turns OFF light

  }

}

///////////////////////////////////////////////////////////////////////////////////////////
// Other functions
///////////////////////////////////////////////////////////////////////////////////////////
