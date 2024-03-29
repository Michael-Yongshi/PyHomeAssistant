"""
Not used, moved to HASS (watch_thermostat)

depends on thermostat.service in order to get run on reboot of the device
"""

import os
import json
import time
import datetime
import logging
from time import daylight, strptime
from queue import Queue

from paho.mqtt import client as mqtt_client

# temperature sensor communicates through adafruit protocol
import adafruit_dht

# heater relay operates by gpio signal
import gpiozero

""" TODO
mqtt push temperature and heating status to home assistant

rest api to receive commands to activate heating or activate vacation mode
rest api to change configuration
"""

# MQTT stuff
broker = '192.168.178.37'
port = 1883
client_id = 'rpi-fuse-pymqtt'
username = "mqttpublisher"
password = "publishmqtt"

def connect_mqtt():

    def on_connect(client, userdata, flags, rc):

        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.info("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)

    return client

def publish(topic, value, client):

    # publish it
    result = client.publish(topic, value)

    # first item in result array is the status, if this is 0 then the packet is send succesfully
    if result[0] == 0:
        logging.info(f"Send `{value}` to topic `{topic}`")
    
    # if not the message sending failed
    else:
        logging.info(f"Failed to send message to topic {topic}")


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

        # initialize
        self.thermometer = Thermometer()
        self.heater = Heater()

        # set up mqtt client
        self.client = connect_mqtt()

        # start loop, this will process the actual collection and sending of the messages
        self.client.loop_start()

        # publish sensor data every second    
        self.msg_count = 0

        logging.debug('Thermostat object is initiated')

    def run(self):

        try:
            while True:
                logging.info(f"-----Starting Process-----")
                self.process()
                logging.info(f"-----Finished Process-----\n")
                
                # delay for a while
                time.sleep(self.delay)  
        except:
            logging.critical("Thermostat stopped unexpectedly!")

    def process(self):

        # set settings from settings file
        self.days = self.load_json("days")
        self.programs = self.load_json("programs")
        self.bound = 0.5
        
        # get sensor data
        temp = self.thermometer.get_temp()
        humid = self.thermometer.get_humid()
        status = self.heater.get_status()

        # determine if change to heater is needed
        self.determine_setting(temp, humid, status)

        # publish
        publish("living/humidity", humid, self.client)
        publish("living/temperature", temp, self.client)
        publish("heater/status", status, self.client)
        
        # finish off with adding to the message count
        self.msg_count += 1    

    def determine_setting(self, temp, humid, status):

        # get target temperature based on program
        target_temp = self.get_target_temp()
        lower_bound = target_temp - self.bound
        upper_bound = target_temp + self.bound

        # if heater is on (1), turn off only when temperature reaches the upper bound
        if status == 1:
            
            if temp >= upper_bound:
                logging.info(f"Temperature ({temp}) rose above upper bound ({upper_bound})")
                self.heater.switch.off()
                logging.info(f"Turned off heater")
            else:
                logging.info(f"Temperature ({temp}) is still below upper bound ({upper_bound})")
        
        # if heater is off, turn on only when temperature reaches the lower bound
        # (to prevent turning the heater on or off to often)
        if status == 0:
            
            if temp < lower_bound:
                logging.info(f"Temperature ({temp}) fell below lower bound ({lower_bound})")
                self.heater.switch.on()
                logging.info(f"Turned on heater")
            else:
                logging.info(f"Temperature ({temp}) is still above lower bound ({lower_bound})")

    def get_target_temp(self):
        
        # get current day and associated program
        current_day = datetime.datetime.today().weekday()
        current_program_number = self.days[current_day]
        logging.info(f"Loading program {current_program_number}")

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
                    logging.info(f"Target temperature is {target_temp}")

                    break

            # if no target temperature is set, restart this progress until it is set
        
        return target_temp

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

        print(f"Temperature is {temperature}")
        logging.info(f"Read temperature {temperature}")

        return temperature

    def get_humid(self):

        # DHR sensor has a tendency to have timing errors, so we retry on this specific error until a valid return is received
        while True:
            # try to get a valid read
            try:
                humidity = self.sensor.humidity

            # continue in the while loop if an error is returned
            except RuntimeError:
                continue

            # Breaks if code reaches this part, so only if try succeeded
            break

        print(f"humidity {humidity}")
        logging.info(f"Read humidity {humidity}")

        return humidity

class Heater(object):
    """
    Heating is basically an on/off relay
    Used for heaters that only switch on and off instead of the newer modulating relays

    The self.switch variable contains a on() and off() method to manipulate the heater.
    so calling 'heater.switch.on()' turns the heater on.

    """

    def __init__(self):
        
        # grove relay is default open, so active_high needs to be set to True (close if signal is given)
        self.switch = gpiozero.OutputDevice(pin=20, active_high=True)

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
            logging.info(f"Read heater status as {status}")
            return status

        except:
            logging.error(f"Couldn't read heater!")
            return -1

if __name__ == '__main__':
    
    # thermometer = Thermometer()
    # thermometer.get_temp()

    # heater = Heater()
    # heater.switch.on()
    # heater.get_status()
    # time.sleep(1)
    # heater.switch.off()

    thermostat = Thermostat()
    thermostat.run()