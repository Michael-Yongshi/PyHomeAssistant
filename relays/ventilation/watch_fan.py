import appdaemon.plugins.hass.hassapi as hass

class WatchFan(hass.Hass):
    def initialize(self):

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

        # set override variable to default at initialization
        self.override = 0
        self.humidity = 0
        self.smoke = 0

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.fan_override, "FAN_OVERRIDE")
        self.listen_event(self.humidity, "HUMIDITY")
        self.listen_event(self.smoke, "SMOKE")


    # the method that is called when someone wants to override fan setting
    def fan_override(self, event_name, data, kwargs):

        self.override = data["speed"]
        date_time = data["time"][0:18]
        message = f"Someone requested fan speed of {self.override}! \nCurrent date and time is: {date_time}"
        
        # log the message
        self.log(message)

        # Call rest api of ventilation_api.pi on /override
        # add speed in data

    def humidity(self, event_name, data, kwargs):
        
        self.humidity = data["level"]
        date_time = data["time"][0:18]
        
        # log the message
        message = f"Measured humidity at level {self.humidity}! \nCurrent date and time is: {date_time}"
        self.log(message)

        determine_setting()

    def smoke(self, event_name, data, kwargs):
        
        level = data["level"]
        date_time = data["time"][0:18]
        
        # log the message
        message = f"Measured smoke at level {level}! \nCurrent date and time is: {date_time}"
        self.log(message)

        determine_setting()

    def determine_setting():

        if self.smoke >= 600:
            self.log(f"Smoke detected, switching off fan!")
            # request speed 0
        
        else:
            if self.humidity >= 500:
                self.log(f"level 500 or higher observed, set fan to speed 3")
                # request speed 3

            elif level >= 300:
                # request speed 2
                self.log(f"level between 300 and 500 observed, set fan to speed 2")

            else:
                # request_speed 1
                self.log(f"level 300 or lower observed, set fan to speed 1")