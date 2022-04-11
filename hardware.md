
# Tooling
soldering with pinecel
https://www.youtube.com/watch?v=-u_o-yNjpzs&t=3s

# Floor pump
want a manual trigger for floor pump activation on

# Shelly stuff
shelly plug: https://shop.shelly.cloud/shelly-plug-wifi-smart-home-automation#71
shelly bathroom vent controls: https://shop.shelly.cloud/shelly-plus-i4-plus-shelly-wall-switch-4-wifi-smart-home-automation
shelly radiator: https://shelly.cloud/shelly-thermostatic-radiator-valve/
shelly button: https://shop.shelly.cloud/shelly-button-wifi-smart-home-automation#64

# Doorbell aux arduino
music aux addition: https://www.adafruit.com/product/3357
headers to be soldered on addition: https://opencircuit.nl/product/Short-Headers-Kit-Feather-12-pins-Meer-16-pins

# Local doorbell with optional automation

## local doorbell soundboard
adafruit soundboard: https://www.adafruit.com/product/2220
set up and insert audio, just add some music files and connect doorbell to appropriate pin for simple local functionality

## smart addition featherboard
adafruit esp: https://opencircuit.nl/product/Geassembleerde-Adafruit-Feather-HUZZAH-ESP8266
to capture the doorbell press and send it to home assistant
But this part can probably be done by an existing rpi as well, although a dedicated device may be more stable...

## combine featherboard with featherwing
feather sound: https://www.adafruit.com/product/3357
This to combine local and smart in a single device