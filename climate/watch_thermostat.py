import appdaemon.plugins.hass.hassapi as hass
import os
import json
import datetime
import time

class WatchThermostat(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - update state of 'climate.central_heating' entity, attribute 'target_temperature' in order to influence the thermostat setting

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # Home assistant parameters
        self.climate_entity = "climate.central_heating"
        self.heater_status_entity = "sensor.mqtt_heater_status"
        self.current_program = self.set_program()

        # keep track of timeslot to allow for user adjustments in between program slots
        self.last_timeslot_end = 0
        self.last_heater_status = None

        # loop method to determine if target temp needs to change
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))
        self.run_minutely(self.check_heater, datetime.time(0, 0, 0))

        self.determine_setting(kwargs=None)

    def determine_setting(self, kwargs):
        """
        Check logic to see if target temp should change on the thermostat
        """

        current_time = datetime.datetime.now()

        # reload user determined program
        self.current_program = self.set_program()

        # get target temperature values
        current_timeslot = self.get_current_timeslot(current_time)
        current_timeslot_end = current_timeslot["end"]
        program_target = current_timeslot["temp"]
        current_target = self.get_state(self.climate_entity, attribute="temperature")
        # self.log(f"Programming target temperature is {program_target}, while current target temperature is {current_target}")

        # check if we already programmed this timeslot before (we will only once, so user can still change it)
        if self.last_timeslot_end != current_timeslot_end:

            # register that we now programmed this timeslot
            self.last_timeslot_end = current_timeslot_end

            # only set new temperature if its different
            if program_target != current_target:
                # set new target temp
                self.post_target_temp(target_temp=program_target)
                self.event_happened(f"Set new temperature to {program_target}, according to the program")

            else:
                self.event_happened(f"New timeslot, but target temperature is already set correctly to {program_target}")

    def get_current_timeslot(self, current_time):
        """
        Current timeslot is calculated as follows

        Iterate over the timeslots in the current program (start with morning and ending with night)
        check if current time is before the end of the timeslot
        if so this timeslot is the active timeslot
        """

        # get current time parameters
        current_year = current_time.year
        current_month = current_time.month
        current_day = current_time.day

        for timeslot in self.current_program:
            timeslot_end = timeslot["end"]

            # Convert timeslot 'end' to time type
            timeslot_end_str = datetime.datetime.strptime(timeslot_end, "%H:%M:%S")
            timeslot_end_dt = timeslot_end_str.replace(year=current_year, month=current_month, day=current_day)

            # check if current time still falls within this timeslot
            if current_time <= timeslot_end_dt:

                # set as current timeslot
                current_timeslot = timeslot
                break

        return current_timeslot

    def set_program(self):

        default_program = [
            # night
            {
                "end": "05:00:00",
                "temp": 16
            },
            # morning
            {
                "end": "12:00:00",
                "temp": 21
            },
            # afternoon
            {
                "end": "17:00:00",
                "temp": 20
            },
            # evening
            {
                "end": "21:00:00",
                "temp": 18
            },
        ]

        user_program = []

        try:
            # Iterate over user settings
            for timeofday in ['night', 'morning', 'afternoon', 'evening']:

                # get user settings for this time of day
                timeslot_sensor = f"input_datetime.{timeofday}_timeslot_slider"
                timeslotend = self.get_state(timeslot_sensor)
                # self.event_happened(f"timeslot sensor is {timeslot_sensor} with value {timeslotend}")

                temp_sensor = f"input_number.{timeofday}_temp_slider"
                temp = self.get_state(temp_sensor)
                # self.event_happened(f'temp sensor is {temp_sensor} with value {temp}')
                # temp = int(self.get_state(f"mqtt_thermostat_{timeofday}_temp"))

                timeslotdict = {
                    "end": timeslotend,
                    "temp": temp,
                }

                user_program += [timeslotdict]
                # self.event_happened(f"Added timeslot {timeofday} as {timeslotdict}!")

            program = user_program
            # self.event_happened(f"Set user program!")

        except:
            program = default_program
            self.event_happened(f"Couldn't set user program, reverting to default program")

        # add last timeslot until midnight and use the first timeslot as temperature
        timeslotdict = {
            "end": "23:59:59",
            "temp": program[0]["temp"],
        }
        program += [timeslotdict]

        return program

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

    def check_heater(self, kwargs):
        """
        Check heater and push status to telegram if changed
        """
        
        new = self.get_heater_status()
        if new != self.last_heater_status:
            self.last_heater_status = new
            self.event_happened(f"Heater turned to {new}")

    def get_heater_status(self):

        # get heater state from the heater entity in home assistant
        heater_status = int(self.get_state(self.heater_status_entity))

        return heater_status

    def post_target_temp(self, target_temp):

        self.call_service("climate/set_temperature", entity_id=self.climate_entity, temperature=target_temp)

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