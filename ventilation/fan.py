
import gpiozero
import time
import logging

class Fan(object):
    """
    Provdes calls to interface with the fan
    """

    def __init__(self):
        """
        Default fans (in NL) work on a 3 input basis, which means it expects a combination of power on L1, L2 and L3.
        You can find often a switch in the kitchen and/or living room to control it. from those switches the Lx cables run to the fan

        L1:                 lowest speed (1)
        L1 and L2:          medium speed (2)
        L1(, L2) and L3:    highest speed (3)

        """

        # Pi relay hat uses below pins, active_high means the relays are by default turned on (in our case not ideal)
        self.channel1 = gpiozero.OutputDevice(pin=26, active_high=False)
        self.channel2 = gpiozero.OutputDevice(pin=20, active_high=False)
        self.channel3 = gpiozero.OutputDevice(pin=21, active_high=False)

    def test_relay(self):

        try:

            # cycle those relays twice to see if it works
            logging.info("Checking relays...")
            
            for x in [0,1]:
                self.channel1.on()
                time.sleep(1)
                self.channel1.off()

                self.channel2.on()
                time.sleep(1)
                self.channel2.off()

                self.channel3.on()
                time.sleep(1)
                self.channel3.off()

            logging.info("Checking relays finished")
        except:
            logging.error(f"Couldn't check relays!")

    def get_speed(self):
        """
        Check the current status of the ventilation speeds and returns result
        """

        """
        Checks the channels on GPIO to see which setting is currently active

        All channels off means fan off
        Only channel 1 means setting 1
        Channel 1 and 2 means setting 2
        Channel 1 and 3 means setting 3

        if for some reason all channels are on, it will return setting 3 (as its checked first)
        """

        try:
            #[1,x,1]
            print(self.channel1.value)
            print(self.channel2.value)
            print(self.channel3.value)

            if self.channel1.value == 1 and self.channel3.value == 1:
                speed = 3
            #[1,1,x]
            elif self.channel1.value == 1 and self.channel2.value == 1:
                speed = 2
            #[1,x,x]
            elif self.channel1.value == 1:
                speed = 1
            #[0,x,x]
            else:
                speed = 0
            logging.info(f"Read speed {speed}")

            return speed

        except:
            logging.error(f"Couldn't read speed!")

            return -1

    def set_speed(self, speed):

        try:

            logging.info(f"Setting speed to {speed}")
            if speed == 0:
                self.channel1.off()
                self.channel2.off()
                self.channel3.off()

            elif speed == 1:
                self.channel1.on()
                self.channel2.off()
                self.channel3.off()

            elif speed == 2:
                self.channel1.on()
                self.channel2.on()
                self.channel3.off()

            elif speed == 3:
                self.channel1.on()
                self.channel2.off()
                self.channel3.on()
            
            else:
                logging.info(f"Received invalid speed {speed}.")

                return speed
            
            logging.info(f"Set speed to {speed}!")

            # Wait for fan to process the change before accepting a new change
            time.sleep(1)

            return speed
        
        except:

            logging.info(f"Couldnt set speed {speed}.")
            return -1

if __name__ == '__main__':
    
    fan = Fan()
    fan.test_relay()