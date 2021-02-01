# PySmartMeter

# https://computertotaal.nl/artikelen/overige-elektronica/slimme-meter-uitlezen-met-je-raspberry-pi/

# https://www.domoticz.com/wiki/Raspberry_Pi

# https://www.domoticz.com/wiki/Dutch_DSMR_smart_meter_with_P1_port

# https://www.home-assistant.io/integrations/dsmr/
# https://www.jpaul.me/2019/01/how-to-build-a-raspberry-pi-serial-console-server-with-ser2net/




#### Pull event from Home Assistant
# https://www.home-assistant.io/integrations/rest/

# The Rest sensor
# Home Assistant P1 addon to poll ser2net on the pi connected to the smart meter.



### reading p1 data on pi
# https://github.com/ndokter/dsmr_parser
pip3 install dsmr_parser

from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V4

serial_reader = SerialReader(
    device='/dev/ttyUSB0',
    serial_settings=SERIAL_SETTINGS_V4,
    telegram_specification=telegram_specifications.V4
)

for telegram in serial_reader.read():
    print(telegram)  # see 'Telegram object' docs below