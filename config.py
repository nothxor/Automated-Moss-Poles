import ubinascii
import machine


# WIFI

localIP = '' #The IP of your Raspberry Pi Pico
homeAssistantIP = '' # The IP of your Home Assistant server

SSID = '' # SSID of your wifi
pw = '' # Password to your wifi

subnetMask = '' # Subnet mask of your LAN
gateway = '' # Gateway address of your LAN
DNS = '' # DNS Server to use

maxWait = 30


# PLANTS
threshold = 60
dryThreshold = 45
dryCycle = 4

# PUMPS (Which hours to run between so as not to disturb)
# Note that these values are in GMT, offset manually for your timezone.
pumpStartForTheDay = 8
pumpStopForTheDay = 17

# MQTT

mqttUser = '' # Username to connect to your MQTT Broker
mqttPw = '' # Password to connect to your MQTT Broker

MQTT_BROKER = homeAssistantIP
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SUBSCRIBE_TOPIC = b"/home/plants/"
PUBLISH_TOPIC = b"/home/plants/"

publish_interval = 5


# Pump variables
numIntervals = 3 # Number of times to run the pump on each 'run pump trigger'
pumpOnTimer = 10 # seconds
pumpIntervalTimer = 20 # seconds
pumpSleepAfterRunTimer = 900 # seconds