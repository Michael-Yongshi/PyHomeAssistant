import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

class WatchLight(hass.Hass):
    """
    Type of class:
    - State Listener

    Method called:
    - Set light.decorative_garden based on rising and setting of the sun

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):
        
        # turn on lights before the sun is setting
        evening_start_offset = -1800
        self.run_at_sunset(self.light_on, offset=evening_start_offset)

        # turn off lights after sun has risen
        morning_end_offset = 1800
        self.run_at_sunrise(self.light_off, offset=morning_end_offset)


        # turn off lights fixed time in the night depending on weekend
        weekday_evening_end_time = datetime.time(hour=22, minute=0)
        self.run_daily(self.daily_light, weekday_evening_end_time, weekend=False, light=False)

        weekend_evening_end_time = datetime.time(hour=0, minute=0)
        self.run_daily(self.daily_light, weekend_evening_end_time, weekend=True, light=False)


        # turn on lights fixed time in the morning depending on weekend
        weekday_morning_start_time = datetime.time(hour=7, minute=30)
        self.run_daily(self.daily_light, weekday_morning_start_time, weekend=False, light=True)

        weekend_morning_start_time = datetime.time(hour=8, minute=00)
        self.run_daily(self.daily_light, weekend_morning_start_time, weekend=True, light=True)

    def light_off(self, kwargs):
        # turn off lights
        self.call_service("light/turn_off", entity_id = "light.bedroom_light")
        self.log(f"turned off garden lights")

    def light_on(self, kwargs):
        # turn on lights
        self.call_service("light/turn_on", entity_id = "light.bedroom_light")
        self.log(f"turned on garden lights")

    def daily_light(self, weekend, light):

        # turn light on or off depending on the day of the week
        weekday = datetime.datetime.now().weekday()

        # The time functions always get called, so we filter out the unneeded call 
        # (weekend call on a weekday or other way around)
        if (weekday <= 5 and weekend == False) or (weekday >= 6 and weekend == True):
            if light == True:
                self.light_on()
            else:
                self.light_off()