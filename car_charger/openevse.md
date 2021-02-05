# Passive openEVSE relay
Passive. Contains a rest api to switch on a 3 phase openevse car charger.

# check with HASS api smart meter data
# deactive ac relay if smart meter indicates crossing limits of the group (i.e. 10A; normal limit of a house here is 16A per group)
# reactives ac relay if smart meter indicates lowering of power below a safe point (i.e. 6A; as AC uses 3,6 maximum so its safe to activate without crossing the upper 10A limit)

OpenEVSE charger build:
single phase kit:
                https://store.openevse.com/collections/all-products/products/advanced-kit

3 phase wiring: https://store.openevse.com/products/standard-series-40a-component-kit
3 phase cable:  https://store.openevse.com/products/iec-mennekes-type-2-32a-3-phase-ev-cable-7-5m-25
cable fix x2:   https://store.openevse.com/collections/all-products/products/cable-gland-cg-16
enclosure:      https://store.openevse.com/collections/all-products/products/custom-enclosure-poly-carbonate-standard

build
https://openevse.dozuki.com/Guide/Current+-+v5+OpenEVSE+Advanced+and+Value/26?lang=en

first time setup
https://guide.openenergymonitor.org/integrations/openevse/

https://community.openenergymonitor.org/t/3ph-openevse-firmware-5-0-0-eu-vs-4-8/8384
