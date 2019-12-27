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

import sys

from glcdfont import font
from st7735_opcodes import *
import spidev
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
  
        self.dc = dc
  
        self.rst = rst
        self.busNumber = 0 # was 32766 in old firmware
        self.deviceId = 1
        self.spi  = spidev.SpiDev()
        self.spi.open(self.busNumber, self.deviceId) 

        self.spi.mode = 0 #0xb00
        self.spi.cshigh =  False
        self.spi.lsbfirst = False
        self.spi.max_speed_hz = 4000000

        print("spi.mode=", self.spi.mode)
        print("spi.cshigh=", self.spi.cshigh)
        print("lsbfirst=", self.spi.lsbfirst)
        print("speed=", self.spi.max_speed_hz)
        print("bitsPerWord=", self.spi.bits_per_word)
        print("dc = ", self.dc)

        cs = 6
        self.cs = onionGpio.OnionGpio(cs)
        res = self.cs.setOutputDirection()

        sck = 7
        self.sck = onionGpio.OnionGpio(sck)
        res = self.sck.setOutputDirection()

        miso = 9
        self.miso = onionGpio.OnionGpio(miso)
        res = self.miso.setInputDirection()

        mosi = 8        
        self.mosi = onionGpio.OnionGpio(mosi)
        res = self.mosi.setOutputDirection()
  
        """
        # checkDevice is gone in spidev
        res = self.spi.checkDevice()
        if res == 1:
            print("Device adapter is not registered, trying register")
        
            res = self.spi.registerDevice()
            if res == 0:
                print("Device adapter is now registered with the kernel")
            elif res == 1:    
                print("*** Device adapter has failed to register ***")
                sys.exit(-1)

        """

        # Just to see something happen. Could put light on 3.3v
        self.light = onionGpio.OnionGpio(3)
        res = self.light.setOutputDirection()
        #self.light.setValue(LOW)
        #delay(1000.0)
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
        self.initR()
        
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
            
        # write takes a list
        #print("writebytes - ", val)
        res = self.spi.writebytes(val)
        if (res != 0) and (res != None):
            print("writebytes failed to write value: status ", val, res)
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
        self.writendata([0, x0+2, 0, x1+2])

        self.writecommand(ST7735_RASET)  # row addr set
        self.writendata([0, y0+1, 0, y1+1])

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
            self.spi.writebytes(scrn)
        #end = timer()
        #print("fill screen took ", end-start)
    



    def initR(self):
        #print("in initR")

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
        # frame rate = fosc / (1 x 2 + 40) * (LINE + 2C + 2D)
        self.writendata([0x01, 0x2c, 0x2d])
      
        self.writecommand(ST7735_FRMCTR2)  # frame rate control - idle mode
        # frame rate = fosc / (1 x 2 + 40) * (LINE + 2C + 2D)
        self.writendata([0x01, 0x2c, 0x2d])
      
        self.writecommand(ST7735_FRMCTR3)  # frame rate control - partial mode
        # dot inversion mode , line inversion mode
        self.writendata([0x01, 0x2c, 0x2d, 0x01, 0x2c, 0x2d])
        
        self.writecommand(ST7735_INVCTR)  # display inversion control
        self.writedata(0x07)  # no inversion
      
        self.writecommand(ST7735_PWCTR1)  # power control
        self.writendata([0xa2, 0x02, 0x84])
        #self.writedata(0xA2)     
        #self.writedata(0x02)      # -4.6V
        #self.writedata(0x84)      # AUTO mode
      
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
        self.writedata(0xC8)  # row address/col address, bottom to top refresh
        madctl = 0xC8
        
        self.writecommand(ST7735_COLMOD)  # set color mode
        self.writedata(0x05)        # 16-bit color
      
        self.writecommand(ST7735_CASET)  # column addr set
        self.writendata([0x00, 0x00, 0x00, 0x7f]) #XSTART = 0  XEND = 127
      
        self.writecommand(ST7735_RASET)  # row addr set
        # XSTART = 0, XEND = 159
        self.writendata([0, 0, 0, 0x9f])
      
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
      

    # draw a string from memory

    def drawString(self, x, y, c, color, bg_color, size = 1):
        for ch in c:
            self.drawChar(x, y, ch, color, bg_color, size)
            x += size*6
            if (x + 5 >= self.width):
                y += 10
                x = 0

    # draw a character
    # doesn't need bg_color but Lorem ipsum takes 67.32 secs
    def slowdrawChar(self, x, y, c, color, bg_color, size = 1):
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

    def drawChar(self, x, y, c, color, bg_color, size = 1):
        #print(c, end="")
        if size == 1: # default size. Lorem ipsum takes 7.36 secs
            val = []
            lines = []
            for i in range(0, 5):
                lines.append(font[(ord(c)*5)+i])
                #if c == 'L': 
                    #print("{0:8x}".format(int(lines[i])))
            mask = 1
            for j in range(0,8):
                for i in range (0,5):
                    if (lines[i] & mask):
                        #if c == 'L':print('1', end="")

                        val.append(color >> 8)
                        val.append(color)
                    else:
                        #if c == 'L':print('0', end="")
                        val.append(bg_color >> 8)
                        val.append(bg_color)
                mask <<= 1

            self.setAddrWindow(x, y, x+4, y+7)
            # setup for data
            self.setdata()
            self.spi.writebytes(val)
        else: # big chars- old way
            for i in range(0, 5):
                line = font[(ord(c)*5)+i]
                for j in range(0,8):
                    if (line & 1):
                        self.fillRect(x+i*size, y+j*size, size, size, color)
            
                    line >>= 1

    # fill a circle
    def fillCircle(self, x0, y0, r, color):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

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
            self.drawVerticalLine(x0-x, y0-y, 2*y+1, color)
            self.drawVerticalLine(x0+y, y0-x, 2*x+1, color)
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
     
     
        # restrict argument iist to 4096 bytes
        val = []
        lenval = 0
        for x in range(0, w):
            for y in range(0, h):
                val.append(color >> 8)
                val.append(color)
                lenval += 2
                if lenval >= 4094:
                    self.spi.writebytes(val)
                    val = []
                    lenval = 0
        if lenval > 0:
            self.spi.writebytes(val)



    def drawVerticalLine(self, x, y, length, color):

        if (x >= self.width): return
        if (y+length >= self.height): length = self.height-y-1

        self.drawFastLine(x,y,length,color,1)


    def drawHorizontalLine(self, x,  y,  length,  color):

        if (y >= self.height): return
        if (x+length >= self.width): length = self.width-x-1

        self.drawFastLine(x,y,length,color,0)


    def drawFastLine(self, x, y, length, color, rotflag):
        if length == 0: return

        if (rotflag):
            self.setAddrWindow(x, y, x, y+length)
        else:
            self.setAddrWindow(x, y, x+length, y+1)
  
        # setup for data
        self.setdata()

        val = []
        while (length > 0):
            val.append(color >> 8)
            val.append(color)
            #self.spiwrite([color >> 8, color], dc= NEITHER)    
            length -= 1
        self.spi.writebytes(val)

    def rot(self):
        # dummy rotation for now
        # needs more research
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

        err = dx // 2

        if (y0 < y1):
            ystep = 1
        else:
            ystep = -1

        lowx0 = x0
        val1 = []
        val2 = []
        #print(x0, y0, x1, y1)
        #print("Initially, err=", err)
        for x0 in range(lowx0,x1+1):
            if (steep):
                val1.append(y0)
                val2.append(x0)
                #self.drawPixel(y0, x0, color)
            else:
                val1.append(x0)
                val2.append(y0)
                #self.drawPixel(x0, y0, color)
    
            err -= dy
            #print("err=", err, "x0 = ", x0)
            if x0 == x1: 
                # or we miss the last half segment
                err = -dy//2
                #print("Fiddled err=", err, "x0 = ", x0)
            if (err < 0):
                if len(val1) == 1:
                    self.drawPixel(val1[0], val2[0], color)
                else:
                    # ganging up the transfers like this cuts average line
                    # draw times by half (315 secs to 157 secs in 
                    # testdrawlines). Much faster for lines that are nearly 
                    # horizontal or vertical.
                    lst = len(val1) -1
                    self.setAddrWindow(val1[0], val2[0], val1[lst], val2[lst])
                    #print('Window (', val1[0],',',val2[0],') ',
                    #      '(', val1[lst],',',val2[lst],')')
                    dat = []
                    leng = lst+1
                    while (leng >= 0):
                        dat.append(color >> 8)
                        dat.append(color)
                        leng -= 1
                    self.setdata()
                    self.spi.writebytes(dat)

                val1 = []
                val2 = []
                y0 += ystep
                err += dx
    

