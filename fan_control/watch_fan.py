import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

class WatchFan(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - Post to api of fan-pi to switch on ventilator with speed x
    
    Test this class by firing a test event
    -> hass web ui -> developer tools -> events -> type "FAN_OVERRIDE -> fire event

    add data like below and replace x with 0 - 3 (0 means stop override)
    {'speed': x}
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # Were keeping track of an override variable to keep override only on for a certain amount of time
        self.override = datetime.datetime.now() + datetime.timedelta(minutes=-30)

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_state(self.fan_override, "input_number.fan_override")
        self.listen_state(self.humidity, "sensor.mqtt_bathroom_humidity")

    # the method that is called when someone wants to override fan setting from home assistant itself
    def fan_override(self, entity, attribute, old, new, kwargs):

        # remember last time override has been used
        self.override = datetime.datetime.now()

        # convert the state to a valid integer
        speed = int(new.split('.', 1)[0])
        
        # send fan command to set the speed to the new level
        self.post_fan_speed(speed)

        # log
        self.log(f"Someone requested fan override, setting speed {old} => {new}! \nCurrent date and time is: {self.override}\n")

    def humidity(self, entity, attribute, old, new, kwargs):

        # log humidity level
        self.log(f"Measured humidity at {new}%!\n")
        humidity_new = int(new.split('.', 1)[0])

        # get fanspeed state
        speed = int(self.get_state("sensor.mqtt_fan_speed"))
        self.log(f"Fan speed is {speed}")

        # timings
        override_expiration = self.override + datetime.timedelta(minutes=15)
        current_time = datetime.datetime.now()
        self.log(f"Override expires at {override_expiration}\n")
        self.log(f"Current date and time is: {current_time}")

        # automatically adjust fan speed based on sensor data, humidity and smoke
        if override_expiration <= current_time:
            self.log(f"Override expired")

            # set to 3 if increased to above 80 from below 80 (2)
            if humidity_new >= 80 and speed != 3:
                self.post_fan_speed(3)
                self.log(f"level above 80%  observed, set fan to speed 3")

            # set to 2 if humidity_new is between 60 - 80 (2) and humidity_old was below 60 (1) or above 80 (3)
            elif (humidity_new >= 60 and humidity_new < 80) and speed != 2:
                self.post_fan_speed(2)
                self.log(f"level between 60% and 80% observed, set fan to speed 2")

            # set to 1 if new dropped below 60 (1) while humidity_old was higher than 60 (2 or 3) 
            elif humidity_new < 60 and speed != 1:
                self.post_fan_speed(1)
                self.log(f"level below 60% observed, set fan to speed 1")

    def get_fan_speed(self):

        # address for the rest api
        url = "http://192.168.178.29:5000/get_speed"

        # # denote that we are sending data in the form of a json string
        # headers = {
        #     "content-type": "application/json",
        # }

        # json = {
        #     "speed": f"{speed}",
        # }

        # send out the actual request to the api
        response = requests.get(url=url)
        speed = response.text

        return speed

    def post_fan_speed(self, speed):
        
        # address for the rest api
        url = "http://192.168.178.29:5000/post_speed"

        # denote that we are sending data in the form of a json string
        headers = {
            "content-type": "application/json",
        }

        json = {
            "speed": f"{speed}",
        }

        # send out the actual request to the api
        response = requests.post(url=url, headers=headers, json=json)

        self.log(response.text)