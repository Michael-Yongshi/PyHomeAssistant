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
    - Post to api to switch on/off heater
    
    Test this class by firing a test event
    -> hass web ui -> developer tools -> events -> type "THERMOSTAT_OVERRIDE -> fire event

    add data like below and replace x with 0 (off), 1 (on), 9(stop override)
    {'status': x}
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # set settings from settings file
        self.days = self.load_json("days")
        self.programs = self.load_json("programs")
        self.bound = 0.5

        # Were keeping track of an override variable to keep override only on for a certain amount of time
        self.override_expiration = datetime.datetime.now()
        self.override_interval = 60

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.override, "HEATER_OVERRIDE")
        self.listen_state(self.mqtt_update, "sensor.mqtt_living_temperature")

        # enforce determining setting even if humidity is unchanged every minute
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    def override(self, event_name, data, kwargs):

        status = int(data["status"])
        oldstatus = int(self.get_heater_status())
        current_time = datetime.datetime.now()
        self.log(f"status is {status} with old status {oldstatus}")

        # if override is active (and status is the same as previous override) extend the override
        if status == oldstatus and self.override_expiration > current_time:

            # extend the override parameter
            self.override_expiration += datetime.timedelta(minutes=self.override_interval)
            
            # log
            self.log(f"Someone requested thermostat override, extending the override by {self.override_interval} minutes!")

        else:

            if status >= 2:
                # disable override by setting expiration to current time
                self.override_expiration = current_time
                
                # immediately run automatically setting the fan as override is stopped
                self.determine_setting(kwargs)

                self.log(f"Thermostat override lifted!")

            else:

                # if override is currently not active (for this status) override is set anew
                self.override_expiration = current_time + datetime.timedelta(minutes=self.override_interval)

                # send thermostat command to set the status to the new level
                self.post_heater_status(status)

                # log
                self.log(f"Someone requested heater override, setting status {oldstatus} => {status}!")

        self.log(f"Current date and time is: {current_time}")
        self.log("")

    def mqtt_update(self, entity, attribute, old, new, kwargs):

        self.determine_setting(kwargs)

    def determine_setting(self, kwargs):

        # get heater state
        status = int(self.get_state("sensor.mqtt_heater_status"))
        
        current_time = datetime.datetime.now()

        # check if override is active
        if self.override_expiration >= current_time:
            until = self.override_expiration - current_time
            self.log(f"Override active, expires in {until}")
            return
            
        # # humidity level (try block as sensor can be down)
        # try:
        temp = float(self.get_state("sensor.mqtt_living_temperature"))
        self.log(f"Measured temperature at {temp}C!")

        # get target temperature based on program
        target_temp = self.get_target_temp()
        lower_bound = target_temp - self.bound
        upper_bound = target_temp + self.bound

        # if heater is on (1), turn off only when temperature reaches the upper bound
        if status == 1:
            
            if temp >= upper_bound:
                self.log(f"Temperature ({temp}) rose above upper bound ({upper_bound})")
                self.post_heater_status(status=0)
                self.log(f"Turned off heater")
            else:
                self.log(f"Temperature ({temp}) is still below upper bound ({upper_bound})")
        
        # if heater is off, turn on only when temperature reaches the lower bound
        # (to prevent turning the heater on or off to often)
        if status == 0:
            
            if temp < lower_bound:
                self.log(f"Temperature ({temp}) fell below lower bound ({lower_bound})")
                self.post_heater_status(status=1)
                self.log(f"Turned on heater")
            else:
                self.log(f"Temperature ({temp}) is still above lower bound ({lower_bound})")

    def get_target_temp(self):
        
        # get current day and associated program
        current_day = datetime.datetime.today().weekday()
        current_program_number = self.days[current_day]
        self.log(f"Loading program {current_program_number}")

        # load program
        current_program = self.programs[current_program_number]
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

    def get_heater_status(self):

        # address for the rest api
        url = "http://192.168.178.44:5000/get_status"

        # send out the actual request to the api
        response = requests.get(url=url)
        status = response.text

        return status

    def post_heater_status(self, status):

        # address for the rest api
        url = "http://192.168.178.44:5000/post_status"

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
