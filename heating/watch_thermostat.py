import appdaemon.plugins.hass.hassapi as hass
import datetime
import pytz
from pytz import utc

class WatchThermostat(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - update state of 'climate.central_heating' entity, attribute 'target_temperature' in order to influence the thermostat setting

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # Entities to influence
        self.entity = self.args["climate"]

        ###### User program

        # Toggle to turn programming on or off
        self.toggle = self.args["toggle"]
        self.timezone = pytz.timezone("Europe/Amsterdam")
        self.timezone = utc

        # helper format
        helper_type_temp = "input_number."
        helper_type_end = "input_datetime."
        self.helper_temp = helper_type_temp + "thermostat_temperature_"
        self.helper_end = helper_type_end + "thermostat_timeslot_"
        self.timeslotcategories = self.args["timeslots"]

        # variables to watch with initial value
        self.current_program = self.set_program()


        ###### Override method: Simple
        # only set temperature upon new timeslot
        self.last_timeslot_end = 0
        

        """
        Following call runs every minute to check if something needs to happen
        """
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

        self.determine_setting(kwargs=None)

    def determine_setting(self, kwargs):
        """
        Check logic to see if target temp should change on the thermostat
        """

        if self.get_state(self.toggle) != "on":
            return

        # get current datetime value
        current_time = datetime.datetime.now()

        # get current timeslot
        current_timeslot = self.get_current_timeslot(current_time)

        # get variables from timeslot data
        current_timeslot_end = current_timeslot["end"]
        program_target = current_timeslot["temp"]

        # get current value from entity
        current_target = self.get_state(self.entity, attribute="temperature")
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

        # reload user determined program
        self.current_program = self.set_program()

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

        user_program = []

        # Iterate over user settings
        for category in self.timeslotcategories:

            # get user settings for this time of day
            timeslot_sensor = self.helper_end + category
            timeslotend = self.get_state(timeslot_sensor)
            # self.event_happened(f"timeslot sensor is {timeslot_sensor} with value {timeslotend}")

            temp_sensor = self.helper_temp + category
            temp = self.get_state(temp_sensor)
            # self.event_happened(f'temp sensor is {temp_sensor} with value {temp}')
            # temp = int(self.get_state(f"mqtt_thermostat_{category}_temp"))

            timeslotdict = {
                "end": timeslotend,
                "temp": temp,
            }

            user_program += [timeslotdict]
            # self.event_happened(f"Added timeslot {category} as {timeslotdict}!")

        program = user_program
        # self.event_happened(f"Set user program!")

        # add last timeslot until midnight and use the first timeslot as temperature
        timeslotdict = {
            "end": "23:59:59",
            "temp": program[0]["temp"],
        }
        program += [timeslotdict]

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

    def pretty_datetime(self, datetime):

        # Format datetime string
        pretty_dt = datetime.strftime("day %d time %H:%M")

        return pretty_dt

    def post_target_temp(self, target_temp):

        self.call_service("climate/set_temperature", entity_id=self.entity, temperature=target_temp)
