import gpiozero
import time
import logging

def check_relay():

    try:

        channel1 = gpiozero.OutputDevice(pin=25)
        channel2 = gpiozero.OutputDevice(pin=28)
        channel3 = gpiozero.OutputDevice(pin=29)

        # cycle those relays twice to see if it works
        for x in [0,1]:
            channel1.on()
            time.sleep(1)
            channel1.off()

            channel2.on()
            time.sleep(1)
            channel2.off()

            channel3.on()
            time.sleep(1)
            channel3.off()
    
    except:
        logging.error(f"Couldn't check relays!")
    
def set_speed(speed):
    """
    Code to set the speed of the fan by setting the two relays through GPIO output channels in a certain combination
    
    All channels off means fan off
    Only channel 1 means setting 1
    Channel 1 and 2 means setting 2
    Channel 1 and 3 means setting 3

    Always all channels are set, even if its not strictly necessary 
    i.e. switching from setting 1 to 3 could be done by just setting channel 3, 
    but lets make sure the other channels are forced to the correct channel either way is off just in case
    """

    try:

        channel1 = gpiozero.OutputDevice(pin=25)
        channel2 = gpiozero.OutputDevice(pin=28)
        channel3 = gpiozero.OutputDevice(pin=29)

        if speed == 0:
            channel1.off()
            channel2.off()
            channel3.off()

        elif speed == 1:
            channel1.on()
            channel2.off()
            channel3.off()

        elif speed == 2:
            channel1.on()
            channel2.on()
            channel3.off()

        elif speed == 3:
            channel1.on()
            channel2.off()
            channel3.on()
        
        else:
            logging.info(f"Didn't set speed. Received speed {speed}.")
            return speed
        
        logging.info(f"Set speed {speed}!")
        return speed
    
    except:
        logging.error(f"Error, couldn't set speed {speed}")

def read_speed():
    """
    Checks the channels on GPIO to see which setting is currently active

    All channels off means fan off
    Only channel 1 means setting 1
    Channel 1 and 2 means setting 2
    Channel 1 and 3 means setting 3

    if for some reason all channels are on, it will return setting 3 (as its checked first)
    """

    try:

        channel1 = gpiozero.OutputDevice(pin=25)
        channel2 = gpiozero.OutputDevice(pin=28)
        channel3 = gpiozero.OutputDevice(pin=29)

        #[1,x,1]
        if channel1.value == 1 and channel3.value == 1:
            speed = 3

        #[1,1,x]
        elif channel1.value == 1 and channel2.value == 1:
            speed = 2

        #[1,x,x]
        elif channel1.value == 1:
            speed = 1

        #[0,x,x]
        else:
            speed = 0
        
        logging.info(f"Read speed {speed}")
        return speed

    except:
        logging.error(f"Couldn't read speed!")

if __name__ == '__main__':

    check_relays()

    # check if settings work
    set_speed(1)
    read_speed()

    set_speed(2)
    read_speed()

    set_speed(3)
    read_speed()

    set_speed(0)
    read_speed()