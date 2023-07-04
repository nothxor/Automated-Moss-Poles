# ----- IMPORT -----

from machine import ADC, Pin
import time
import ntptime
import uasyncio

# Local imports from other files in the same dir
from system import System
from plant import Plant
import config






# ----- INITIALIZATION -----


plantList = []

# ADC = 26, Relay = 16, min = 47500, max = 55245, moisture threshold = config.threshold, moisture 'dry' threshold = config.dryThreshold
plantList.append(Plant(26, 16, 47500, 55245, config.threshold, config.dryThreshold))
# ADC = 27, Relay = 17, min = 47300, max = 55300, moisture threshold = config.threshold, moisture 'dry' threshold = config.dryThreshold
plantList.append(Plant(27, 17, 47300, 55300, config.threshold, config.dryThreshold))
# ADC = 28, relay = 18, min = 47000, max = 55000, moisture threshold = config.threshold, moisture 'dry' threshold = config.dryThreshold
plantList.append(Plant(28, 18, 47000, 55000, config.threshold, config.dryThreshold))



# Initialize the system.


# Add plants to system
# System(plantList, magnetID, valveID)
system = System(plantList, 15, 13)

# Connect to the wifi.
system.wlanConnect()

# Initialize local time
print(time.localtime())
ntptime.settime()
print(time.localtime())



# MQTT
system.main()



# ----- ASYNC SETUP -----

loop = uasyncio.get_event_loop()

loop.create_task(system.runTasks(loop))

loop.run_forever()