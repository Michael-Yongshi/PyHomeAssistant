
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

        # Entities to influence
        self.entities = self.args["entities"]

        ###### User program

        # Toggle to turn programming on or off
        self.toggle = self.args["toggle"]
        self.timezone = pytz.timezone("Europe/Amsterdam")
        # self.timezone = utc

        # In amount of degrees of elevation: gives you offset of around 10 - 15 minutes per degree
        self.elevation_offset = self.args["offset"]

        # helper format
        helper_type = "input_datetime."
        self.helper_start = helper_type + "light_start_"
        self.helper_end = helper_type + "light_end_"
        self.timeslotcategories = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


        # variables to watch with initial value
        self.current_program = self.set_program()


        ###### Override method: Complex
        # keep track of override datetime variables to allow for user override disregarding timeslots
        self.override_interval = self.args["interval"]

        # variable to watch with initial value
        self.override_expiration_utc = datetime.datetime.now(tz=self.timezone)

        # Entities to listen for manual override
        self.switches = self.args["switches"]
        
        # Event to listen for HASS override
        self.event = self.args["event"]

        """
        Callback runs once an event has been fired in HASS
        """
        self.listen_event(self.override_event, self.event)
        for switch in self.switches:
            self.listen_state(self.override_switch, switch)

        """
        Following call runs every minute to check if something needs to happen
        """
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 10))

        self.determine_setting(kwargs=None)

    def determine_setting(self, kwargs):
        """
        Checks if the time is currently between sundown and evening end time or between start time and sunrise.
        If so turns on /off light if needed.

        in order to run lights always when its dark, set evening end to 1 o clock and morning start at 23 o clock
        """

        if self.get_state(self.toggle) != "on":
            return

        # get current datetime value
        current_datetime_local = datetime.datetime.now(tz=self.timezone)
        self.log(f"current datetime local is {current_datetime_local}")
        current_datetime_utc = self.convert_dt_local_aware_to_utc_aware(current_datetime_local)
        self.log(f"current datetime utc is {current_datetime_utc}")

        # check if override is active, if so discontinue and return
        if self.override_expiration_utc >= current_datetime_utc:
            # expire_time = self.override_expiration_utc - current_datetime_utc
            # override_expiration_local = self.convert_dt_utc_aware_to_local_aware(self.override_expiration_utc)
            # self.event_happened(f"Override active, expires in {expire_time} at {override_expiration_local}")

            return

        # get current status and skip if status of the entity is unavailable
        status = self.get_state(self.entities[0])
        if status == "unavailable":
            self.log(f"status is unavailable, skipping for now...")

            # signal whenever the state cant be received
            # self.event_happened(message)

            return

        # Check sun elevation
        sun_elevation_str = self.get_state("sun.sun", attribute = 'elevation')
        sun_elevation = int(sun_elevation_str)
        # self.event_happened(f"elevation is {sun_elevation} and is of type {type(sun_elevation)}")

        # check elevation offset
        offset_raw = self.get_state(self.elevation_offset)
        offset_str = offset_raw.split(".")[0]
        offset = int(offset_str)
        # self.event_happened(f"target offset = {offset} and is type {type(offset)}")

        # timeslot is only needed if sun is under elevation level
        if sun_elevation < offset:

            self.log(f"Actual elevation {sun_elevation} is below elevation {offset_raw}")
            self.log(f"Sun is down, now checking if its in exclusion frame...")

            # get current timeslot (in utc)
            current_timeslot = self.get_current_timeslot(current_datetime_local)
            morning_start_local_naive = current_timeslot["start"]
            evening_end_local_naive = current_timeslot["end"]
            morning_start_utc = self.convert_dt_local_naive_to_dt_utc_aware(morning_start_local_naive)
            evening_end_utc = self.convert_dt_local_naive_to_dt_utc_aware(evening_end_local_naive)

            # get times in local for logging purposes
            morning_start_local = self.convert_dt_local_naive_to_dt_local_aware(morning_start_local_naive)
            evening_end_local = self.convert_dt_local_naive_to_dt_local_aware(evening_end_local_naive)

            # check if time is before evening end (evening window)
            if current_datetime_utc <= evening_end_utc:
                self.log(f"current time utc {current_datetime_utc} is before evening end utc {evening_end_utc}, local time setting was {evening_end_local}")
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is before evening end {self.pretty_datetime(evening_end_local)}, lights should be on"
                within_lights_window = True

            # check if time is after morning start (morning window)
            elif current_datetime_utc >= morning_start_utc:
                self.log(f"current time utc {current_datetime_utc} is before evening end utc {morning_start_utc}, local time setting was {morning_start_local}")
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is after morning start {self.pretty_datetime(morning_start_local)}, lights should be on"
                within_lights_window = True

            # check if time is in between evening end and morning start (exclusion frame)
            else:
                self.log(f"current time utc {current_datetime_utc} is between evening end utc {evening_end_utc}, local time setting was {evening_end_local}, and morning start utc {morning_start_utc}, with local setting was {morning_start_local}")
                message = f"Sun is down, time {self.pretty_datetime(current_datetime_local)} is between between evening end {self.pretty_datetime(evening_end_local)} and morning start {self.pretty_datetime(morning_start_local)}, lights should be off"
                within_lights_window = False

        # sun is up, lights should be off regardless
        else:
            self.log(f"sun is up with current time utc {current_datetime_utc} and local time {current_datetime_local}")
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

    def get_current_timeslot(self, current_datetime_local):
        """
        Finds the correct setting based on the config and the current datetime
        """

        # reload user determined program
        self.current_program = self.set_program()

        # Get the relevant timeslot based on weekday
        # get today, tomorrow, yesterday and weekday in local times (otherwise date is off)
        today = current_datetime_local.date()
        tomorrow = current_datetime_local.date() + datetime.timedelta(days=1)
        yesterday = current_datetime_local.date() - datetime.timedelta(days=1)
        weekday = current_datetime_local.weekday()

        # get settings for yesterday, today and tomorrow (weekday start at 0 / monday, so today is just weekday number in lookup in the array)
        tomorrows_program = self.current_program[weekday + 1] if weekday < 6 else self.current_program[0]
        # self.event_happened(f"tomorrows program = {tomorrows_program}")
        todays_program = self.current_program[weekday]
        # self.event_happened(f"todays program = {todays_program}")
        yesterdays_program = self.current_program[weekday - 1] if weekday > 0 else self.current_program[6]
        # self.event_happened(f"yesterdays program = {yesterdays_program}")

        # establish noon as a datetime aware object (in UTC)
        noontime = self.convert_string_local_to_t_local_naive("12:00:00")
        noon = datetime.datetime.combine(current_datetime_local.date(), noontime.time())
        noon_local = self.convert_dt_local_naive_to_dt_local_aware(noon)
        self.log(f"Noon local is at {noon_local}, while current dt is {current_datetime_local}")

        # take the correct settings with noon as the delimiter (as sun is up and lights are definitely supposed to be off, in contrast to midnight...)
        if current_datetime_local > noon_local:

            # its post-noon program (between noon and midnight)
            # self.event_happened("Post-Noon programming for this evening and tomorrow morning")
            evening_program = todays_program["evening_end"]
            evening_day = today
            morning_program = tomorrows_program["morning_start"]
            morning_day = tomorrow

        else:

            # its night or morning (between midnight and noon)
            # self.event_happened("Pre-Noon programming for yesterday evening and this morning")

            evening_program = yesterdays_program["evening_end"]
            evening_day = yesterday
            morning_program = todays_program["morning_start"]
            morning_day = today

        # convert the settings that are written by the user in local time to both a utc and local timezone aware datetime
        evening_time = self.convert_string_local_to_t_local_naive(evening_program)
        evening_day_correction = 0 if evening_time.time() > datetime.time(hour=12) else 1
        evening_end_naive = datetime.datetime.combine(evening_day + datetime.timedelta(days=evening_day_correction), evening_time.time())
        evening_end_utc = self.convert_dt_local_naive_to_dt_utc_aware(evening_end_naive)
        self.log(f"Evening end is in utc {evening_end_utc}, which is in local time {evening_end_naive}")

        morning_time = self.convert_string_local_to_t_local_naive(morning_program)
        morning_day_correction = 1 if morning_time.time() > datetime.time(hour=12) else 0
        morning_start_naive = datetime.datetime.combine(morning_day - datetime.timedelta(days=morning_day_correction), morning_time.time())
        morning_start_utc = self.convert_dt_local_naive_to_dt_utc_aware(morning_start_naive)
        self.log(f"Morning start in utc is {morning_start_utc}, which is in local time {morning_start_naive}")

        current_timeslot = {
            "start": morning_start_naive, 
            "end": evening_end_naive
        }

        return current_timeslot

    def set_program(self):

        user_program = []

        # Iterate over user settings
        for category in self.timeslotcategories:

            start_sensor = self.helper_start + category
            start_time = self.get_state(start_sensor)
            # self.event_happened(f"timeslot start sensor is {start_sensor} with value {start_time}")

            end_sensor = self.helper_end + category
            end_time = self.get_state(end_sensor)
            # self.event_happened(f'timeslot end sensor is {end_sensor} with value {end_time}')

            timeslotdict = {
                "day": f"{category}",
                "morning_start": start_time,
                "evening_end": end_time
            }

            user_program += [timeslotdict]
            # self.event_happened(f"Added timeslot {category} as {timeslotdict}!")

        program = user_program
        # self.event_happened(f"Set user program!")


        return program

    def event_happened(self, message):
        """
        the method that is called when an event happens
        """

        # log the message before sending it
        self.log(message)

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            f'notify/telegram_log', title="", message=message)

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

        # self.event_happened(f"{old} changed to {new}")

        valid = ["on", "off"]
        if old in valid and new in valid:
            self.override(set_state=new)

    def override_event(self, event_name, data, kwargs):
        """
        the method that is called when someone wants to override lights setting from home assistant itself, which works through firing events
        """

        self.override(data["status"])

    def override(self, set_state=""):
        """
        if no set_state is given it will default to "auto"
        """

        # current (date)time
        current_datetime_utc = datetime.datetime.now(tz=self.timezone)
        current_datetime_local = self.convert_dt_utc_aware_to_local_aware(current_datetime_utc)
        # self.event_happened(f"current datetime is {current_datetime_local}")

        # get current status of the entity
        current_status = self.get_state(self.entities[0])

        if set_state == "auto" or set_state == "":

            # disable override by setting expiration to current time
            self.override_expiration_utc = current_datetime_utc

            # log
            message = f"Lights override lifted!"
            self.event_happened(message)

            # immediately run automatically setting the lights as override is stopped
            self.determine_setting(kwargs=None)

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
            if set_state == "on":
                self.light_on()
            elif set_state == "off":
                self.light_off()

    def convert_string_utc_to_dt_utc_aware(self, string_utc):
        """
        Converts a string of UTC time to a (timezone aware) datetime object
        Home assistant works with UTC datetime strings, including the UTC timezone attribute
        """
        dt_utc_aware = datetime.datetime.strptime(string_utc, "%Y-%m-%dT%H:%M:%S%z")

        return dt_utc_aware

    def convert_string_utc_to_t_utc_aware(self, string_utc):
        """
        Converts a string of UTC time to a (timezone aware) datetime object
        Home assistant works with UTC datetime strings, including the UTC timezone attribute
        """

        dt_utc_aware = datetime.datetime.strptime(string_utc, "%H:%M:%S%z")

        return dt_utc_aware

    def convert_string_local_to_t_local_naive(self, string_local):
        """
        Used to convert a string notation of a time stamp into a python datetime object 

        Used to convert a setting from a json file (or other user / manual source) into a manipulatable object
        Usually these settings are user controlled and thus in local time

        date or timezone info still needs to be added!
        """

        if string_local[:2] == '24':
            string_local = '00' + string_local[2:]
            # self.event_happened(f"string local corrected to {string_local}")
        dt_local_naive = datetime.datetime.strptime(string_local, "%H:%M:%S")

        return dt_local_naive

    def convert_dt_utc_aware_to_local_aware(self, dt_utc_aware):
        """
        receives a utc aware datetime and transforms it in local aware datetime
        """

        # converts a timezone aware datetime object to local time (based on timezone established in config)
        dt_local_aware = dt_utc_aware.astimezone(tz=self.timezone)

        return dt_local_aware

    def convert_dt_local_aware_to_utc_aware(self, dt_local_aware):
        """
        receives a utc aware datetime and transforms it in local aware datetime
        """

        # converts a timezone aware datetime object to local time (based on timezone established in config)
        dt_utc_aware = dt_local_aware.astimezone(tz=utc)

        return dt_utc_aware

    def convert_dt_local_naive_to_dt_utc_aware(self, dt_local_naive):
        """
        receives a local naive datetime and transforms it in utc aware datetime
        Once we converted a user setting to a naive datetime object we still need to add timezone info and transform to UTC time
        """

        dt_local_aware = self.convert_dt_local_naive_to_dt_local_aware(dt_local_naive)

        # converts a timezone aware datetime object to universal time (utc)
        dt_utc_aware = dt_local_aware.astimezone(tz=utc)

        return dt_utc_aware

    def convert_dt_local_naive_to_dt_local_aware(self, dt_local_naive):

        # adds timezone info only in order to make the datetime object aware of the timezone it represents
        dt_local_aware = self.timezone.localize(dt_local_naive)

        return dt_local_aware

    def pretty_datetime(self, datetime):

        # Format datetime string
        pretty_dt = datetime.strftime("day %d time %H:%M")

        return pretty_dt

    def light_off(self):
        """
        actual call to turn off lights
        """

        for entity in self.entities:
            self.call_service("light/turn_off", entity_id = entity)
        self.event_happened(f"Turned off lights")

    def light_on(self):
        """
        actual call to turn on lights
        """

        for entity in self.entities:
            self.call_service("light/turn_on", entity_id = entity)
        self.event_happened(f"Turned on lights")
