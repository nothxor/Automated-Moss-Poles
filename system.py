from machine import ADC, Pin
import machine
import utime
import time
import network
import uasyncio

from plant import Plant
from magnet import Magnet
from valve import Valve
import config

from umqtt.simple import MQTTClient

# ----- SYSTEM CLASS -----

class System:
    
    def __init__(self, plantList, magnetID, valveID):
        
        print("Initializing system...")
        
        Pin("LED", Pin.OUT).value(1)
        utime.sleep(1)
        Pin("LED", Pin.OUT).value(0)
        utime.sleep(2)
        
        self.homeAssIP = config.homeAssistantIP
        
        self.plantList = plantList
        self.plantCounter = 0
        
        # Create a magnet for checking if the lid is open
        self.magnet = Magnet(magnetID)
        
        # Create a valve for checking the water level
        self.floatValve = Valve(valveID)
        
        
        # Set correct ID's for all plants.
        for plant in self.plantList:
            plant.plantID = self.plantCounter
            self.plantCounter += 1
            
        self.mqttClient = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, keepalive = 120, user = config.mqttUser, password = config.mqttPw)
        
        # Values for MQTT
        self.last_publish = time.time()
        self.publish_interval = config.publish_interval


    def wlanConnect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # Prevent the wireless chip from activating power-saving mode when it is idle.
        wlan.config(pm = 0xa11140)

        # Set a static IP and setup subnet mask, gateway & DNS.
        wlan.ifconfig((config.localIP, config.subnetMask, config.gateway, config.DNS))

        # Connect to network using login details from config file.
        wlan.connect(config.SSID, config.pw)

        # Search for up to config.maxWait seconds for a network connection
        maxWait = config.maxWait
        while maxWait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            maxWait -= 1
            print("Waiting for connection...")
            utime.sleep(1)
            
        # Raise an error if unable to connect.
        if wlan.status() != 3:
            raise RuntimeError("Network connection failed.")
        else:
            print("Connected.")
            status = wlan.ifconfig()
            print('IP = ' + status[0])
    
    async def runTasks(self, loop):
        
        for plant in self.plantList:
            loop.create_task(plant.runSensor())
            loop.create_task(plant.runPump())
        
        loop.create_task(self.magnet.runMagnet())
        loop.create_task(self.floatValve.runValve())
        
        loop.create_task(self.mqttSend(self.last_publish, self.publish_interval))
        
        loop.create_task(self.runLED())
        
    
    # Blink the LED to show that everything works fine and that all the parts of the system are up and running (wifi, MQTT, sensors, pumps).
    async def runLED(self):
        
        while True:
            Pin("LED", Pin.OUT).value(0)
            await uasyncio.sleep(1)
            Pin("LED", Pin.OUT).value(1)
            await uasyncio.sleep(1)

    
    
    # MQTT
    
    def sub_cb(self, topic, msg):
        # Setup built in Pico LED as Output
        led = machine.Pin("LED", machine.Pin.OUT)
        
        print((topic, msg))
            
    # Currently not in use        
    def reset(self):
        print("Resetting...")
        time.sleep(5)
        machine.reset()
        
    def main(self):
        
        self.mqttConnect()

    def mqttConnect(self):
        print(f"Begin connection with MQTT Broker :: {config.MQTT_BROKER}")
        
        self.mqttClient.set_callback(self.sub_cb)
        self.mqttClient.connect()
        self.mqttClient.subscribe(config.SUBSCRIBE_TOPIC)
        
        print(f"Connected to MQTT Broker :: {config.MQTT_BROKER}, and waiting for callback function to be called!")
        
    async def mqttSend(self, last_publish, publish_interval):

        while True:
            self.mqttClient.check_msg()
            if (time.time() - last_publish) >= publish_interval:
                for plant in self.plantList:
                    
                    publishUndertopic = config.PUBLISH_TOPIC + str(plant.plantID) + "/humidity"
                    self.mqttClient.publish(publishUndertopic, str(plant.moisture).encode())
                    
                    publishUndertopic = config.PUBLISH_TOPIC + str(plant.plantID) + "/pump"
                    self.mqttClient.publish(publishUndertopic, str(plant.pumpStatus).encode())
                    
                publishUndertopic = config.PUBLISH_TOPIC + "valve"
                self.mqttClient.publish(publishUndertopic, str(self.floatValve.valveStatus).encode())
                    
                last_publish = time.time()
            
            # This code isn't on the publish_interval timeout, since it's very important to send it asap to Home Assistant
            # to trigger an automation there to turn the 230V off when the lid is opened.
            
            # A good change here would be to put this in an if statement and check if there's any change compared to some variable
            # that tracks the state of the door sensor, and only then send the status.
            publishUndertopic = config.PUBLISH_TOPIC + "door" 
            self.mqttClient.publish(publishUndertopic, str(self.magnet.magStatus).encode())
            
            
            await uasyncio.sleep(1)