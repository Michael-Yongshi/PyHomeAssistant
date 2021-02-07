import RPi.GPIO as GPIO

# set gpio wires
wire1 = 4
wire2 = 16
wire3 = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(wire1, GPIO.OUT)
GPIO.setup(wire2, GPIO.OUT)
GPIO.setup(wire3, GPIO.OUT)


def set_speed(speed):
    """
    Code to set the speed of the fan by setting the two relays through GPIO output wires in a certain combination
    
    All wires off means fan off
    Only wire 1 means setting 1
    Wire 1 and 2 means setting 2
    Wire 1 and 3 means setting 3

    """

    if speed == 0:
        GPIO.output(wire1, False)
        GPIO.output(wire2, False)
        GPIO.output(wire3, False)

    elif speed == 1:
        GPIO.output(wire1, True)
        GPIO.output(wire2, False)
        GPIO.output(wire3, False)

    elif speed == 2:
        GPIO.output(wire1, True)
        GPIO.output(wire2, True)
        GPIO.output(wire3, False)

    elif speed == 3:
        GPIO.output(wire1, True)
        GPIO.output(wire2, False)
        GPIO.output(wire3, True)
    
    else:
        pass

def read_speed():
    """
    Checks the wires on GPIO to see which setting is currently active

    All wires off means fan off
    Only wire 1 means setting 1
    Wire 1 and 2 means setting 2
    Wire 1 and 3 means setting 3

    if for some reason both wires are on, it will return setting 3
    """

    if GPIO.read(wire1) == True and GPIO.read(wire3) == True:
        speed = 3

    elif GPIO.read(wire1) == True and GPIO.read(wire2) == True:
        speed = 2

    elif GPIO.read(wire1) == True:
        speed = 1

    else:
        speed = 0
    
    return speed

if __name__ == '__main__':

    # check if settings work
    print(f"Set setting to 1")
    set_speed(1)

    print(f"Current setting is {read_speed()}")

    print(f"Set setting to 2")
    set_speed(2)

    print(f"Current setting is {read_speed()}")

    print(f"Set setting to 3")
    set_speed(3)

    print(f"Current setting is {read_speed()}")

    print(f"Set setting to 0")
    set_speed(0)

    print(f"Current setting is {read_speed()}")