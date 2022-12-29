import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

import mqttapi as mqtt

class WatchFan(mqtt.Mqtt, hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - Post to api of fan-pi to switch on ventilator with speed x
    
    Test this class by firing a test event
    -> hass web ui -> developer tools -> events -> type "FAN_OVERRIDE -> fire event

    add data like below and replace x with 0 - 3 (0 means stop override)
    {'speed': x}
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # override set topic is a queue to take commands and always gets reset back to 99 after a command is taken
        self.topic_override_set = "fan/override/set"
        # override status topic is the current status of the override
        self.topic_override_status = "fan/override/status"
        self.topic_override_timeleft = "fan/override/timeleft"

        # keep track of timeslot to allow for user adjustments in between program slots
        self.last_timeslot_end = 0
        self.last_fan_status = None

        # Home assistant parameters
        self.current_program = self.set_program()

        # Were keeping track of an override variable to keep override only on for a certain amount of time
        self.override_expiration = datetime.datetime.now()
        self.override_interval = 30

        # call a certain method when mqtt updates are available.
        self.listen_state(self.override, "sensor.mqtt_fan_override_set")

        # enforce determining setting even if humidity is unchanged every minute
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    # the method that is called when someone wants to override fan setting from home assistant itself
    def override(self, entity, attribute, old, new, kwargs):

        # immediately reset override command flag in mqtt to gather additional inputs
        self.mqtt_publish(topic = self.topic_override_set, payload = 99, qos = 1)

        status_new = int(new)
        status_old = int(self.get_fan_speed())

        current_time = datetime.datetime.now()

        # disregard a reset of the override command topic to value 99
        if status_new == 99:

            # disregard
            return

        # persistent override is requested
        elif status_new == 8:

            # no override expiration
            self.override_expiration = datetime.datetime(9999, 1, 1)
            self.mqtt_publish(topic = self.topic_override_status, payload = "Persistent Override", qos = 1)
            self.event_happened(f"Fan override persists!")

        # check if requested to go back to automatic programming
        elif status_new == 9:

            # disable override by setting expiration to current time
            self.override_expiration = current_time
            self.mqtt_publish(topic = self.topic_override_status, payload = "Automatic Programming", qos = 1)
            self.event_happened(f"Fan override lifted!")

            # immediately run automatically setting the fan as override is stopped
            self.determine_setting(kwargs)

        # temporary override is requested. determining which type
        elif status_new in [0,1,2,3]:

            # if override is already active (and speed is the same as previous override) extend the override
            if status_new == status_old and self.override_expiration > current_time:

                # extend the override parameter
                self.override_expiration += datetime.timedelta(minutes=self.override_interval)
                pretty_time = self.pretty_time(self.override_expiration)
                self.event_happened(f"Someone requested fan override, extending the override by {self.override_interval} minutes to {pretty_time}!")

            # override is currently not active (or for a different speed) so override is set anew
            elif status_new == 0:

                # override to shut off the fan for longer period of time
                self.override_expiration = current_time + datetime.timedelta(days=1)
                self.post_fan_speed(status_new)
                pretty_time = self.pretty_time(self.override_expiration)
                self.event_happened(f"Someone requested stopping the fan, shutting off the fan until {pretty_time}!")

            else:
                # new override
                self.override_expiration = current_time + datetime.timedelta(minutes=self.override_interval)
                self.post_fan_speed(status_new)
                pretty_time = self.pretty_time(self.override_expiration)
                self.event_happened(f"Someone requested fan override, setting speed {status_old} => {status_new} until {pretty_time}!")
            
            # publish override to MQTT
            time_left = self.time_left()
            self.mqtt_publish(topic = self.topic_override_status, payload = "Temporary Override", qos = 1)
            self.mqtt_publish(topic = self.topic_override_timeleft, payload = f"{time_left}", qos = 1)

        else:
            self.log(f"Error, no valid input received: {status_new}")

        self.log(f"Current date and time is: {current_time}")

    # determining the setting for the fan based on override expiration
    def determine_setting(self, kwargs):
        """
        Check logic to see if target speed should change on the thermostat
        """

        # get fanspeed state
        current_speed = self.get_fan_speed()
        # self.log(f"Fan speed is {current_speed}")

        current_time = datetime.datetime.now()

        # check if override is active
        if self.override_expiration >= current_time:

            # publish override to MQTT
            time_left = self.time_left()
            self.mqtt_publish(topic = self.topic_override_timeleft, payload = f"{time_left}", qos = 1)

            return

        else:
            # make sure override status is on auto
            self.mqtt_publish(topic = self.topic_override_status, payload = "Automatic programming", qos = 1)



        # reload user determined program
        self.current_program = self.set_program()

        # get current and target values
        current_timeslot = self.get_current_timeslot(current_time)
        current_timeslot_end = current_timeslot["end"]
        program_target = current_timeslot["speed"]
        self.log(f"Programming target speed is {program_target}, while current target speed is {current_speed}")

        # check if we already programmed this timeslot before (we will only once, so user can still change it)
        if self.last_timeslot_end != current_timeslot_end:

            # register that we now programmed this timeslot
            self.last_timeslot_end = current_timeslot_end

            # only set new speed if its different
            if program_target != current_speed:
                # set new target speed
                self.post_fan_speed(speed=program_target)
                self.event_happened(f"Set new fan speed to {program_target}, according to the program")

            else:
                self.event_happened(f"New timeslot, but target fan speed is already set correctly to {program_target}")

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
                "speed": 1
            },
            # morning
            {
                "end": "12:00:00",
                "speed": 1
            },
            # afternoon
            {
                "end": "17:00:00",
                "speed": 1
            },
            # evening
            {
                "end": "21:00:00",
                "speed": 0
            },
        ]

        user_program = []

        try:
            # Iterate over user settings
            for timeofday in ['night', 'morning', 'afternoon', 'evening']:

                # get user settings for this time of day
                timeslot_sensor = f"input_datetime.fan_{timeofday}_timeslot_end"
                timeslotend = self.get_state(timeslot_sensor)
                # self.event_happened(f"timeslot sensor is {timeslot_sensor} with value {timeslotend}")

                speed_sensor = f"input_number.fan_{timeofday}_speed"
                speed_string = self.get_state(speed_sensor)
                # self.event_happened(f'speed is {speed_string}')
                speed = int(speed_string[0])
                # self.event_happened(f'speed sensor is {speed_sensor} with value {speed}')

                timeslotdict = {
                    "end": timeslotend,
                    "speed": speed,
                }

                user_program += [timeslotdict]
                # self.event_happened(f"Added timeslot {timeofday} as {timeslotdict}!")

            program = user_program
            # self.event_happened(f"Set user program!")

        except:
            program = default_program
            self.event_happened(f"Couldn't set user program, reverting to default program")

        # add last timeslot until midnight and use the first timeslot as speed
        timeslotdict = {
            "end": "23:59:59",
            "speed": program[0]["speed"],
        }
        program += [timeslotdict]

        return program

    def time_left(self):

        current_time = datetime.datetime.now()

        time_left_delta = self.override_expiration - current_time
        time_left_str = self.pretty_time_delta(time_left_delta.total_seconds())

        return time_left_str

    def pretty_time(self, datetime):

        # Format datetime string
        pretty_t = datetime.strftime("%H:%M")

        return pretty_t

    def pretty_time_delta(self, seconds):

        seconds = int(seconds)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        if days > 0:
            return f"{days}d" #{hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h" #{minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m" #{seconds}s"
        else:
            return f"{seconds}s"

    def get_fan_speed(self):
        """
        get the current speed of the fan
        """

        # get hass sensor data
        current_speed = int(self.get_state("sensor.mqtt_fan_status"))

        return current_speed

    def post_fan_speed(self, speed):

        self.mqtt_publish(topic = "fan/set", payload = speed, qos = 1)

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