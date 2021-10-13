import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

import mqttapi as mqtt

class WatchFan(mqtt.Mqtt, hass.Hass):
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
        
        # we set some humidity limits, TODO can become MQTT settings in the future to set by the user
        self.limit3 = 95
        self.limit2 = 85

        # Were keeping track of an override variable to keep override only on for a certain amount of time
        self.override_expiration = datetime.datetime.now()
        self.override_interval = 30

        # call a certain method when mqtt updates are available.
        self.listen_state(self.mqtt_update, "sensor.mqtt_bathroom_humidity")
        self.listen_state(self.override, "sensor.mqtt_fan_set")

        # enforce determining setting even if humidity is unchanged every minute
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    # the method that is called when someone wants to override fan setting from home assistant itself
    def override(self, entity, attribute, old, new, kwargs):

        speed = int(new)
        oldspeed = int(self.get_fan_speed())

        current_time = datetime.datetime.now()

        # check if override is requested to be disabled
        if speed == 9:
            # disable override by setting expiration to current time
            self.override_expiration = current_time
            self.event_happened(f"Fan override lifted!")

            # immediately run automatically setting the fan as override is stopped
            self.determine_setting(kwargs)

        # if override is active (and speed is the same as previous override) extend the override
        elif speed == oldspeed and self.override_expiration > current_time:

            # extend the override parameter
            self.override_expiration += datetime.timedelta(minutes=self.override_interval)
            
            # log
            self.event_happened(f"Someone requested fan override, extending the override by {self.override_interval} minutes!")

        else:
            # if override is currently not active (for this speed) override is set anew
            
            if speed == 0:
                # override to shut off the fan for longer period of time or until override is lifted or changed. 
                self.override_expiration = current_time + datetime.timedelta(days=1)

                # log
                self.event_happened(f"Someone requested stopping the fan, shutting off the fan for the time being!")

            else:
                # overrides in the off setting for by default a day. 
                self.override_expiration = current_time + datetime.timedelta(minutes=self.override_interval)

                # log
                self.event_happened(f"Someone requested fan override, setting speed {oldspeed} => {speed}!")
            
            # send fan command to set the speed to the new level
            self.post_fan_speed(speed)

        self.log(f"Current date and time is: {current_time}")

    # determine setting when humidity changed
    def mqtt_update(self, entity, attribute, old, new, kwargs):

        self.determine_setting(kwargs)

    # determining the setting for the fan based on humidity and override expiration
    def determine_setting(self, kwargs):

        # get fanspeed state
        current_speed = self.get_fan_speed()
        self.log(f"Fan speed is {current_speed}")

        current_time = datetime.datetime.now()

        # check if override is active
        if self.override_expiration >= current_time:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until}")
            return

        # Collect requested settings
        settings = []
        settings += [self.determine_humidity()]
        # settings += [self.determine_cooling()]

        # retrieve highest setting from the array (sort and get last element)
        new_speed = sorted(settings)[-1]

        if current_speed != new_speed:
            self.event_happened(f"Setting fan speed to {new_speed}!")
            self.post_fan_speed(new_speed)
        else:
            self.log(f"Fan speed is already at {new_speed}!")

    def get_fan_speed(self):
        """
        get the current speed of the fan
        """

        # get hass sensor data
        current_speed = int(self.get_state("sensor.mqtt_fan_status"))

        return current_speed

    def post_fan_speed(self, speed):

        self.mqtt_publish(topic = "fan/set", payload = speed, qos = 1)

    def determine_humidity(self):
        """
        Requests a setting to exhaust moisture
        """

        # humidity level (try block as sensor can be down)
        try:
            humidity = float(self.get_state("sensor.mqtt_bathroom_humidity"))
        
            self.log(f"Measured humidity at {humidity}%!")

            # set to 3 if humidity increased to above limit3
            if humidity >= self.limit3:
                setting = 3
                self.log(f"level above {self.limit3}%  observed!")
            
            # set to 2 if humidity is above limit2
            elif humidity >= self.limit2:
                setting = 2
                self.log(f"level above {self.limit2}%, but below {self.limit3}, observed!")

            # set to 1 if humidity is below limit2
            elif humidity < self.limit2:
                setting = 1
                self.log(f"level below {self.limit2}% observed!")

        # if sensor is down, return fan to lowest setting
        except:
            setting = 1
            self.log(f"Couldn't observe humidity!")
        
        return setting
    
    def determine_cooling(self):
        """
        Requests a higher setting in order to cool
        """

        try:
            comfort_temp = 12
            inside_temp = float(self.get_state("sensor.mqtt_living_temperature"))
            outside_temp = float(self.get_state(entity_id="weather.serenity", attribute="temperature"))
            self.log(f"Inside temperature is {inside_temp} versus outside temperature of {outside_temp}")

            if inside_temp > 23:
                self.log(f"Inside temperature is high")
                if inside_temp > outside_temp:
                    setting = 2
                    self.log(f"Outside temperature is low enough to cool!")
                else:
                    setting = 1
                    self.log(f"Outside temperature is too high!")
            else:
                setting = 1
                self.log(f"Inside temperature reached target")

        except:
            setting = 1
            self.log(f"Couldn't observe temperature!")

        return setting

    def event_happened(self, message):
        """
        the method that is called when an event happens
        """

        # log the message before sending it
        self.log(message)

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            "telegram_bot/send_message", message=message,
        )