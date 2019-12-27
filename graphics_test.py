#!/usr/bin/env python
from __future__ import print_function 

# MIT License
# Look it up. It's on the internet.  

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

import st7735
from st7735_opcodes import *
from time import sleep
from timeit import default_timer as timer

tft = st7735.Spi(dc, rst)   


def delay(ms_count):
    sleep(ms_count/1000.0)


def fillpixelbypixel(color):
    for x in range(0, tft.width):
        for y in range(0, tft.height):
            tft.drawPixel(x, y, color)
  
    --delay(100.0)


def testlines():
    # takes 600 seconds - draws many lines
    interval = 10
    tft.fillScreen(BLACK)
    color = BLUE
    for x in range(0,  tft.width, interval):
        tft.drawLine(0, 0, x, tft.height-1, color)
   
    for y in range(0, tft.height, interval):
        tft.drawLine(0, 0, tft.width-1, y, color)
   
    color = RED
    for x in range(0, tft.width, interval):
        tft.drawLine(tft.width-1, 0, x, tft.height-1, color)
   
    for y in range(0, tft.height,interval):
        tft.drawLine(tft.width-1, 0, 0, y, color)
   
    color = YELLOW
    for x in range(0, tft.width, interval):
        tft.drawLine(0, tft.height-1, x, 0, color)
   
    for y in range(0, tft.height, interval):
        tft.drawLine(0, tft.height-1, tft.width-1, y, color)
   

    color = GREEN
    for x in range(0, tft.width, interval):
        tft.drawLine(tft.width-1, tft.height-1, x, 0, color)
   
    for y in range(0, tft.height, interval):
        tft.drawLine(tft.width-1, tft.height-1, 0, y, color)
   


def testdrawtext(text, color, bg_color):
    tft.drawString(0, 0, text, color, bg_color)


def testfastlines(color1, color2): 
    tft.fillScreen(BLACK)
    for y in range(0, tft.height, 5):
        tft.drawHorizontalLine(0, y, tft.width, color1)
   
    for x in range(0, tft.width, 5):
        tft.drawVerticalLine(x, 0, tft.height, color2)
   


def testdrawrects(color): 
    tft.fillScreen(BLACK)
    for x in range(0, tft.width, 6):
        tft.drawRect(tft.width/2 -x/2, tft.height/2 -x/2 , x, x, color)
 


def testfillrects(color1, color2): 
    tft.fillScreen(BLACK)
    for x in range(tft.width-1,6, -6):
        tft.fillRect(tft.width/2 -x/2, tft.height/2 -x/2 , x, x, color1)
        tft.drawRect(tft.width/2 -x/2, tft.height/2 -x/2 , x, x, color2)
 


def testfillcircles(radius, color): 
    for x in range(radius, tft.width, radius*2):
        for y in range(radius, tft.height, radius*2):
            tft.fillCircle(x, y, radius, color)
    

def testdrawcircles(radius, color): 
    for x in range(0, tft.width+radius, radius*2): 
        for y in range(0, tft.height+radius, radius*2):
            tft.drawCircle(x, y, radius, color)
    


def setup(): 
 
    #tft.initR()       # initialize a ST7735R chip (was done in __init__)

    tft.writecommand(ST7735_DISPON)
  
    tft.fillScreen(BLACK)
    print("Screen should be black")

    #tft.drawLine(tft.width/2, 0,tft.width/2+4, tft.height, BLUE)
    #tft.drawLine(tft.width/2, 0,tft.width/2+10, tft.height, BLUE)
    #return

    for i in range(4):
        tft.drawLine(0,tft.height/2, tft.width, tft.height/2, BLUE)
        # make it a multiple of 4 or rest of test outputs strangely
        tft.rot()

    #
    tft.fillScreen(WHITE)
    start = timer()
    testdrawtext("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                 "Curabitur adipiscing ante sed nibh tincidunt feugiat. "
                 "Maecenas enim massa, fringilla sed malesuada et, "
                 "malesuada sit amet turpis. Sed porttitor neque ut ante "
                 "pretium vitae malesuada nunc bibendum. Nullam aliquet "
                 "ultrices massa eu hendrerit. Ut sed nisi lorem. "
                 "In vestibulum purus a tortor imperdiet posuere. ", 
                 BLACK, WHITE)
    end = timer()
    print("text took {0:.2f} secs".format(end-start))
    #testdrawtext("Some text, a little shorterf you prefer.", WHITE, BLACK)
    delay(1000.0)
  
    #a single pixel
    #tft.drawPixel(tft.width/2, tft.height/2, GREEN)
    #delay(500.0)

    # line draw test
    start = timer()
    testlines()
    end = timer()
    print("lines took {0:.2f} secs".format(end-start))
    #delay(500.0)    
  
    # optimized lines
    start = timer()
    testfastlines(RED, BLUE)
    end = timer()
    print("fast lines took {0:.2f} secs".format(end-start))
    delay(500.0)    

    testdrawrects(GREEN)
    delay(500.0)

    testfillrects(YELLOW, MAGENTA)
    delay(500.0)

    tft.fillScreen(BLACK)

    start = timer()
    testfillcircles(10, BLUE)
    end = timer()
    print("fill circles took {0:.2f} secs".format(end-start))

    start = timer()
    testdrawcircles(10, WHITE)
    end = timer()
    print("draw circles took {0:.2f} secs".format(end-start))
 
    delay(1000.0)



def loop(): 
    tft.writecommand(ST7735_INVON)
    delay(500.0)
    tft.writecommand(ST7735_INVOFF)
    delay(500.0)


if __name__ == '__main__':

    try:
        setup()
  
        """
        while (True): 
            loop()
        """
    except KeyboardInterrupt:                                
        print("Keyboard interrupt, exiting")                 
        quit()       

