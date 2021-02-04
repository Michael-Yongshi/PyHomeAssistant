# Active AC Relay
active requestor checking status in HASS in order to determine to switch something on or off
i.e. check energy use of a certain group and shut off the car charger if energy use goes beyond a certain point.

# check with HASS api smart meter data
# deactive ac relay if smart meter indicates crossing limits of the group (i.e. 10A; normal limit of a house here is 16A per group)
# reactives ac relay if smart meter indicates lowering of power below a safe point (i.e. 6A; as AC uses 3,6 maximum so its safe to activate without crossing the upper 10A limit)

evse
https://www.hackster.io/news/raspberry-pi-hat-is-an-electric-vehicle-charger-controller-55c3a585689f
