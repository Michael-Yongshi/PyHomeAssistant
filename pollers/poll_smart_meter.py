# PySmartMeter

## use dedicated p1 smart meter pi zero to convert serial data and open to polling by home assistant




### Home assistant
# Example configuration.yaml entry for remote (TCP/IP, i.e., via ser2net) connection to host which is connected to Smartmeter

sensor:
  - platform: dsmr
    host: 192.168.1.13
    port: 2001
    dsmr_version: 5

group:
  meter_readings:
    name: Meter readings
    entities:
      - sensor.energy_consumption_tarif_1
      - sensor.energy_consumption_tarif_2
      - sensor.energy_production_tarif_1
      - sensor.energy_production_tarif_2
      - sensor.gas_consumption
