import appdaemon.plugins.hass.hassapi as hass

class ListenState(hass.Hass):
    """
    Type of class:
    - State Listener

    Method called:
    - Print to log: "Hey, Listen!"

    Test this class by manually setting a test state
    -> hass web ui -> developer tools -> state -> type "person.yongshi" -> state: 'online' -> set state

    Technically a state change is still an event under the hood, although of a special kind and they all follow the event "state_changed".
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # tells appdaemon we want to call a certain method when a certain entity ("person.yongshi") changes state. 
        # in our case we can test this by manually changing the state of our current user 
        # (recognizable by the 'person.' before the user name)
        self.listen_state(self.state_changed, "person.yongshi")

    # the method that is called when the state changes
    def state_changed(self, entity, attribute, old, new, kwargs):

        # Now let's print a message when this function is called. Add the following line
        self.log(f"Hey, Listen!")
        self.log(f"The state of entity {entity} changed from {old} to {new}!")

        # do something based on the new state
        # if new == "new":
        #     self.call_service("light/turn_on", entity_id = "light.arilux_rgb_led_controller", brightness = 255)
        # else:
        #     self.call_service("light/turn_off", entity_id = "light.arilux_rgb_led_controller")