import appdaemon.plugins.hass.hassapi as hass
import datetime


class WatchNightHeater(hass.Hass):
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

        # loop method to determine if target temp needs to change
        # self.run_minutely(self.determine_setting, datetime.time(0, 0, 0))
        self.run_daily(self.heater_on, datetime.time(23, 0, 0))
        self.run_daily(self.heater_off, datetime.time(7, 0, 0))

    def heater_on(self, kwargs):
        self.call_service("climate/set_hvac_mode", entity_id=self.climate_entity, hvac_mode="heat")
        self.event_happened(f"Turned on electric heater")

    def heater_off(self, kwargs):
        self.call_service("climate/set_hvac_mode", entity_id=self.climate_entity, hvac_mode="off")
        self.event_happened(f"Turned off electric heater")

    def event_happened(self, message):
        """
        the method that is called when an event happens
        """

        # log the message before sending it
        self.log(message)

        # Call telegram message service to send the message from the telegram bot
        # self.call_service(
        #     "telegram_bot/send_message", message=message,
        # )