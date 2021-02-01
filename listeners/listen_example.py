import appdaemon.plugins.hass.hassapi as hass

class ListenExample(hass.Hass):
    """
    Type of class:
    - Event Listener

    Method called:
    - Log event and data
    
    Test this class by firing a test event or running emit_example.py
    -> hass web ui -> developer tools -> events -> type "EVENT_EXAMPLE" -> fire event
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # tells appdaemon we want to call a certain method when a certain event ("EVENT") is received. 
        self.listen_event(self.event_happened, "EVENT_EXAMPLE")

    # the method that is called when an event happens
    def event_happened(self, event_name, data, kwargs):

        # log the message
        self.log(f"Event {event_name} was just received with data: {data}")