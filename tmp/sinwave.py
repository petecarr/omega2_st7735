#!/usr/bin/env python
from __future__ import print_function

from math import pi, sin, cos, sqrt, floor
import random

# Pins SCLK and MOSI are fixed in hardware
# I put the light on gpio 3 but it could just as well take the 3.3v supply
# miso  SDI = 9
# mosi, SDO = 8
# sclk  SCLK = 7
cs= 6
dc= 1
rst= 0

# Color definitions
BLACK         = 0x0000
BLUE          = 0x001F
RED           = 0xF800
GREEN         = 0x07E0
CYAN          = 0x07FF
MAGENTA       = 0xF81F
YELLOW        = 0xFFE0
WHITE         = 0xFFFF
VIOLET        = 0x580b
INDIGO        = 0x601f
ORANGE        = 0xf9c0

colors = [VIOLET, INDIGO, BLUE, CYAN, GREEN, YELLOW, ORANGE, RED, 
          MAGENTA, WHITE]

import st7735
from st7735_opcodes import *
"""
from time import sleep
from timeit import default_timer as timer
from datetime import datetime
"""

tft = st7735.Spi(dc, rst)


CANVASWIDTH=tft.height
CANVASHEIGHT=tft.width
BGCOLOR=BLACK
ALL='all'


x = [0]*361
y = [0]*361

"""
def delay(delayTime):
    from time import sleep
    sleep(delayTime)

from datetime import datetime
#from datetime import timedelta

start_time = datetime.now()

# returns the elapsed milliseconds since the start of the program
def millis():
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms

"""

def setColor(red, green, blue):
    color = (red & 0x1f)<<11 | (green & 0x3f) << 5 | blue & 0x1f
    return color
    
def clrDisplay():
    tft.fillScreen(BLACK)
    return

    

#*****************************************************************#
#**                       System Setup                          **#
#*****************************************************************#

def setup():
    clrDisplay()

    # Seed the generator
    random.randrange(0,100)

    # build a list of coords
    global x, y
    conv = pi/180.0
    xcenter = CANVASHEIGHT/2
    ycenter = CANVASWIDTH/4
    rad = ycenter-4.0
    for i in range(361):
        if i != 0:
            angle = float(i)*conv
        else:
            angle = 0.0
        x[i] = int(xcenter + rad*sin(angle))
        y[i] = int(ycenter + rad*cos(angle))
    
    
def drawSin():
    global x, y
    idx = random.randint(0,len(colors)-1)
    col = colors[idx]
    xcenter = CANVASHEIGHT//2
    ycenter = CANVASWIDTH//4
    rad = ycenter-4
    tft.drawCircle(xcenter, ycenter, rad, col)
    tft.drawLine(CANVASHEIGHT//2, 1, CANVASHEIGHT//2, CANVASWIDTH-1, col)
    
    xx = xcenter   
    yy = ycenter+rad

    choice = (random.randint(0,19) & 1) != 0

    if choice: 
        rev = range(360, -1, -5)
    else: 
        rev = range(0,361, 5)

    for i in rev:
        # draw new pointer
        tft.drawLine(xcenter, ycenter, x[i],y[i], col)
        # draw sin wave increment
        if x[i] > xcenter:
            tft.drawHorizontalLine(xcenter, yy, x[i]-xcenter+1, col)
        elif xcenter > x[i]:
            tft.drawHorizontalLine(x[i], yy, xcenter-x[i]+1, col)
        yy = yy+1
 

def loop():
    drawSin()
    

#--------------------------------------------------------------------

if __name__ == '__main__':

    try:
        print("Circles and sines")
        print("Enter cntrl-C to quit")
        setup()
        while (True):
            loop()
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
        quit()



