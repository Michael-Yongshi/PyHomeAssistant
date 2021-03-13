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
        self.log(f"Someone requested fan override, setting speed {old} => {new}!")
        self.log(f"Current date and time is: {self.override}")
        self.log("")

    def humidity(self, entity, attribute, old, new, kwargs):

        # log humidity level
        self.log(f"Measured humidity at {new}%!")
        humidity_level = int(new.split('.', 1)[0])

        # get fanspeed state
        speed = int(self.get_state("sensor.mqtt_fan_speed"))
        self.log(f"Fan speed is {speed}")

        # timings
        override_expiration = self.override + datetime.timedelta(minutes=15)
        current_time = datetime.datetime.now()
        self.log(f"Override expires at {override_expiration}")
        self.log(f"Current date and time is: {current_time}")

        limit3 = 95
        limit2 = 85

        # automatically adjust fan speed based on sensor data, humidity and smoke
        if override_expiration <= current_time:
            self.log(f"Override expired")

            # set to 3 if humidity_level increased to above limit3
            if humidity_level >= limit3:
                setting = 3
                if speed != setting:
                    self.post_fan_speed(setting)
                    self.log(f"level above {limit3}%  observed, set fan to speed {setting}")
                else:
                    self.log(f"level above {limit3}%  observed, fan already at speed {setting}")
            
            # set to 2 if humidity_level is above limit2
            elif humidity_level >= limit2:
                setting = 2
                if speed != setting:
                    self.post_fan_speed(setting)
                    self.log(f"level above {limit2}% observed, set fan to speed {setting}")
                else:
                    self.log(f"level above {limit2}% observed, fan already at speed {setting}")

            # set to 1 if humidity_level is below limit2
            elif humidity_level < limit2:
                setting = 1
                if speed != setting:
                    self.post_fan_speed(setting)
                    self.log(f"level below {limit2}% observed, set fan to speed {setting}")
                else:
                    self.log(f"level below {limit2}% observed, fan already at speed {setting}")

        self.log("")

    def get_fan_speed(self):

        # address for the rest api
        url = "http://192.168.178.29:5000/get_speed"

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