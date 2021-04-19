import appdaemon.plugins.hass.hassapi as hass
import datetime

class WatchLight(hass.Hass):
    """
    Type of class:
    - State Listener

    Method called:
    - Set light.decorative_garden based on rising and setting of the sun

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # define the actual (light) entities used in home assistant
        self.entity = "light.garden_lights"

        """
        Following calls are needed to turn on the lights on sunset and turn off the lights on sunrise
        """
        # turn on lights before the sun is setting
        evening_start_offset = -1800 # <= 0, in seconds
        self.run_at_sunset(self.light_on, offset=evening_start_offset)

        # turn off lights after sun has risen
        morning_end_offset = 1800 # >= 0, in seconds
        self.run_at_sunrise(self.light_off, offset=morning_end_offset)


        """
        Following calls are needed if we want the lights to not burn through the night
        Appdaemon can only run functions everyday without exception, 
        so we create seperate functions and give a list of days to run and filter in the functions themselves accordingly
        """

        """
        in the evening we shut them down when we expect to go to sleep
        """
        # Day before a weekday I dont stay up late
        self.run_daily(self.evening_end, datetime.time(hour=23, minute=0), valid=[1,2,3,4,7],)

        # On friday and saturday I can stay up later
        self.run_daily(self.evening_end, datetime.time(hour=0, minute=0), valid=[5,6],)

        """
        in the morning we turn them on again when we wake up (if we wake up when sun is still down)
        """
        # On weekdays I have to get up early
        self.run_daily(self.morning_start, datetime.time(hour=6, minute=0), valid=[1,2,3,4,5],)

        # In weekend I can sleep in
        self.run_daily(self.morning_start, datetime.time(hour=7, minute=0), valid=[6,7],)


    def evening_end(self, valid):
        """
        Set the weekdays for the evening program and call the verify function with the light turn off call
        """

        # check if the call is valid on this day, filter out the non-matching calls
        self.verify_call( 
            valid = valid,
            call = self.light.off
            )


    def morning_start(self, valid):
        """
        Set the weekdays for the morning program and call the verify function with the light turn on call
        But additional check if sun isnt already up:
        otherwise the program first turns off during sunrise and turn on will be called afterwards and will never be turned off again
        """

        # In the morning, only do something if sun is still down
        if self.sun_up():
            self.log(f"Morning call invalid as sun has already risen!")

        else:
            # check if the call is valid on this day, filter out the non-matching calls
            self.verify_call(
                valid = valid, 
                call = self.light.on
                )

    def verify_call(self, valid, call):
        """
        Contains the logic to filter out unmatching calls, as appdaemon cant run daily functions on specific days of the week
        So we run both a weekend function and weekday function and only execute when they are applicable
        """

        # current day of the week
        weekday = datetime.datetime.now().weekday()

        # if the current day is in the list of days that are applicable then its a valid call
        if (weekday in valid):
            self.log(f"This call was valid with current day {weekday} and valid days {valid}, calling {call}!")
            call()

        else:
            self.log(f"This call was invalid with current day {weekday} and valid days {valid}!")
            pass

    def light_off(self, kwargs):
        # actual call to turn off lights
        self.call_service("light/turn_off", entity_id = self.entity)
        self.log(f"Turned off lights")

    def light_on(self, kwargs):
        # turn on lights
        self.call_service("light/turn_on", entity_id = self.entity)
        self.log(f"Turned on lights")
