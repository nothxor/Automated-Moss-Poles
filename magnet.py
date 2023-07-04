from machine import Pin
import uasyncio
import time
import random

from neopixel import Neopixel

class Magnet:
    
    def __init__(self, pinID):
        self.pinID = pinID
        self.magStatus = 0
        self.ledID = 0  # Hardcoded LED strip GPIO value!
        
        self.mag = Pin(self.pinID, Pin.IN, Pin.PULL_UP)
        
        
        # LED stuff below
        self.numpix = 16
        self.strip = Neopixel(self.numpix, 0, self.ledID, "RGB")
        
        self.red = (255, 0, 0)
        self.orange = (255, 50, 0)
        self.yellow = (255, 100, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.indigo = (100, 0, 90)
        self.violet = (200, 0, 100)
        self.colors_rgb = [self.red, self.orange, self.yellow, self.green, self.blue, self.indigo, self.violet]
        
        self.delay = 0.5
        self.strip.brightness(42)
        self.blank = (0,0,0)
        
    
    async def runMagnet(self):
        
        while True:
            if self.mag.value() == 1:
                if self.magStatus == 0:
                    print("Door open.")
                    self.magStatus = 1
                
                
                self.strip.fill((255,0,110))
                
                self.strip.show()
                
                await uasyncio.sleep(self.delay)

            elif self.mag.value() == 0:
                if self.magStatus == 1:
                    print("Door closed.")
                    self.magStatus = 0
                self.strip.fill((0,0,0))
                self.strip.show()
            else:
                print("Magnet Error?")
            
            await uasyncio.sleep(1)