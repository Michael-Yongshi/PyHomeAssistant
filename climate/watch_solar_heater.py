import appdaemon.plugins.hass.hassapi as hass
import datetime


class WatchSolarHeater(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - update state of 'climate' entity based on solar yield

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # Home assistant parameters
        self.climate_entity = "climate.electric_heater"
        self.current_temp = 20
        self.target_temp = 20
        self.solar_yield_entity = "sensor.grid_power"

        self.rolling_checks = ["off","off","off"]

        # loop method to determine if target temp needs to change
        self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))

    def determine_setting(self, kwargs):
        """
        Check logic to see if heater needs to be turned on based on solar yield
        its assumed the thermostat itself arranges the actual turning on of the heater
        """

        # Add a rolling check if enough solar energy or too little
        solar_yield = int(self.get_state(self.solar_yield_entity))
        self.event_happened(f"solar yield is {solar_yield}")

        if solar_yield >= 200:

            self.rolling_checks = self.rolling_checks[1:] + ["heat"]
            self.event_happened(f"New rolling checks: {self.rolling_checks}")

        else:
            self.rolling_checks = self.rolling_checks[1:] + ["off"]
            self.event_happened(f"New rolling checks: {self.rolling_checks}")

        # # Get status of the climate entity itself (not the action, this can differ depending on temperature)
        # heater_status = self.get_state(self.climate_entity, attribute="operation_mode")
        # self.event_happened(f"heater status = {heater_status}")

        # Turn on if solar energy is enough and heater is still off
        if self.rolling_checks == ["heat", "heat", "heat"]:
        # if self.rolling_checks == ["heat", "heat", "heat"] and heater_status == "off":
            self.call_service("climate/set_hvac_mode", entity_id=self.climate_entity, hvac_mode="heat")
            self.event_happened(f"Turned on electric heater, solar yield = {solar_yield}")

        # vice versa
        # elif self.rolling_checks == ["off", "off", "off"] and heater_status == "heat":
        elif self.rolling_checks == ["off", "off", "off"]:
            self.call_service("climate/set_hvac_mode", entity_id=self.climate_entity, hvac_mode="off")
            self.event_happened(f"Turned off electric heater, solar yield = {solar_yield}")

        # ignore if not stable reading
        else:
            pass

    def event_happened(self, message):
        """
        the method that is called when an event happens
        """

        # log the message before sending it
        self.log(message)

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            "telegram_bot/send_message", message=message,
        )