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
    - process automatically manages the state of the entity denoted in the config file according to the program denoted there
    - override makes sure process is stopped for a certain time

    If you manage the light also with a physical switch, make sure you let the switch fire an override event, otherwise the automatic program will
    switch it back as the automatic program is not overridden without it.
    """

    def initialize(self):
        """
        Next, we will define our initialize function, which is how AppDaemon starts our app. 
        """

        self.override_expiration_utc = datetime.datetime.now(tz=utc)
        self.override_interval = 1

        # define the actual (light) entities used in home assistant and the events to watch for
        self.entity = "light.garden_lights"
        self.switch = "binary_sensor.garden_lights_input"
        self.event = "GARDEN_LIGHTS_OVERRIDE"

        # check config and fetch settings
        config_filename = "watch_light_config"
        self.config = self.load_json(config_filename)

        # set timezone
        self.timezone = pytz.timezone(self.config["timezone"])
        self.log(self.timezone)

        # tells appdaemon we want to call a certain method upon event or state change
        self.listen_event(self.override_event, self.event)
        self.listen_state(self.override_switch, self.switch)

        """
        Following call runs every minute to check if something needs to happen
        """
        self.run_minutely(self.periodic_process, datetime.time(0, 0, 10))

    def override_switch(self, entity, attribute, old, new, kwargs):
        """
        the method that is called when someone overrides with the manual external (physical) switch, which works by observing the switch state
        As shelly already switched the lights on or off, we just have to add an override and leaves the 'set_state' field blank

        only do something when the sensor has valid values, i.e. when it is 'unavailable' it shouldnt do anything
        both from and to unavalability status need to be prevented as this represents the shelly being unreachable for now
        but doesnt signify a real change in status
         
        old = valid status to new = unavailable
        old = unavailable to new = valid status
        """

        self.log(f"{old} changed to {new}")

        valid = ["on", "off"]
        if old in valid and new in valid:
            self.override()

    def override_event(self, event_name, data, kwargs):
        """
        the method that is called when someone wants to override lights setting from home assistant itself, which works through firing events
        """

        self.override(data["status"])

    def periodic_process(self, kwargs):
        """
        Only here to redirect without the kwargs variable as process is also called from another method in this script
        """

        self.process()

    def override(self, set_state=""):
        """
        if no set_state is given it will default to "auto"
        """

        # current (date)time
        current_datetime_utc = datetime.datetime.now(tz=utc)
        current_datetime_local = self.convert_dt_utc_aware_to_local_aware(current_datetime_utc)
        self.log(f"current datetime is {current_datetime_local}")

        # get current status of the entity
        current_status = self.get_state(self.entity)

        if set_state == "auto" or set_state == "":

            # disable override by setting expiration to current time
            self.override_expiration_utc = current_datetime_utc

            # log
            message = f"Lights override lifted!"
            self.event_happened(message)

            # immediately run automatically setting the lights as override is stopped
            self.process()

        # if override is active (and speed is the same as previous override) extend the override
        elif set_state == current_status and self.override_expiration_utc > current_datetime_utc:

            # extend the override parameter
            self.override_expiration_utc += datetime.timedelta(days=self.override_interval)

            # log
            message = f"Someone requested lights override, extending the override!"
            self.event_happened(message)

        else:

            # to get to noon next day or today
            # i.e. 21 o clock, then 15 hours have to be added to get to tomorrows noon. 36 - 21 = 15
            # i.e. 7 o clock, then only 5 hours have to be added to get to todays noon. 12 - 7 = 5
            extension = 36 if current_datetime_local.hour > 12 else 12
            expiration_time_delta = datetime.timedelta(hours=(extension-current_datetime_local.hour))

            # override is set anew
            self.override_expiration_utc = current_datetime_local + expiration_time_delta
            # self.override_expiration_utc = self.convert_string_utc_to_dt_utc_aware(self.get_state('sun.sun', 'next_noon'))

            # log
            message = f"Someone requested lights override, turning lights {set_state}!"
            self.event_happened(message)

            # send lights command to set the status to the new level
            self.post_light_status(set_state)

    def process(self):
        """
        Checks if the time is currently between sundown and evening end time or between start time and sunrise.
        If so turns on /off light if needed.

        in order to run lights always when its dark, set evening end to 1 o clock and morning start at 23 o clock
        """

        # current (date)time
        current_datetime_utc = datetime.datetime.now(tz=utc)
        current_datetime_local = self.convert_dt_utc_aware_to_local_aware(current_datetime_utc)
        self.log(f"current datetime is {current_datetime_local}")

        # check if override is active
        if self.override_expiration_utc >= current_datetime_utc:
            expire_time = self.override_expiration_utc - current_datetime_utc
            override_expiration_local = self.convert_dt_utc_aware_to_local_aware(self.override_expiration_utc)
            self.log(f"Override active, expires in {expire_time} at {override_expiration_local}")

            # override is active, return without doing anything
            return

        # get current status and skip if status of the entity is unavailable
        status = self.get_state(self.entity)
        if status == "unavailable":
            message = f"status is unavailable, skipping for now..."

            # signal whenever the state cant be received
            self.event_happened(message)

            return

        # sun status
        sun_status = self.get_state("sun.sun")
        # self.log(f"sun is {sun_status}")

        if sun_status == "below_horizon":
            self.log(f"Sun is down, now checking if its in exclusion frame...")

            morning_start_utc, morning_start_local, evening_end_utc, evening_end_local = self.determine_setting(current_datetime_utc, current_datetime_local)

            # check if time is before evening end (evening window)
            if current_datetime_utc <= evening_end_utc:
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is before evening end {self.pretty_datetime(evening_end_local)}, lights should be on"
                within_lights_window = True

            # check if time is after morning start (morning window)
            elif current_datetime_utc >= morning_start_utc:
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is after morning start {self.pretty_datetime(morning_start_local)}, lights should be on"
                within_lights_window = True

            # check if time is in between evening end and morning start (exclusion frame)
            else:
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is between between evening end {self.pretty_datetime(evening_end_local)} and morning start {self.pretty_datetime(morning_start_local)}, lights should be off"
                within_lights_window = False

        # sun is up, lights should be off regardless
        else:
            message = f"Sun is up, time {self.pretty_datetime(current_datetime_local)}"
            within_lights_window = False

        # log for debugging of every decision
        self.log(message)

        # if within a light window, but lights are off, turn them on
        if within_lights_window == True and status == "off":
            self.light_on()
            self.event_happened(message + ". Turning on lights")

        # if sun is up or time within the exclusion frame, but lights are on, turn them off
        elif within_lights_window == False and status == "on":
            self.light_off()
            self.event_happened(message + ". Turning off lights")

        # else do nothing (can be left out, here just for explicit clarity)
        else:
            pass

    def determine_setting(self, current_datetime_utc, current_datetime_local):
        """
        Finds the correct setting based on the config file and the current datetime
        """

        # establish noon as a datetime aware object (based on today in local time, but expressed in UTC)
        noontime = self.convert_string_local_to_t_local_naive("12:00:00")
        noon = datetime.datetime.combine(current_datetime_local.date(), noontime.time())
        noon_utc = self.convert_dt_local_naive_to_dt_utc_aware(noon)
        noon_local = self.convert_dt_utc_aware_to_local_aware(noon_utc)
        self.log(f"Noon Local is at {noon_local}")

        # get today, tomorrow, yesterday and weekday in local times (otherwise date is off)
        today = current_datetime_local.date()
        tomorrow = current_datetime_local.date() + datetime.timedelta(days=1)
        yesterday = current_datetime_local.date() - datetime.timedelta(days=1)
        weekday = current_datetime_local.weekday()

        # get settings for yesterday, today and tomorrow (weekday start at 0 / monday, so today is just weekday number in lookup in the array)
        self.program = self.config["program"]
        tomorrows_program = self.program[weekday + 1] if weekday < 6 else self.program[0]
        todays_program = self.program[weekday]
        yesterdays_program = self.program[weekday - 1] if weekday > 0 else self.program[6]

        # take the correct settings with noon as the delimiter (as sun is up and lights are definitely supposed to be off, in contrast to midnight...)
        if current_datetime_local > noon_local:

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

        # convert the settings that are written by the user in local time to both a utc and local timezone aware datetime
        evening_time = self.convert_string_local_to_t_local_naive(evening_program)
        evening_day_correction = 0 if evening_time.time() > datetime.time(hour=12) else 1
        evening_end_naive = datetime.datetime.combine(evening_day + datetime.timedelta(days=evening_day_correction), evening_time.time())
        evening_end_utc = self.convert_dt_local_naive_to_dt_utc_aware(evening_end_naive)
        evening_end_local = self.convert_dt_utc_aware_to_local_aware(evening_end_utc)
        self.log(f"Evening end is {evening_end_local}")

        morning_time = self.convert_string_local_to_t_local_naive(morning_program)
        morning_day_correction = 1 if morning_time.time() > datetime.time(hour=12) else 0
        morning_start_naive = datetime.datetime.combine(morning_day - datetime.timedelta(days=morning_day_correction), morning_time.time())
        morning_start_utc = self.convert_dt_local_naive_to_dt_utc_aware(morning_start_naive)
        morning_start_local = self.convert_dt_utc_aware_to_local_aware(morning_start_utc)
        self.log(f"Morning start is {morning_start_local}")

        return morning_start_utc, morning_start_local, evening_end_utc, evening_end_local

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

    def convert_dt_utc_aware_to_local_aware(self, dt_utc_aware):
        """
        receives a utc aware datetime and transforms it in local aware datetime
        """

        # converts a timezone aware datetime object to local time (based on timezone established in config)
        dt_local_aware = dt_utc_aware.astimezone(tz=self.timezone)

        return dt_local_aware

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

    def pretty_datetime(self, datetime):

        # Format datetime string
        pretty_dt = datetime.strftime("%Y-%m-%d %H:%M:%S")

        return pretty_dt

    def load_json(self, filename):
        """
        Load settings json
        """

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
