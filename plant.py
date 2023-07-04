from machine import ADC, Pin
import uasyncio
import time

import config

# ----- PLANT CLASS -----

class Plant:
    
    def __init__(self, moisturePin, relayPin, minMoisture, maxMoisture, thresholdValue, dryThreshold):
        
        self.moisturePin = moisturePin
        self.relayPin = relayPin
        self.minMoisture = minMoisture
        self.maxMoisture = maxMoisture
        self.thresholdValue = thresholdValue
        self.dryThreshold = dryThreshold
        self.currentRead = 0
        self.moisture = 100
        self.pumpStatus = False
        self.currentCycle = 0
        
        # Temporary initialization value. (Gets initialized to a proper value as part of the system class constructor.)
        self.plantID = 0
        
        # Setup Pico pins to be used by the plant.
        self.soil = ADC(Pin(self.moisturePin))
        self.relay = Pin(self.relayPin, Pin.OUT)
        
        # Initialize pump to OFF.
        self.relay.value(1)

    async def runSensor(self):
        print(f'Running sensor on plant: {self.plantID}')
        
        while True:
            
            # Read the sensor.
            self.currentRead = self.soil.read_u16()
            
            # Convert the digital value to a percentage.
            self.moisture = (int)((self.maxMoisture - self.currentRead) * 100 / (self.maxMoisture - self.minMoisture))
            
            # Clean up extreme values.
            if self.moisture < 0:
                self.moisture = 0
            elif self.moisture > 100:
                self.moisture = 100
            
            # Calibrating purposes, comment out once your sensors are set up.
            # print(f"moisture on plant {self.plantID} is: " + "%.2f" % self.moisture +"% (adc: "+str(self.currentRead)+")")
            
            await uasyncio.sleep(1)            


    async def runPump(self):
        while True:
            await uasyncio.sleep(1)
            
            # If statement to make sure that we're in the right hours of the day (localtime[3] = the hour) to run the pumps (so we don't disturb sleep or whatever).
            if time.localtime()[3] >= config.pumpStartForTheDay and time.localtime()[3] <= config.pumpStopForTheDay:
            
                # If statement to see if we're in a regular cycle (with regards to moisture threshold) or if we're in a dry cycle (lower moisture threshold).
                # We use the dry cycle to make sure the moss poles get to dry out at times, mostly to prevent molding or similar issues.
                if self.currentCycle < config.dryCycle:
                    
                    # Final if statement to see if the moisture is actually below the threshold value (ie, run the pump).
                    if self.moisture < self.thresholdValue:
                        
                        numIntervals = 0
                        print(f'Moisture at {self.moisture}% - running pump on plant: {self.plantID} for {config.numIntervals} x {config.pumpOnTimer} seconds.')
        
                        while numIntervals < config.numIntervals:
                            
                            numIntervals += 1
                            
                            self.pumpStatus = True
                            self.relay.value(0)
                            await uasyncio.sleep(config.pumpOnTimer) # Run pump for config.pumpOnTimer seconds (to prevent flooding)
                            self.pumpStatus = False
                            self.relay.value(1)
                            if numIntervals == config.numIntervals:
                                break
                            else:
                                await uasyncio.sleep(config.pumpIntervalTimer)
                            
                        print(f'Moisture at {self.moisture}% - stopping pump on plant: {self.plantID} and sleeping system for {config.pumpSleepAfterRunTimer} seconds.')
                        await uasyncio.sleep(config.pumpSleepAfterRunTimer) # Sleep for config.pumpSleepTimer seconds to not constantly check/run the pump (also done to prevent flooding as the new moisture takes time to reach the sensor)   

                        self.currentCycle += 1 # Add one to the dry cycle.
                        
                elif self.currentCycle == config.dryCycle:
                    
                    if self.moisture < self.dryThreshold:
                        
                        numIntervals = 0
                        print(f'Moisture at {self.moisture}% - running pump on plant: {self.plantID} for {config.numIntervals} x {config.pumpOnTimer} seconds.')
        
                        while numIntervals < config.numIntervals:
                            
                            numIntervals += 1
                            
                            self.pumpStatus = True
                            self.relay.value(0)
                            await uasyncio.sleep(config.pumpOnTimer) # Run pump for config.pumpOnTimer seconds (to prevent flooding)
                            self.pumpStatus = False
                            self.relay.value(1)
                            if numIntervals == config.numIntervals:
                                break
                            else:
                                await uasyncio.sleep(config.pumpIntervalTimer)
                            
                        print(f'Moisture at {self.moisture}% - stopping pump on plant: {self.plantID} and sleeping system for {config.pumpSleepAfterRunTimer} seconds.')
                        await uasyncio.sleep(config.pumpSleepAfterRunTimer) # Sleep for config.pumpSleepTimer seconds to not constantly check/run the pump   

                        self.currentCycle = 0 # Reset the dry cycle to 0.