import RPi.GPIO as GPIO

# set gpio wires
wire1 = 16
wire2 = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(wire1, GPIO.OUT)
GPIO.setup(wire2, GPIO.OUT)


def set_speed(speed):
    """
    Code to set the speed of the fan by setting the two relays through GPIO output wires in a certain combination
    
    Both wires off means setting 1
    Only wire 1 on means setting 2
    Only wire 2 on means setting 3

    both wires is ???
    """

    if speed == 1:
        GPIO.output(wire1, False)
        GPIO.output(wire2, False)

    elif speed == 2:
        GPIO.output(wire1, True)
        GPIO.output(wire2, False)

    elif speed == 3:
        GPIO.output(wire1, False)
        GPIO.output(wire2, True)
    
    else:
        pass

def read_speed():
    """
    Checks the wires on GPIO to see which setting is currently active

    Both wires off means setting 1
    Only wire 1 on means setting 2
    Only wire 2 on means setting 3

    if for some reason both wires are on, it will return setting 3
    """

    if GPIO.read(wire2) == True:
        speed = 3

    elif GPIO.read(wire1) == True:
        speed = 2

    else:
        speed = 1
    
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
