import appdaemon.plugins.hass.hassapi as hass

class WatchEnergy(hass.Hass):
    """
    Type of class:
    - State Listener

    Method called:
    - Set light.decorative_garden based on rising and setting of the sun

    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # define the actual (light) entities used in home assistant
        self.power_prod = "sensor.power_production"
        self.power_cons = "sensor.power_consumption"

        self.listen_state(self.send_message, self.power_prod)

    def send_message(self):

        message = f"Overflow of electricity production!"

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            "telegram_bot/send_message", message=message,
        )