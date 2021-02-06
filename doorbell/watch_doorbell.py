import appdaemon.plugins.hass.hassapi as hass

class WatchDoorbell(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - Create message and send to the telegram bot
    
    Test this class by firing a test event
    -> hass web ui -> developer tools -> events -> type "DOORBELL_PRESSED" -> fire event
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.event_happened, "DOORBELL_PRESSED")

    # the method that is called when an event happens
    def event_happened(self, event_name, data, kwargs):

        date_time = data["time"][0:18]
        message = f"I heard that someone is at the door! \nCurrent date and time is: {date_time}"
        
        # log the message
        self.log(message)
        self.log(f"data = {data}")

        # Call telegram message service to send the message from the telegram bot
        self.call_service(
            "telegram_bot/send_message", message=message,
        )