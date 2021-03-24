import os
import json
import time
import datetime
import logging
from time import daylight, strptime

# heater relay operates by gpio signal
import gpiozero

# temperature sensor communicates through adafruit protocol
import adafruit_dht

""" TODO
mqtt push temperature and heating status to home assistant

rest api to receive commands to activate heating or activate vacation mode
rest api to change configuration
"""

class Thermostat(object):
    """
    Class that contains the logic for the heater to turn on and off at specific times of the day

    reads temperature of the room
    activates heater based upon temperature
    """

    def __init__(self):

        # set up logging
        logging.basicConfig(level=logging.DEBUG)
        
        # set a delay to avoid continuously running
        self.delay = 10

        # set settings from settings file
        self.days = self.load_json("days")
        self.programs = self.load_json("programs")

        print(self.days)

        # initialize thermometer
        self.thermometer = Thermometer()

        # initialize heater
        self.heater = Heater()

        logging.debug('Thermostat object is initiated')

    def run(self):

        # try:
        while True:
            self.process()
        # except:
        #     logging.critical("Thermostat stopped unexpectedly!")

    def process(self):

        # get current day and associated program
        current_day = datetime.datetime.today().weekday()
        current_program_number = self.days[current_day]
        logging.info(f"Loading program {current_program_number}")

        # load program
        current_program = self.programs[current_program_number]
        logging.debug(f"Program loaded as: \n{current_program}")

        # check current target temperature
        target_temp = 0
        while target_temp == 0:
            
            # get current time
            current_time = datetime.datetime.now() # .strftime("%H:%M:%S")
            current_year = current_time.year
            current_month = current_time.month
            current_day = current_time.day

            logging.info(f"Searching for active timeslot... ({current_time})")
            for timeslot in current_program:

                # Convert timeslot 'end' to time type
                time_from_string = datetime.datetime.strptime(timeslot["end"], "%H:%M:%S")
                timeslot_end = time_from_string.replace(year=current_year, month=current_month, day=current_day)
                # print(timeslot_end)

                # check if current time still falls within this timeslot
                if current_time <= timeslot_end:
                    logging.info(f"Active timeslot is {timeslot}")
                    print(f"current timeslot = {timeslot}")

                    # set timeslot temperature as current target
                    target_temp = timeslot["temp"]
                    logging.info(f"Target temperature is {current_program_number}")

                    break

            # if no target temperature is set, restart this progress until it is set

        # get current temperature
        temp = self.thermometer.get_temp()

        # get heater status
        status = self.heater.get_status()

        # if heater is on (1), turn off only when temperature reaches the upper bound
        if status == 1:
            if temp >= target_temp:
                logging.info(f"Target temperature rose above upper bound")
                self.heater.switch.off()
                logging.info(f"Turned off heater")
            else:
                logging.info(f"Target temperature still below upper bound")
        
        # if heater is off, turn on only when temperature reaches the lower bound
        # (to prevent turning the heater on or off to often)
        if status == 0:
            if temp < target_temp - 1:
                logging.info(f"Target temperature fell below lower bound")
                self.heater.switch.on()
                logging.info(f"Turned on heater")
            else:
                logging.info(f"Target temperature still within bounds")

        # delay for a while
        time.sleep(self.delay)

    def load_json(self, filename):
        """Load settings json"""

        path = os.path.expanduser('~')

        # check if directory already exists, if not create it
        if not os.path.exists(path):
            print(f"cant find path '{path}'")

        else:
            complete_path = os.path.join(path, filename + ".json")

            # open json and return as an array
            with open(complete_path, 'r') as infile:
                contents = json.load(infile)
        
            return contents

class Thermometer(object):
    """
    The thermometer is a termperature sensor on this device
    opens functions to read the temperature
    """

    def __init__(self):

        self.sensor = adafruit_dht.DHT22(pin=4)

        logging.debug('Thermometer object is initiated')

    def get_temp(self):

        # DHR sensor has a tendency to have timing errors, so we retry on this specific error until a valid return is received
        while True:
            # try to get a valid read
            try:
                temperature = self.sensor.temperature

            # continue in the while loop if an error is returned
            except RuntimeError:
                continue

            # Breaks if code reaches this part, so only if try succeeded
            break

        # print(f"Temperature is {temperature}")
        logging.info(f"Read DHT sensor {temperature}")

        return temperature

    def get_humid(self):

        humidity = self.sensor.humidity

        print(f"humidity {humidity}")
        logging.info(f"Read DHT sensor {humidity}")

        return humidity

class Heater(object):
    """
    Heating is basically an on/off relay
    Used for heaters that only switch on and off instead of the newer modulating relays

    The self.switch variable contains a on() and off() method to manipulate the heater.
    so calling 'heater.switch.on()' turns the heater on.

    """

    def __init__(self):
        
        self.switch = gpiozero.OutputDevice(pin=20, active_high=False)

        logging.debug('Heater object is initiated')

    def test_relay(self):

        try:

            # cycle those relays twice to see if it works
            logging.info("Checking relay...")
       
            for x in [0,10]:
                self.switch.on()
                time.sleep(1)
                self.switch.off()
                time.sleep(1)

            logging.info("Checking relays finished")
        except:
            logging.error(f"Couldn't check relays!")

    def get_status(self):
        """
        Check the current status of the heater and returns result
        if relay = 1, then heater is on
        """

        try:
            status = self.switch.value

            print(f"Heater status is {status}")
            logging.info(f"Read heater {status}")
            return status

        except:
            logging.error(f"Couldn't read heater!")
            return -1

if __name__ == '__main__':
    
    # heater = Heater()
    # heater.switch.on()
    # heater.get_status()
    # time.sleep(1)
    # heater.switch.off()

    # thermometer = Thermometer()
    # thermometer.get_temp()

    thermostat = Thermostat()
    thermostat.run()