import os
import json
import time
import datetime
import logging
from time import daylight

# heater relay operates by gpio signal
import gpiozero

# temperature sensor communicates through 1wire protocol
# import w1thermsensor

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

        # set a delay to avoid continuously running
        self.delay = 10

        # set settings from settings file
        self.days = self.load_json("days")
        self.programs = self.load_json("programs")

        print(self.days)

        logging.debug('Thermostat object is initiated')

    def process(self):

        # get current day and associated program
        current_day = datetime.datetime.today().weekday()
        current_program_number = self.days[current_day]
        logging.info(f"Loading program {current_program_number}")

        # load program
        current_program = self.programs[str(current_program_number)]
        logging.debug(f"Program loaded as: \n{current_program}")

        # check current target temperature
        target_temp = 0
        while target_temp == 0:
            
            # get current time
            current_time = datetime.time.now()

            logging.info(f"Searching for active timeslot... ({current_time})")
            for timeslot in current_program:

                # Convert timeslot 'end' to time type
                timeslot_time = datetime.datetime(timeslot["end"], "%h-%m-%s")

                # check if current time still falls within this timeslot
                if current_time <= timeslot_time:
                    logging.info(f"Active timeslot is {timeslot}")

                    # set timeslot temperature as current target
                    target_temp = timeslot["temp"]
                    logging.info(f"Target temperature is {current_program_number}")

            # if no target temperature is set, restart this progress until it is set

        # get current temperature
        thermometer = Thermometer()
        temp = thermometer.get_temp()

        # get heater status
        heater = Heater()
        status = heater.get_status()

        # if heater is on (1), turn off only when temperature reaches the upper bound
        if status == 1:
            if temp >= target_temp:
                logging.info(f"Target temperature rose above upper bound")
                heater.switch.off()
                logging.info(f"Turned off heater")
            else:
                logging.info(f"Target temperature still below upper bound")
        
        # if heater is off, turn on only when temperature reaches the lower bound
        # (to prevent turning the heater on or off to often)
        if status == 0:
            if temp < target_temp - 1:
                logging.info(f"Target temperature fell below lower bound")
                heater.switch.on()
                logging.info(f"Turned on heater")
            else:
                logging.info(f"Target temperature still within bounds")

        # delay for a while
        time.sleep(self.delay)

    def load_json(filename):
        """Load settings json"""

        path = os.path.join("~")

        # check if directory already exists, if not create it
        if not os.path.exists(path):
            print(f"cant find path '{path}'")

        else:
            complete_path = os.path.join(path, 'filename' + ".json")

            # open json and return as an array
            with open(complete_path, 'r') as infile:
                contents = json.load(infile)
        
            return contents

    def run(self):

        try:
            while True:
                self.process()
        except:
            logging.critical("Thermostat stopped unexpectedly!")

class Thermometer(object):
    """
    The thermometer is a termperature sensor on this device
    opens functions to read the temperature
    """

    def __init__(self):

        self.channelTemp = gpiozero.InputDevice(pin=4)

        logging.debug('Thermometer object is initiated')

    # def get_temp(self):
    # https://bigl.es/ds18b20-temperature-sensor-with-python-raspberry-pi/
    #     return self.channelTemp.value

class Heater(object):
    """
    The heater 
    """

    def __init__(self):
        """
        Heating is basically an on/off relay
        Used for heaters that only switch on and off instead of the newer modulating relays
        """
        
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

    def get_heating(self):
        """
        Check the current status of the heatings and returns result
        if relay = 1, then heating is on
        """

        try:
            heating = self.switch.value
            logging.info(f"Read heating {heating}")
            return heating

        except:
            logging.error(f"Couldn't read heating!")
            return -1

if __name__ == '__main__':
    
    heater = Heater()

    heater.test_relay()

    # thermostat = Thermostat()