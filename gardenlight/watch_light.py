import os
import json
import datetime
import pytz

from pytz import utc
import appdaemon.plugins.hass.hassapi as hass


class WatchLight(hass.Hass):
    """
    Type of class:
    - State Manager

    Method called:
    - determine_setting automatically manages the state of the entity denoted in the config file according to the program denoted there.

    If you manage the light also with a physical switch, make sure you let the switch fire an override event, otherwise the automatic program will
    switch it back as the automatic program is not overridden without it.
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        self.override_expiration = datetime.datetime.now()
        self.override_interval = 12

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.override, "LIGHT_OVERRIDE")

        # check config and fetch settings
        config_filename = "watch_light_config"
        self.config = self.load_json(config_filename)

        # set timezone
        self.timezone = pytz.timezone(self.config["timezone"])
        self.log(self.timezone)

        # define the actual (light) entities used in home assistant
        self.entity = self.config["entity"]
        self.log(self.entity)

        """
        Following call runs every minute to check if something needs to happen
        """
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 10))


    # the method that is called when someone wants to override lights setting from home assistant itself
    def override(self, event_name, data, kwargs):

        if data["entity"] == self.entity:

            current_time = datetime.datetime.now()
            status = data["status"]
            oldstatus = self.get_state(self.entity)

            if status == "auto":
                # disable override by setting expiration to current time
                self.override_expiration = current_time
                self.log(f"Lights override lifted!")

                # immediately run automatically setting the lights as override is stopped
                self.determine_setting(kwargs)

            # if override is active (and speed is the same as previous override) extend the override
            elif status == oldstatus and self.override_expiration > current_time:

                # extend the override parameter
                self.override_expiration += datetime.timedelta(hours=self.override_interval)
                
                # log
                self.log(f"Someone requested lights override, extending the override by {self.override_interval} hours!")

            else:
                # if override is currently not active (for this status) override is set anew
                self.override_expiration = current_time + datetime.timedelta(hours=self.override_interval)

                # log
                self.log(f"Someone requested lights override, setting status {oldstatus} => {status}!")
                
                # send lights command to set the status to the new level
                self.post_light_status(status)

            self.log(f"Current date and time is: {current_time}")

        else:
            pass

    def determine_setting(self, kwargs):
        """
        Checks if the time is currently between sundown and evening end time or between start time and sunrise.
        If so turns on /off light if needed.

        in order to run lights always when its dark, set evening end to 1 o clock and morning start at 23 o clock
        """

        current_time = datetime.datetime.now()

        # check if override is active
        if self.override_expiration >= current_time:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until}")
            return

        # get current status and skip if status of the entity is unavailable
        status = self.get_state(self.entity)
        if status == "unavailable":
            self.log(f"status is unavailable, skipping for now...")
            return

        # sun status
        sun_status = self.get_state("sun.sun")
        self.log(f"sun is {sun_status}")

        # current (date)time
        current_datetime = datetime.datetime.now(tz=utc)
        self.log(f"current datetime is {current_datetime}")

        # get today, tomorrow, yesterday and weekday
        today = current_datetime.date()
        tomorrow = current_datetime.date() + datetime.timedelta(days=1)
        yesterday = current_datetime.date() - datetime.timedelta(days=1)
        weekday = current_datetime.weekday()

        # establish noon
        noon = datetime.datetime.combine(today, datetime.time(hour=12))
        noon = noon.replace(tzinfo=utc)
        self.log(f"Noon {noon}")

        # check which settings are applicable (weekday start at 0 / monday, so today is just weekday number in lookup in the array)
        self.program = self.config["program"]
        tomorrows_program = self.program[weekday + 1]
        todays_program = self.program[weekday]
        yesterdays_program = self.program[weekday - 1] if weekday > 0 else self.program[6]

        # take the settings with noon as the delimiter (as sun is up and lights are definitely supposed to be off)
        if current_datetime > noon:

            # its post-noon program (between noon and midnight)
            self.log("Post-Noon programming for this evening and tomorrow morning")
            evening_program = todays_program["evening_end"]
            evening_day = today
            morning_program = tomorrows_program["morning_start"]
            morning_day = tomorrow

        else:

            # its night or morning (between midnight and noon)
            self.log("Pre-Noon programming for yesterday evening and this morning")

            evening_program = yesterdays_program["evening_end"]
            evening_day = yesterday
            morning_program = todays_program["morning_start"]
            morning_day = today

        # convert the settings of local time to a utc timezone aware datetime
        evening_time = self.convert_string_local_to_t_local_naive(evening_program)
        evening_end_naive = datetime.datetime.combine(evening_day, evening_time.time())
        evening_end = self.convert_dt_local_naive_to_dt_utc_aware(evening_end_naive)
        self.log(f"Evening end is {evening_end}")

        morning_time = self.convert_string_local_to_t_local_naive(morning_program)
        morning_start_naive = datetime.datetime.combine(morning_day, morning_time.time())
        morning_start = self.convert_dt_local_naive_to_dt_utc_aware(morning_start_naive)
        self.log(f"Morning start is {morning_start}")


        if sun_status == "below_horizon":
            self.log(f"Sun is down, now checking if its in exclusion frame...")
            
            if current_datetime <= evening_end:
                message = f"Sun is down, time {current_datetime} is before evening end {evening_end}, lights should be on"
                within_program = True

            elif current_datetime >= morning_start:
                message = f"Sun is down, time {current_datetime} is after morning start {morning_start}, lights should be on"
                within_program = True

            else:
                message = f"Time {current_datetime} is between between evening end {evening_end} and morning start {morning_start}, lights should be off"
                within_program = False

        else:
            message = f"Sun is up"
            within_program = False

        self.log(message)

        # if within program make sure lights are on
        if within_program == True and status == "off":
            self.light_on()
            self.event_happened(message + ". Turning on lights")

        # otherwise make sure lights are off
        elif within_program == False and status == "on":
            self.light_off()
            self.event_happened(message + ". Turning off lights")

        # else do nothing (can be left out, here just for explicit clarity)
        else:
            pass

    def post_light_status(self, status):

        if status == "on":
            self.light_on()
        elif status == "off":
            self.light_off()


    def light_off(self):
        """
        actual call to turn off lights
        """

        self.call_service("light/turn_off", entity_id = self.entity)
        self.log(f"Turned off lights")

    def light_on(self):
        """
        actual call to turn on lights
        """

        self.call_service("light/turn_on", entity_id = self.entity)
        self.log(f"Turned on lights")

    # the method that is called when an event happens
    def event_happened(self, message):

        # log the message before sending it
        # self.log(message)

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            "telegram_bot/send_message", message=message,
        )

    def load_json(self, filename):
        """Load settings json"""

        path = os.path.join(os.sep, "config", "appdaemon", "apps")

        # check if directory already exists
        if not os.path.exists(path):
            self.log(f"cant find path '{path}'")

        else:
            complete_path = os.path.join(path, filename + ".json")

            # open json and return as an array
            with open(complete_path, 'r') as infile:
                contents = json.load(infile)
        
            return contents

    def convert_string_utc_to_dt_utc_aware(self, string_utc):
        """
        Converts a string of UTC time to a (timezone aware) datetime object
        Home assistant works with UTC datetime strings, including the UTC timezone attribute
        """
        dt_utc_aware = datetime.datetime.strptime(string_utc, "%Y-%m-%dT%H:%M:%S%z")

        return dt_utc_aware

    def convert_string_local_to_t_local_naive(self, string_local):
        """
        Used to convert a string notation of a time stamp into a python datetime object 

        Used to convert a setting from a json file (or other user / manual source) into a manipulatable object
        Usually these settings are user controlled and thus in local time

        date or timezone info still needs to be added!
        """

        dt_local_naive = datetime.datetime.strptime(string_local, "%H:%M:%S")

        return dt_local_naive

    def convert_dt_local_naive_to_dt_utc_aware(self, dt_local_naive):
        """
        receives a local naive datetime and transforms it in utc aware datetime
        Once we converted a user setting to a naive datetime object we still need to add timezone info and transform to UTC time
        """

        # adds timezone info only in order to make the datetime object aware of the timezone it represents
        dt_local_aware = self.timezone.localize(dt_local_naive)

        # converts a timezone aware datetime object to universal time (utc)
        dt_utc_aware = dt_local_aware.astimezone(tz=utc)

        return dt_utc_aware