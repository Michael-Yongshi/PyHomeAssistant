import appdaemon.plugins.hass.hassapi as hass

class ListenEvent(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - Print to log: "Hey, Listen!"
    
    Test this class by firing a test event
    -> hass web ui -> developer tools -> events -> type "EVENT" -> fire event
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.event_happened, "EVENT")

    # the method that is called when an event happens
    def event_happened(self, event_name, data, kwargs):

        # Now let's print a message when this function is called. Add the following line
        self.log(f"Hey, Listen!")
        self.log(f"I saw that event {event_name} is fired!")