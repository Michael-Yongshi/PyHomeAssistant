import logging

# temperature sensor communicates through adafruit protocol
import adafruit_dht

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
