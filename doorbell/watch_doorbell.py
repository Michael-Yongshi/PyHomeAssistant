import appdaemon.plugins.hass.hassapi as hass

class WatchDoorbell(hass.Hass):
    """
    Type of class:
    - MQTT Listener

    Method called:
    - Create message and send to the telegram bot
    """

    def initialize(self):

        # tells appdaemon we want to call a certain method when a certain MQTT state changed. 
        self.listen_state(self.doorbell_change, "sensor.mqtt_doorbell_status")

    def doorbell_change(self, entity, attribute, old, new, kwargs):
        
        # send a message when doorbell rang
        if new == "Ringing":
            message = f"I heard that someone is at the door!"

        # doorbell blocks for 10 seconds after ringing
        elif new == "Waiting":
            message = f"Doorbell finished ringing!"

        self.event_happened(message)

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