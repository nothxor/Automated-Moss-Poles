from machine import Pin
import uasyncio

class Valve:
    
    def __init__(self, valvePinID):
        
        self.valvePinID = valvePinID
        self.valveStatus = 0

        self.floatValve = Pin(self.valvePinID, Pin.IN, Pin.PULL_UP)
        
        
    async def runValve(self):
        
        while True:
            if self.floatValve.value() == 1:
                if self.valveStatus == 0:
                    print("Water level low!")
                    self.valveStatus = 1
            elif self.floatValve.value() == 0:
                if self.valveStatus == 1:
                    print("Water level high!")
                    self.valveStatus = 0
            else:
                print("Float Valve Error?")
            
            await uasyncio.sleep(1)