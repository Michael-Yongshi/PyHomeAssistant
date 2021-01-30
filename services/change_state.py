
# The way you change the state of an entity in AppDaemon is the same as in Home Assistant: you call a service. 
# Changing the state of the entity directly does nothing but change the value in software! 
# You must use the service to physically change the state of the device. 

import appdaemon.plugins.hass.hassapi as hass

class ServiceStateChange(hass.Hass):
    """
    Type of class:
    - Service script

    Method called:
    - Changes state of entity 'person.yongshi'

    Test this class
    """

    # Next, we will define our initialize function, which is how AppDaemon starts our app. 
    def initialize(self):

        # restrict running only when you are called

    def run(self):

        if new == "new":
            self.call_service("light/turn_on", entity_id = "light.arilux_rgb_led_controller", brightness = 255)
        
            # Now let's print a message when this function is called. Add the following line
            self.log(f"Hey, Service script ran!")
            self.log(f"The state of entity {entity} changed from {old} to {new}!")

        else:
            self.call_service("light/turn_off", entity_id = "light.arilux_rgb_led_controller")