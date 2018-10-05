#!/usr/bin/env python
from __future__ import print_function   # how about a jet-pack as well?

# Adapted from the Graphics library by Ladyada/Adafruit 
# Python code for the Onion Omega2 which provides the onionGpio and 
# onionSpi packages. It is Python 2 since they don't support Python3 yet 
# in these packages.
# Init code from Rossum 

""" ************************ from original (with a few changes).
This is an interface for the Adafruit 1.8" SPI display.
This program works with the Adafruit 1.8" TFT Breakout w/SD card
  ----> http://www.adafruit.com/products/358
as well as Adafruit raw 1.8" TFT display
  ----> http://www.adafruit.com/products/618

Check out the links above for Adafruit's tutorials and wiring diagrams.
These displays use SPI to communicate, 4 or 5 pins are required
to interface (RST is optional).
Adafruit invests time and resources providing (the original of) this 
open source code, please support Adafruit and open-source hardware by 
purchasing products from Adafruit!

Original C program for Arduino w ritten by Limor Fried/Ladyada for 
Adafruit Industries.
MIT license, all text above must be included in any redistribution
****************************   """
# MIT License                      
# Look it up. It's on the internet.

"""
This info from Adafruit. I have a Sainsmart display with a BLUETAB
but it appears to be the same as a BLACKTAB.

Our supplier changed the 1.8" display slightly after Jan 10, 2012
so that the alignment of the TFT had to be shifted by a few pixels
this just means the init code is slightly different. Check the   
color of the tab to see which init code to try. If the display is
cut off or has extra 'random' pixels on the top & left, try the  
other option!                                                    
If you are seeing red and green color inversion, use Black Tab   
                                                                      
If your TFT's plastic wrap has a Black Tab, use the following:   
tft.initR(INITR_BLACKTAB);   // initialize a ST7735S chip, black tab
If your TFT's plastic wrap has a Red Tab, use the following:   
tft.initR(INITR_REDTAB);   // initialize a ST7735R chip, red tab
If your TFT's plastic wrap has a Green Tab, use the following: 
tft.initR(INITR_GREENTAB); // initialize a ST7735R chip, green tab
                                                                 
"""

import sys

from glcdfont import font
from st7735_opcodes import *

# Make the change here.
displayType = INITR_BLACKTAB  # or BLUETAB
#displayType = INITR_GREENTAB

import onionSpi
import onionGpio

from time import sleep
from timeit import default_timer as timer

LOW = 0
HIGH = 1
# dc values (or neither to be set)
CMD = LOW
DAT = HIGH
NEITHER = -1

def delay(ms_count):
    sleep(ms_count/1000.0)

class Spi:

    def __init__(self,  dc,  rst):

        self.width = 128
        self.height = 160

        self.madctl = 0     
        self.colstart = self.rowstart = 0
  
        self.dc = dc
  
        self.rst = rst
        self.busNumber = 1
        self.deviceId = 32766
        self.spi  = onionSpi.OnionSpi(self.busNumber, self.deviceId) 

        #print("spi.mode=", self.spi.mode)
        #print("sck=", self.spi.sck)
        #print("lsbfirst=", self.spi.lsbfirst)
        #print("speed=", self.spi.speed)
        #print("bitsPerWord=", self.spi.bitsPerWord)
        #print("dc = ", self.dc)

        self.spi.cs = 6
        self.cs = onionGpio.OnionGpio(self.spi.cs)
        res = self.cs.setOutputDirection()

        self.spi.sck = 7
        self.sck = onionGpio.OnionGpio(self.spi.sck)
        res = self.sck.setOutputDirection()

        self.spi.miso = 9
        self.miso = onionGpio.OnionGpio(self.spi.miso)
        res = self.miso.setInputDirection()

        self.spi.mosi = 8        
        self.mosi = onionGpio.OnionGpio(self.spi.mosi)
        res = self.mosi.setOutputDirection()
  
        res = self.spi.checkDevice()
        if res == 1:
            print("Device adapter is not registered, trying register")
        
            res = self.spi.registerDevice()
            if res == 0:
                print("Device adapter is now registered with the kernel")
            elif res == 1:    
                print("*** Device adapter has failed to register ***")
                sys.exit(-1)


        # Just to see something happen. Could put light on 3.3v
        self.light = onionGpio.OnionGpio(3)
        res = self.light.setOutputDirection()
        self.light.setValue(HIGH)
    
        # reset
        self.rst = onionGpio.OnionGpio(rst)
        res = self.rst.setOutputDirection()
        if res != 0:
            print("Failed to set rst output direction, pin=",rst, 
                  "status = ", res)
        self.dc = onionGpio.OnionGpio(dc)
        
        # data (0) or command (1)
        res = self.dc.setOutputDirection()
        if res != 0:
            print("Failed to set dc output direction, pin=",dc, 
                  "status = ", res)
        
        # all the st7735 specific initialization
        self.initR(displayType)
        
    def setcommand(self):
        res = self.dc.setValue(LOW)
        if res == -1:
            print("setcommand failed, status = ", res)        
        
    def setdata(self):
        res = self.dc.setValue(HIGH)
        if res == -1:
            print("setdata failed, status = ", res)  
            
    def spiwrite(self, val, dc = CMD):
        if dc != NEITHER:
            res = self.dc.setValue(dc)
            if res == -1:
                if dc == CMD:
                    print("setcommand failed, status = ", res)        
                else:
                   print("setdata failed, status = ", res)  
            
        """ ********************* doesn't seem to work at all
        # but is roughly my understanding of the signal sequence
        # raise clk 
        res = self.sck.setValue(HIGH)
        #print("clk raised, res=", res)
        # drop cs
        res += self.cs.setValue(LOW)
        #print("cs dropped, res=", res)
        for data_byte in val:
            # assuming msb down wards since lsbfirst is 0 
            mask = 0x80        # set data
            while mask != 0:
                if (data_byte & mask) != 0:
                    data_bit = 1
                else:
                    data_bit = 0
                res += self.mosi.setValue(data_bit)
                #print("mosi set to", data_bit, ", res=", res)
	        mask >>= 1
                # drop clock
                res += self.sck.setValue(LOW)
                #print("clk dropped, res=", res)
                #delay(10.0)
                # raise clock
                res += self.sck.setValue(HIGH)
                #print("clk raised, res=", res)
                #delay(10.0)

        # raise cs
        res += self.cs.setValue(HIGH)
        #print("cs raised, res=", res)
        
        ****************************** """
        # write takes a list
        res = self.spi.write(val)
        if (res != 0) and (res != None):
            print("spiwrite failed to write value: status ", val, res)
            sys.exit(-1)


    def writecommand(self, c):
        self.spiwrite([c], CMD)


    def writedata(self, c):
        self.spiwrite([c], DAT)
	

    def writendata(self,  c):
        # already a list
        self.spiwrite(c, DAT)  
   

    def setAddrWindow(self, x0,  y0,  x1, y1):

        self.writecommand(ST7735_CASET)  # column addr set
        self.writendata([0, x0+self.colstart, 0, x1+self.colstart])

        self.writecommand(ST7735_RASET)  # row addr set
        self.writendata([0, y0+self.rowstart, 0, y1+self.rowstart])

        self.writecommand(ST7735_RAMWR)  # self.write to RAM


    def pushColor(self, color):
        self.spiwrite([color >> 8, color], DAT)    


    def drawPixel(self, x, y, color):
        if ((x >= self.width) or (y >= self.height)):
            return

        self.setAddrWindow(x,y,x+1,y+1)

        self.spiwrite([color >> 8, color], DAT)    


    def fillScreen(self,color):
        #print("Fill screen, width = ", self.width, " height = ", self.height)
        self.setAddrWindow(0, 0, self.width-1, self.height-1)

        # setup for data
        self.setdata()

        # 3 ms * 20k gets a minute to fill the screen
        # but sending out 100 at a time gets an I/O error
        SCREEN_SLICE = 20
        #start = timer()
        scrn = []
        for i in range(0, SCREEN_SLICE):
            scrn.append(color >> 8)
            scrn.append(color)
        #end = timer()
        #print("screen init took ", end-start)
        #start = timer()
        # doing full 20480 gets IO error
        for i in range(0,20480/SCREEN_SLICE):
            self.spiwrite(scrn, dc = NEITHER)
        #end = timer()
        #print("fill screen took ", end-start)
    



    def initR(self, displayType):
        if displayType == INITR_GREENTAB:
            self.colstart = 2
            self.rowstart = 1

        # toggle RST low to reset; CS low so it'll listen to us
        self.rst.setValue(LOW)
        delay(500.0)
        self.rst.setValue(HIGH)
        delay(500.0)
        
        self.writecommand(ST7735_SWRESET) # software reset
        delay(150.0)

        self.writecommand(ST7735_SLPOUT)  # out of sleep mode
        delay(500.0)

        self.writecommand(ST7735_FRMCTR1)  # frame rate control - normal mode
        self.writedata(0x01)  # frame rate = fosc / (1 x 2 + 40) * (LINE + 2C + 2D)
        self.writedata(0x2C) 
        self.writedata(0x2D) 
      
        self.writecommand(ST7735_FRMCTR2)  # frame rate control - idle mode
        self.writedata(0x01)  # frame rate = fosc / (1 x 2 + 40) * (LINE + 2C + 2D)
        self.writedata(0x2C) 
        self.writedata(0x2D) 
      
        self.writecommand(ST7735_FRMCTR3)  # frame rate control - partial mode
        self.writedata(0x01) # dot inversion mode
        self.writedata(0x2C) 
        self.writedata(0x2D) 
        self.writedata(0x01) # line inversion mode
        self.writedata(0x2C) 
        self.writedata(0x2D) 
        
        self.writecommand(ST7735_INVCTR)  # display inversion control
        self.writedata(0x07)  # no inversion
      
        self.writecommand(ST7735_PWCTR1)  # power control
        self.writedata(0xA2)     
        self.writedata(0x02)      # -4.6V
        self.writedata(0x84)      # AUTO mode
      
        self.writecommand(ST7735_PWCTR2)  # power control
        self.writedata(0xC5)      # VGH25 = 2.4C VGSEL = -10 VGH = 3 * AVDD
      
        self.writecommand(ST7735_PWCTR3)  # power control
        self.writedata(0x0A)      # Opamp current small 
        self.writedata(0x00)      # Boost frequency
      
        self.writecommand(ST7735_PWCTR4)  # power control
        self.writedata(0x8A)      # BCLK/2, Opamp current small & Medium low
        self.writedata(0x2A)     
      
        self.writecommand(ST7735_PWCTR5)  # power control
        self.writendata([0x8A, 0xEE])     
      
        self.writecommand(ST7735_VMCTR1)  # power control
        self.writedata(0x0E)  
      
        self.writecommand(ST7735_INVOFF)    # don't invert display
      
        self.writecommand(ST7735_MADCTL)  # memory access control (directions)
        if displayType == INITR_BLACKTAB:
            madctl = 0xc0
        else:
            madctl = 0xc8
        self.writedata(madctl)  # row address/col address, bottom to top refresh
        
        self.writecommand(ST7735_COLMOD)  # set color mode
        self.writedata(0x05)        # 16-bit color
      
        self.writecommand(ST7735_CASET)  # column addr set
        self.writendata([0x00, self.colstart, 0x00, 0x7f]) #XSTART = 0  XEND = 127
      
        self.writecommand(ST7735_RASET)  # row addr set
        # XSTART = 0, XEND = 159
        self.writendata([0, self.rowstart, 0, 0x9f])
      
        self.writecommand(ST7735_GMCTRP1)
        self.writendata([0x02, 0x1c, 0x07, 0x12, 
                        0x37, 0x32, 0x29, 0x2d, 
                        0x29, 0x25, 0x2B, 0x39, 
                        0x00, 0x01, 0x03, 0x10])
        self.writecommand(ST7735_GMCTRN1)
        self.writendata([0x03, 0x1d, 0x07, 0x06,  
                        0x2E, 0x2C, 0x29, 0x2D,  
                        0x2E, 0x2E, 0x37, 0x3F,  
                        0x00, 0x00, 0x02, 0x10]) 
        
        self.writecommand(ST7735_DISPON)
        delay(100.0)
      
        self.writecommand(ST7735_NORON)  # normal display on
        delay(10.0)

        #print("initR complete")
      
    def updateString(self, x, y, c, old_c, color, bg_color, size = 1):
        idx = 0
        for ch in c:
            if ch != old_c[idx]:
                self.fillRect(x, y, 6*size, 10*size, bg_color)
                self.drawChar(x, y, ch, color, size)
            idx += 1
            x += size*6
            if (x + 5 >= self.width):
                y += 10
                x = 0

    # draw a string from memory

    def drawString(self, x, y, c, color, size = 1):
        for ch in c:
            self.drawChar(x, y, ch, color, size)
            x += size*6
            if (x + 5 >= self.width):
                y += 10
                x = 0

    # draw a character
    def drawChar(self, x, y, c, color, size = 1):
        #print(c, end="")
        for i in range(0, 5):
            line = font[(ord(c)*5)+i]
            for j in range(0,8):
                if (line & 1):
                    if (size == 1): # default size
                        self.drawPixel(x+i, y+j, color)
                    else:  # big size
                        self.fillRect(x+i*size, y+j*size, size, size, color)
            
                line >>= 1
          
      

    # fill a circle
    def fillCircle(self, x0, y0, r, color):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

        #if x0 >= 0:
        self.drawVerticalLine(x0, y0-r, 2*r+1, color)

        while (x<y):
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y
 
            x += 1
            ddF_x += 2
            f += ddF_x
          
            self.drawVerticalLine(x0+x, y0-y, 2*y+1, color)
            #if (x0-x) >= 0:
            self.drawVerticalLine(x0-x, y0-y, 2*y+1, color)
            self.drawVerticalLine(x0+y, y0-x, 2*x+1, color)
            #if (x0-y) >= 0:
            self.drawVerticalLine(x0-y, y0-x, 2*x+1, color)


    # draw a circle outline
    def drawCircle(self, x0, y0, r, color):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
      
        self.drawPixel(x0, y0+r, color)
        self.drawPixel(x0, y0-r, color)
        self.drawPixel(x0+r, y0, color)
        self.drawPixel(x0-r, y0, color)
      
        while (x<y):
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y
          
            x += 1
            ddF_x += 2
            f += ddF_x
        
            self.drawPixel(x0 + x, y0 + y, color)
            self.drawPixel(x0 - x, y0 + y, color)
            self.drawPixel(x0 + x, y0 - y, color)
            self.drawPixel(x0 - x, y0 - y, color)
          
            self.drawPixel(x0 + y, y0 + x, color)
            self.drawPixel(x0 - y, y0 + x, color)
            self.drawPixel(x0 + y, y0 - x, color)
            self.drawPixel(x0 - y, y0 - x, color)
    

    def getRotation(self):
        return self.madctl


    def setRotation(self, m):
        self.madctl = m
        self.writecommand(ST7735_MADCTL)  # memory access control (directions)
        self.writedata(self.madctl)  # row address/col address, 
                                     # bottom to top refresh


    # draw a rectangle
    def drawRect(self, x,  y,  w, h, color):
        # smarter version
        self.drawHorizontalLine(x, y, w, color)
        self.drawHorizontalLine(x, y+h-1, w, color)
        self.drawVerticalLine(x, y, h, color)
        self.drawVerticalLine(x+w-1, y, h, color)


    def fillRect(self, x, y, w,  h, color):
        # smarter version

        self.setAddrWindow(x, y, x+w, y+h)

        # setup for data
        self.setdata()
     
        for x in range(0, w):
            for y in range(0, h):
                self.spiwrite([color >> 8, color], dc=NEITHER)   




    def drawVerticalLine(self, x, y, length, color):

        if (x < 0) : return
        if (x >= self.width): return
        if (y < 0): 
            length += y
            y = 0
        if (y+length >= self.height): length = self.height-y-1

        self.drawFastLine(x,y,length,color,1)


    def drawHorizontalLine(self, x,  y,  length,  color):

        if (y < 0): return
        if (y >= self.height): return
        if (x < 0): 
            length += x
            x = 0
        if (x+length >= self.width): length = self.width-x-1

        self.drawFastLine(x,y,length,color,0)


    def drawFastLine(self, x, y, length, color, rotflag):

        if (rotflag):
            self.setAddrWindow(x, y, x, y+length)
        else:
            self.setAddrWindow(x, y, x+length, y+1)
  
        # setup for data
        self.setdata()

        while (length > 0):
            self.spiwrite([color >> 8, color], dc= NEITHER)    
            length -= 1

    def rot(self):
        # dummy rotation for now
        #self.setRotation(self.getRotation()+1); 
        return


    # bresenham's algorithm - thx wikpedia
    def drawLine(self, x0, y0, x1, y1, color):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if (steep):
            #swap(x0, y0)
            x0, y0 = y0, x0
            #swap(x1, y1)
            x1, y1 = y1, x1

        if (x0 > x1):
            #swap(x0, x1)
            x0, x1 = x1, x0
            #swap(y0, y1)
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)

        err = dx / 2

        if (y0 < y1):
            ystep = 1
        else:
            ystep = -1

        lowx0 = x0
        for x0 in range(lowx0,x1+1):
            if (steep):
                self.drawPixel(y0, x0, color)
            else:
                self.drawPixel(x0, y0, color)
    
            err -= dy
            if (err < 0):
                y0 += ystep
                err += dx
    


