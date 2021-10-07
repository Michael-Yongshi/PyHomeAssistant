"""
Contains logic to check and set a GPIO pin connected to a relay that turns the heater (CV / boiler / heatpump) on or off and request current status
"""

import time
import logging

# heater relay operates by gpio signal
import gpiozero

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

    def set_status(self, status):

    # try:
        logging.info(f"Setting status to {status}")
        if status == 1:
            self.switch.on()
        elif status == 0:
            self.switch.off()

        return status

    # except:
        logging.error(f"Couldn't set heater!")
        return -1