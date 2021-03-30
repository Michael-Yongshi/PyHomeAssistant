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

        try:

            logging.info(f"Setting status to {status}")
            if status == 0:
                self.channel1.off()
                self.channel2.off()
                self.channel3.off()

            elif status == 1:
                self.channel1.on()
                self.channel2.off()
                self.channel3.off()
            
            else:
                logging.info(f"Received invalid status {status}.")

                return status
            
            logging.info(f"Set status to {status}!")

            # Wait for heater to process the change before accepting a new change
            time.sleep(1)

            return status
        
        except:

            logging.info(f"Couldnt set status {status}.")
            return -1
