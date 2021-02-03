import hassapi as hass

class ListenSun(hass.Hass):
    """
    Type of class:
    - Service Listener

    Method called:
    - Print to log: "Hey, Listen!"

    Method is called whenever the sun rises or sets (which is a built-in event trigger)
    See other built-in events here:
    https://www.home-assistant.io/docs/configuration/events/
    
    """

    def initialize(self):

        # we register two seperate callbacks, one for sunrise and one for sunset.
        self.run_at_sunrise(self.log_rise)
        self.run_at_sunset(self.log_set, offset=-900)

    def log_rise(self, kwargs):

        self.log(f"Hey, Listen!")
        self.log(f"Sun is now rising!")

    def log_set(self, kwargs):

        self.log(f"Hey, Listen!")
        self.log(f"Sun is now setting!")
