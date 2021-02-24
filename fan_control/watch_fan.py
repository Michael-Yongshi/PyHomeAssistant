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
        self.override = 0
        # self.humidity_level = 0
        # self.smoke_level = 0

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_state(self.fan_override, "input_number.fan_override")
        # self.listen_event(self.humidity, "HUMIDITY")
        # self.listen_event(self.smoke, "SMOKE")

    def send_request(self, speed):
        
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

    # the method that is called when someone wants to override fan setting from home assistant itself
    def fan_override(self, entity, attribute, old, new, kwargs):

        # remember last time override has been used
        self.override = datetime.datetime.now()

        # convert the state to a valid integer
        speed = int(new.split('.', 1)[0])
        
        # send fan command to set the speed to the new level
        self.send_request(speed)

        # log
        message = f"Someone requested fan override, setting speed {old} => {new}! \nCurrent date and time is: {self.override}"
        self.log(message)

    # the method that is called if someone uses the motion detector
    def motion(self, event_name, data, kwargs):

        self.override = datetime.now()
        speed = self.get_state("input_number.fan") + 1

        message = f"Motion detected, setting speed to {speed}! \nCurrent date and time is: {self.override}"
        
        # Call rest api of the fan
        self.set_fan_speed(speed=self.override)

    # automatically adjust fan speed based on sensor data, humidity and smoke
    def determine_setting(self):

        # only automate if override is 0
        # TODO add 30 min time to revoke the override here
        if self.override != 0:

            # # check if there is smoke outside, disable fan if so
            # if self.smoke_level >= 600:
            #     self.log(f"Smoke detected, switching off fan!")
            #     # request speed 0
            # else:

            if self.humidity_level >= 500:
                self.log(f"level 500 or higher observed, set fan to speed 3")
                # request speed 3

            elif self.humidity_level >= 300:
                # request speed 2
                self.log(f"level between 300 and 500 observed, set fan to speed 2")

            else:
                # request_speed 1
                self.log(f"level 300 or lower observed, set fan to speed 1")

    def humidity(self, event_name, data, kwargs):
        
        self.humidity_level = data["level"]
        date_time = data["time"][0:18]
        
        # log the message
        message = f"Measured humidity at level {self.humidity_level}! \nCurrent date and time is: {date_time}"
        self.log(message)

        self.determine_setting()

    # def smoke(self, event_name, data, kwargs):
        
    #     level = data["level"]
    #     date_time = data["time"][0:18]
        
    #     # log the message
    #     message = f"Measured smoke at level {level}! \nCurrent date and time is: {date_time}"
    #     self.log(message)

    #     self.determine_setting()
