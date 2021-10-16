import appdaemon.plugins.hass.hassapi as hass
import os
import json
import datetime
import requests

class WatchThermostat(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - update state of 'climate.thermostat' entity, attribute 'target_temperature' in order to influence the thermostat setting
    - keep override buttons working it is now

    add data like below and replace x with 0 (off), 1 (on), 9(stop override)
    {'status': x}
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # Home assistant parameters
        self.climate_entity = "climate.thermostat"
        self.floorpump_entity = "switch.floor_pump"
        self.heater_status_entity = "sensor.mqtt_heater_status"

        # keep track of timeslot to avoid having an override for normal behaviour and minor tweaks by users for a short time
        self.last_timeslot_end = 0

        # loop method to determine if target temp needs to change
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

        # call turn on/off floorpump when heater status changes and add once a day floor pump flushing to prevent damage to pipes
        self.listen_state(self.floorpump, self.heater_status_entity)
        self.run_daily(self.floorpump_24_on, datetime.time(12, 0, 0))
        self.run_daily(self.floorpump_24_off, datetime.time(12, 10, 0))

    def floorpump(self, entity, attribute, old, new, kwargs):
        """
        Turns on pump if heater is on, otherwise turn off
        """

        if int(new) == 1:
            self.turn_on(self.floorpump_entity)
            self.event_happened(f"heater is now {new}, turning on floorpump")
        else:
            self.turn_off(self.floorpump_entity)
            self.event_happened(f"heater is now {new}, turning off floorpump")

    def floorpump_24_on(self, kwargs):
        """
        Turns on pump once a day at midnight
        """

        if self.get_heater_status() == 0:
            self.turn_on(self.floorpump_entity)
            self.event_happened(f"Flushing floor radiator, turning on floorpump")
        else:
            self.event_happened(f"Heater is on, flushing floor radiator is not necessary")

    def floorpump_24_off(self, kwargs):
        """
        Turns off pump once a day at midnight + some minutes if heater is off
        """

        if self.get_heater_status() == 0:
            self.turn_off(self.floorpump_entity)
            self.event_happened(f"Flushing floor radiator, turning on floorpump")
        else:
            self.event_happened(f"Heater is on, floor pump can stay on")

    def determine_setting(self, kwargs):
        """
        Check logic to see if target temp should change on the thermostat
        """
        
        current_time = datetime.datetime.now()

        # check if override is active, if so return
        if self.override_expiration >= current_time:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until}")
            return

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

        # get current time parameters
        current_year = current_time.year
        current_month = current_time.month
        current_day = current_time.day

        # TODO, we handle a generic program for now
        current_program = [
            # morning
            {
                "end": "06:30:00",
                "temp": 18
            },
            # afternoon
            {
                "end": "18:00:00",
                "temp": 21
            },
            # evening
            {
                "end": "22:00:00",
                "temp": 20
            },
            # night
            {
                "end": "23:59:59",
                "temp": 18
            }
        ]

        for timeslot in current_program:
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

    def get_heater_status(self):

        # get heater state from the heater entity in home assistant
        heater_status = int(self.get_state(self.heater_status_entity))

        return heater_status

    def post_target_temp(self, target_temp):

        self.call_service("climate/set_temperature", entity_id=self.climate_entity, temperature=target_temp)

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