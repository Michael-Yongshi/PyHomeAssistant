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
        self.entity = "climate.thermostat"

        # Were keeping track of an override variable to keep override only on for a certain amount of time
        self.override_expiration = datetime.datetime.now()
        self.override_interval = 1 # hours

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received.
        self.listen_event(self.override, "HEATER_OVERRIDE")

        # loop method to determine if target temp needs to change
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    def override(self, event_name, data, kwargs):

        datetime_interval = datetime.timedelta(hours=self.override_interval)

        status = int(data["status"])
        oldstatus = int(self.get_heater_status())
        current_time = datetime.datetime.now()
        self.log(f"status is {status} with old status {oldstatus}")

        # if override is active (and status is the same as previous override) extend the override
        if status == oldstatus and self.override_expiration > current_time:

            # extend the override parameter
            self.override_expiration += datetime_interval
            
            # log
            self.event_happened(f"Someone requested thermostat override, extending the override by {self.override_interval} hours!")

        else:

            if status >= 2:
                # disable override by setting expiration to current time
                self.override_expiration = current_time
                
                # immediately run automatically setting the fan as override is stopped
                self.determine_setting(kwargs)

                self.event_happened(f"Thermostat override lifted!")

            else:

                # if override is currently not active (for this status) override is set anew
                self.override_expiration = current_time + datetime_interval

                # send thermostat command to set the status to the new level
                self.post_heater_status(status)

                # log
                self.event_happened(f"Someone requested heater override, setting status {oldstatus} => {status}!")

        self.log(f"Current date and time is: {current_time}")
        self.log("")

    def determine_setting(self, kwargs):
        """
        Check logic to see if target temp should change on the thermostat
        """
        
        current_time = datetime.datetime.now()

        # check if override is active
        if self.override_expiration >= current_time:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until}")
            return

        # current target temp
        current_target = self.get_state(self.entity, attribute="temperature")
        # self.log(f"Current target temperature {current_target}")

        # get target temperature based on programming
        program_target = self.get_target_temp()

        if program_target != current_target:
            # only set new temperature if its different
            self.call_service("climate/set_temperature", entity_id=self.entity, temperature=program_target)
            self.event_happened(f"Set new temperature to {program_target} from {current_target}")

    def get_target_temp(self):

        # # get current day
        # current_day = datetime.datetime.today().weekday()
        # current_program_number = self.days[current_day]
        # self.log(f"Loading program {current_program_number}")

        # load program
        # current_program = self.programs[current_program_number]
        # logging.debug(f"Program loaded as: \n{current_program}")

        # check timeslot and target temperature
        target_temp = 0
        while target_temp == 0:
            
            # get current time
            current_time = datetime.datetime.now() # .strftime("%H:%M:%S")
            current_year = current_time.year
            current_month = current_time.month
            current_day = current_time.day

            # self.log(f"Searching for active timeslot... ({current_time})")
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

                # Convert timeslot 'end' to time type
                time_from_string = datetime.datetime.strptime(timeslot["end"], "%H:%M:%S")
                timeslot_end = time_from_string.replace(year=current_year, month=current_month, day=current_day)
                # self.log(timeslot_end)

                # check if current time still falls within this timeslot
                if current_time <= timeslot_end:

                    # set timeslot temperature as current target
                    target_temp = timeslot["temp"]
                    self.log(f"Target temperature is {target_temp}")

                    break

            # if no target temperature is set, restart this progress until it is set
        
        return target_temp

    # depreciated
    def get_heater_status(self):

        # address for the rest api of the device that controls the heater
        url = self.heater + "/get_status"

        # send out the actual request to the api
        response = requests.get(url=url)
        status = response.text

        return status

    # depreciated
    def post_heater_status(self, status):

        # address for the rest api
        url = self.heater + "/post_status"

        # denote that we are sending data in the form of a json string
        headers = {
            "content-type": "application/json",
        }

        json = {
            "status": f"{status}",
        }

        # send out the actual request to the api
        response = requests.post(url=url, headers=headers, json=json)

        self.log(response.text)

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