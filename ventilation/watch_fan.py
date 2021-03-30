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
        self.override_expiration = datetime.datetime.now()
        self.override_interval = 10

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.override, "FAN_OVERRIDE")
        self.listen_state(self.mqtt_update, "sensor.mqtt_bathroom_humidity")

        # enforce determining setting even if humidity is unchanged every minute
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    # the method that is called when someone wants to override fan setting from home assistant itself
    def override(self, event_name, data, kwargs):

        speed = int(data["speed"])
        oldspeed = int(self.get_fan_speed())

        current_time = datetime.datetime.now()

        # check if override is requested to be disabled
        if speed == 9:
            # disable override by setting expiration to current time
            self.override_expiration = current_time
            self.log(f"Fan override lifted!")

            # immediately run automatically setting the fan as override is stopped
            self.determine_setting(kwargs)

        # if override is active (and speed is the same as previous override) extend the override
        elif speed == oldspeed and self.override_expiration > current_time:

            # extend the override parameter
            self.override_expiration += datetime.timedelta(minutes=self.override_interval)
            
            # log
            self.log(f"Someone requested fan override, extending the override by {self.override_interval} minutes!")

        else:
            # if override is currently not active (for this speed) override is set anew
            
            if speed == 0:
                # override to shut off the fan for longer period of time or until override is lifted or changed. 
                self.override_expiration = current_time + datetime.timedelta(days=1)

                # log
                self.log(f"Someone requested stopping the fan, shutting off the fan for the time being!")

            else:
                # overrides in the off setting for by default a day. 
                self.override_expiration = current_time + datetime.timedelta(minutes=self.override_interval)

                # log
                self.log(f"Someone requested fan override, setting speed {oldspeed} => {speed}!")
            
            # send fan command to set the speed to the new level
            self.post_fan_speed(speed)

        self.log(f"Current date and time is: {current_time}")
        self.log("")

    # determine setting when humidity changed
    def mqtt_update(self, entity, attribute, old, new, kwargs):

        self.determine_setting(kwargs)

    # determining the setting for the fan based on humidity and override expiration
    def determine_setting(self, kwargs):

        # get fanspeed state
        speed = int(self.get_state("sensor.mqtt_fan_speed"))
        self.log(f"Fan speed is {speed}")

        current_time = datetime.datetime.now()

        limit3 = 95
        limit2 = 85

        # automatically adjust fan speed based on sensor data, humidity and smoke
        if self.override_expiration <= current_time:
            self.log(f"Override expired")

            # humidity level (try block as sensor can be down)
            try:
                humidity = float(self.get_state("sensor.mqtt_bathroom_humidity"))
            
                self.log(f"Measured humidity at {humidity}%!")

                # set to 3 if humidity increased to above limit3
                if humidity >= limit3:
                    setting = 3
                    if speed != setting:
                        self.post_fan_speed(setting)
                        self.log(f"level above {limit3}%  observed, set fan to speed {setting}")
                    else:
                        self.log(f"level above {limit3}%  observed, fan already at speed {setting}")
                
                # set to 2 if humidity is above limit2
                elif humidity >= limit2:
                    setting = 2
                    if speed != setting:
                        self.post_fan_speed(setting)
                        self.log(f"level above {limit2}% observed, set fan to speed {setting}")
                    else:
                        self.log(f"level above {limit2}% observed, fan already at speed {setting}")

                # set to 1 if humidity is below limit2
                elif humidity < limit2:
                    setting = 1
                    if speed != setting:
                        self.post_fan_speed(setting)
                        self.log(f"level below {limit2}% observed, set fan to speed {setting}")
                    else:
                        self.log(f"level below {limit2}% observed, fan already at speed {setting}")

            # if sensor is down, return fan to lowest setting
            except:
                setting = 1
                self.log(f"Couldn't observe humidity!")
                if speed != setting:
                    self.post_fan_speed(setting)
                    self.log(f"Set fan to speed {setting}")

        else:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until} minutes")
            
        self.log("")

    # get the current speed of the fan
    def get_fan_speed(self):

        # address for the rest api
        url = "http://192.168.178.29:5000/get_speed"

        # send out the actual request to the api
        response = requests.get(url=url)
        speed = response.text

        return speed

    # set the speed of the fan
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