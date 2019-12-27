#!/usr/bin/env python                                                           
from __future__ import print_function                                           
                                                                                
"""
 * The Desktop Contemplator for Nuts and Volts
 *
 * A program to display fractals and other patterns on desktop device
 * with the intent to distract and calm the mind.
 *

 * Concept and Implementation by: Craig A. Lindley
 * Version: 1.0
 * Last Update: 11/11/2012
 *
"""

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
                                                                                
colors = [BLUE,RED,GREEN,CYAN,MAGENTA,YELLOW,WHITE, VIOLET,INDIGO,ORANGE]                             
                                                                                
import st7735                                                                   
from st7735_opcodes import *                        
from time import sleep                                                          
from timeit import default_timer as timer                                       
from datetime import datetime                                                 

tft = st7735.Spi(dc, rst)                                                     

# Trying to compensate for small display without destroying original settings
t46 = 23
t100 = 50
t240 = tft.height
t239 = t240-1
t320 = tft.width #80
t319 = t320-1 #79
                                                                                
                                                                                
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

def setRandomColor():
    idx = random.randint(0, len(colors)-1)
    color = colors[idx]
    #color =  setColor(random.randint(0,0x1f), random.randint(0,0x3f), 
    #                 random.randint(0,0x1f))
    return color

    
    

# Array of pointers to pattern display functions
def patternFunctions(index): 
    if index ==1:
        print("bigPixel")
        bigPixelPattern()
    elif (index == 2):
        print("burstPattern")
        burstPattern()
    elif index == 3:
        print("offsetCircle")
        offsetCirclePattern()
    elif (index == 4):
        print("JuliaPattern")
        #juliaPattern()
    elif index == 5:
        print("plasmaPattern")
        #plasmaPattern()
    elif (index == 6):
        print("horizPalette")
        horizPaletteLinesPattern()
    elif index == 7:
        print("bigPixel")
        bigPixel2Pattern()
    elif (index == 8):
        print("vertPalette")
        vertPaletteLinesPattern()
    elif index == 9:
        print("concentricSquares")
        concentricSquaresPattern()
    elif index == 10:
        print("text")
        textPattern()
    elif index == 11:
        print("circleOfCircles")
        circleOfCirclesPattern()
    elif index == 12:
        print("concentricCircles")
        concentricCirclesPattern()
    elif index == 13:
        print("circlesPattern")
        circlesPattern()
    elif index == 14:
        print("linesPattern")
        linesPattern()
    elif (index == 15):
        print("webPattern")
        webPattern()
    elif index == 16:
        print("spirograph")
        spirographPattern()
    elif (index == 17):
        print("mandelbrot")
        #mandelbrotPattern()
    elif index == 18:
        print("julia")
        #juliaPattern()
    elif (index == 19):
        print("plasma")
        #plasmaPattern()
    elif index == 20:
        print("draw1")
        draw1()
    else:
        return


# Determine the number of display patterns from the entries in the array
NUMBER_OF_PATTERNS=20

# Create array of flags for display pattern selection
flags=[0*NUMBER_OF_PATTERNS]

#*****************************************************************#
#**                       System Setup                          **#
#*****************************************************************#

def setColor(red, green, blue):                                               
    color = (red & 0x1f)<<11 | (green & 0x3f) << 5 | blue & 0x1f              
    return color                                                              
                                                                              
def clrDisplay():                                                             
    tft.fillScreen(BLACK)                                                     
    return      

def setup():
    clrDisplay()
    # Seed the generator
    random.randrange(0,100)


#*****************************************************************#
#**                Pattern Display Infrastructure               **#
#*****************************************************************#

# Pattern display timeout and associated variables
PATTERN_DISPLAY_DURATION_SECONDS=30
BETWEEN_PATTERN_DELAY_SECONDS   = 6

# How many time infrastructure will attempt to generate a random index
MAX_SPINS=100

timeOutEnabled = True
timeOut = 10000000

class timedOut(Exception):
    def __init__(self, value):
        self.value = value
      
    def __str__(self):
        return self.value

# Check for pattern timeout
# This must be called by everyt display pattern 
def checkForTimeout():
    global timeOutEnabled

    timeOutCondition = timeOutEnabled and (millis() > timeOut)

    if not timeOutCondition:
        return
  
    timeOutEnabled = False

    # Do the long jump back into top of main loop
    raise timedOut("")


def selectPattern():
  # Randomly select a pattern to run #
  # Return all patterns before allowing any repeats  
  spins = 0

  while (True):
    # Pick a candidate pattern index
    index = random.randint(0, NUMBER_OF_PATTERNS)

    # Check to see if this pattern was previously selected
    if flags[index] == 0:
      # This index was not previously used, so mark it so
      flags[index] = 1
      return index 
    else:
        spins += 1
        if (spins > MAX_SPINS):
            flags[0:len(flags)] = 0
            spins = 0


def selectPatternAndRun():
    # Select a display pattern randomly and execute it #

    # First clear the screen
    clrDisplay()

    # Then a short delay
    delay(1.0)

    # Select a pattern to run
    index = selectPattern() 

    # Calculate future time to switch pattern
    timeOut = millis() + (1000 * PATTERN_DISPLAY_DURATION_SECONDS)

    # Enable time outs
    timeOutEnabled = True

    # Start up the selected pattern
    patternFunctions(index)

    # This one used for testing only
    #  patternFunctions(0)


#*****************************************************************#
#**         Display and Font Definitions and Variables          **#
#*****************************************************************#

HEIGHT_LANDSCAPE = t320
MIN_X_LANDSCAPE =  0
MAX_X_LANDSCAPE =t319
XMID=(HEIGHT_LANDSCAPE // 2)
WIDTH_LANDSCAPE=t240
MIN_Y_LANDSCAPE =  0
MAX_Y_LANDSCAPE= t239
YMID =(WIDTH_LANDSCAPE // 2)

BIG_FONT_WIDTH =  16
BIG_FONT_HEIGHT = 16

#*****************************************************************#
#**           Color Constants, Variables and Functions          **#
#*****************************************************************#

NUM_OF_COLOR_VALUES=256
MIN_COLOR_VALUE   =  0  
MAX_COLOR_VALUE   = 255


"""
RGB = [ red,0, green, blue]
"""
# Color space conversion
# Input arguments
# hue in degrees (0 - 360.0)
# saturation in percent (0.0 - 1.0)
# value in percent (0.0 - 1.0)
# Output arguments
# red, green blue (0.0 - 1.0)

def _HSVtoRGB(hue, saturation, value,
              red, green, blue):

    i = 0
    f = p = q = t = 0
    if (saturation == 0):
        # achromatic (grey)
        red = green = blue = value
        return
  
    hue //= 60			# sector 0 to 5
    i = floor(hue)
    f = hue - i			# factorial part of h
    p = value * (1 - saturation)
    q = value * (1 - saturation * f)
    t = value * (1 - saturation * (1 - f))
    if i == 0:
        red = value
        green = t
        blue = p
    elif i == 1:
        red = q
        green = value
        blue = p
    elif i == 2:
        red = p
        green = value
        blue = t
    elif i == 3:
        red = p
        green = q
        blue = value
    elif i == 4:
        red = t
        green = p
        blue = value
    else:
        red = value
        green = p
        blue = q
 

# Create a HSV color and return it to an RGB structure
def createColor(hue, saturation, value, color):
    r = g = b = 0

    _HSVtoRGB(hue, saturation, value, r, g, b)
    (color).red   = (int) (r * MAX_COLOR_VALUE)
    (color).green = (int) (g * MAX_COLOR_VALUE)
    (color).blue =  (int) (b * MAX_COLOR_VALUE)


# Create an HSV color
def createHSVColor_(divisions, index, color, saturation = 1.0, value= 1.0):

    hueAngle = (360.0 * index) / divisions;
    createColor(hueAngle, saturation, value, color)


# Create a fully saturated HSV color
def createHSVColor(divisions, index, color):
    index %= divisions
    createHSVColor_(divisions, index, 1.0, 1.0, color)


#*****************************************************************#
#**             Palette definitions and Functions               **#
#*****************************************************************#

PALETTE_SIZE     =256
NUM_OF_PALETTES  =  7
GRAYSCALE_PALETTE=  0
SPECTRUM_PALETTE  = 1
SIN1_PALETTE      = 2
SIN2_PALETTE      = 3
SIN3_PALETTE      = 4
SIN4_PALETTE      = 5
RANDOM_PALETTE    = 6

"""

# Create a palette structure for holding color information
struct RGB palette[PALETTE_SIZE];

# Generate a palette based upon parameter
def generatePalette(  paletteNumber):

  # Create some factors for randomizing the generated palettes
  # This helps keep the display colors interesting
  f1 = random.randint(16, 128)
  f2 = random.randint(16, 128)
  f3 = random.randint(16, 128)

  if paletteNumber == GRAYSCALE_PALETTE:

      # Grayscale palette
      # Sometimes the light colors at low index; other times at high index
      direction = (random.randint(0,2) == 1)
      if (direction):
          for i in range(PALETTE_SIZE):
              palette[i].red = palette[i].green = palette[i].blue = i
        
        
      else:
           for i in range(PALETTE_SIZE):
              palette[i].red = palette[i].green = palette[i].blue = 255 - i
        
      
    
    

  elif paletteNumber == SPECTRUM_PALETTE:

      # Full spectrum palette at full saturation and value
      for i in range(PALETTE_SIZE):
        createHSVColor(PALETTE_SIZE, i, palette[i])
      
    
    

  elif paletteNumber == SIN1_PALETTE:

      # Use sin function to generate palette
      for i in range(PALETTE_SIZE):
        palette[i].red   = 128.0 + 128 * sin(PI * i / f1)
        palette[i].green = 128.0 + 128 * sin(PI * i / f2)
        palette[i].blue  = 128.0 + 128 * sin(PI * i / f3)
       
    
    

  elif paletteNumber ==  SIN2_PALETTE:

      # Use sin function to generate palette - no blue
      for i in range(256):
        palette[i].red   = 128.0 + 128 * sin(PI * i / f1)
        palette[i].green = 128.0 + 128 * sin(PI * i / f2)
        palette[i].blue  = 0;
      
     
    

  elif paletteNumber == SIN3_PALETTE:

      # Use sin function to generate palette - no green
      for i in range(256):
        palette[i].red   = 128.0 + 128 * sin(PI * i / f1)
        palette[i].green = 0;
        palette[i].blue  = 128.0 + 128 * sin(PI * i / f2)
       
    
    

  elif paletteNumber == SIN4_PALETTE:

      # Use sin function to generate palette - no red
      fori in range(PALETTE_SIZE):
        palette[i].red   = 0;
        palette[i].green = 128.0 + 128 * sin(PI * i / f1)
        palette[i].blue  = 128.0 + 128 * sin(PI * i / f2)
       
    
    

    elif paletteNumber ==  RANDOM_PALETTE:
        # Choose random color components
        for i in range(PALETTE_SIZE):
            palette[i].red   = random.randint(0,NUM_OF_COLOR_VALUES)
            palette[i].green = random.randint(0,NUM_OF_COLOR_VALUES)
            palette[i].blue  = random.randint(0,NUM_OF_COLOR_VALUES)
       
    
    
"""

#*****************************************************************#
#**             Mandelbrot and Julia Set Functions              **#
#*****************************************************************#

# The following should probably be 256 but this lengthens mandelbrot generation 
# time substantially
MANDELBROT_STEPS=128

def pointInMandelbrotSet(z0Real, z0Imag, cReal, cImag):

    x = z0Real
    y = z0Imag
    nx = ny = 0.0
    for i in range(MANDELBROT_STEPS):

        # Calculate the real part of the sequence
        nx = (x * x) - (y * y) + cReal
        # Calculate the imaginary part of the sequence
        ny = 2 * x * y + cImag
        # Check magnitude at each step
        # We check if it's greater than 2
        # which means the point diverges towards infinity
        if ((nx * nx) + (ny * ny)) > 4:
            return i
        
        x = nx
        y = ny
  
    # Point in mandelbrot set
    return MANDELBROT_STEPS


# Draw Mandelbrot set
# Drawing occurs on black background unless paintBackground is True
def drawMandelbrotSet(paletteNumber, paintBackground, scale):

    # Generate specified palette
    #generatePalette(paletteNumber)

    if (paintBackground):
        color = setRandomColor()
        tft.fillScr(color) 
  

    xOfs = WIDTH_LANDSCAPE  / 2.0
    yOfs = HEIGHT_LANDSCAPE / 2.0

    for x in range(WIDTH_LANDSCAPE):
        newReal = scale * float((x - xOfs) / xOfs)
  
        for y in range(HEIGHT_LANDSCAPE):
            newImag = scale * float((y - yOfs) / yOfs)
  
            iterations = pointInMandelbrotSet(0, 0, newReal, newImag)
            if iterations != MANDELBROT_STEPS:
                # Map 128 iterations into 256 colors
                iterations *= 2
  
            # Retrieve color from current palette
            color = setRandomColor() #palette[iterations].red,
                   #palette[iterations].green,
                   #palette[iterations].blue)
            tft.drawPixel(x, y, color)

# Generate a random signed 10 digit floating point value
def generateRandomFloat():
    return random.random()


# Draw julia set
def drawJuliaSet(paletteNumber, cReal, cImag):

    # Generate specified palette
    #generatePalette(paletteNumber)

    xOfs = WIDTH_LANDSCAPE  / 2.0
    yOfs = HEIGHT_LANDSCAPE / 2.0

    for x in range(WIDTH_LANDSCAPE):
        newReal = (float(x - xOfs) / xOfs)
    
        for y in range(HEIGHT_LANDSCAPE):
            newImag = (float(y - yOfs) / yOfs)
    
            iterations = pointInMandelbrotSet(newReal, newImag, cReal, cImag)
            if (iterations != MANDELBROT_STEPS):
                # Map 128 iterations into 256 colors
                iterations *= 2
        
                # Retrieve color from current palette
                color = setRandomColor() # palette[iterations].red, palette[iterations].green, palette[iterations].blue)
                tft.drawPixel(x, y, color)


#*****************************************************************#
#**                     Spirograph Functions                    **
#*****************************************************************

# Greatest common divisor using Euclid's method
def gcd(x, y):
    if (x % y) == 0:
        return y
    return gcd(y, x % y)


# Compute revolutions to complete spirograph pattern
# computed from radii of fixed and moving circles
def revolutions(R, r):
    return (r / gcd(R, r)) * 7


def drawSpirograph():

    # Pick parameters randomly

    # Pick moving circle position: inside or outside
    mcInside = (random.randint(0,2) == 1)

    # Pick fcRadius and mcRadius accordingly
    fcRadius = 0 
    mcRadius = 0

    if (mcInside):
        # Moving circle inside fixed circle
        fcRadius = random.randint(t100, HEIGHT_LANDSCAPE // 2)
        # Moving circle radius must be smaller than fixed circle radius
        mcRadius = random.randint(t46, fcRadius)
    else:
        # Moving circle outside fixed circle
        fcRadius = random.randint(40, 65)
        mcRadius = random.randint(26, fcRadius)

    while ((120 + fcRadius + (2 * mcRadius)) >= HEIGHT_LANDSCAPE):
        fcRadius = random.randint(40, 65)
        mcRadius = random.randint(26, fcRadius)
    
  

    # Pick moving circle offset
    mcOffset = random.randint(10, mcRadius)

    # Pick color mode: single, multi or random
    colorMode = random.randint(0,3)

    # Pick drawing mode: point or line
    drawingModePoint = (random.randint(0,2) == 1)

    # Calculate iterations to perform
    iterations = revolutions(fcRadius, mcRadius)

    redBits   = random.randint(0,NUM_OF_COLOR_VALUES)
    greenBits = random.randint(0,NUM_OF_COLOR_VALUES)
    blueBits  = random.randint(0,NUM_OF_COLOR_VALUES)

    x = 0
    y = 0
    prevx = 0
    prevy = 0

    # Controls the step size; low values of r (e.g. 2) make jagged pattern, so s will be small
    # for low value of r; the effect is not directly proportinal, but sqrt (arbitrary)
    exp = random.randint(0, 5)
    scale = pow(10, exp)
    scaleFactor = 4.0 / scale
    s = scaleFactor * sqrt(mcRadius)

    xOffset = WIDTH_LANDSCAPE  // 2
    yOffset = HEIGHT_LANDSCAPE // 2

    rSum  = fcRadius + mcRadius
    rDiff = fcRadius - mcRadius

    # For multiColor, step to change for each color 
    redStep = 1
    greenStep = 1
    blueStep = 1

    si = int(s)
    if si == 0:
        si = 1
    for t in range(0,int(iterations),si):
        prevx = x
        prevy = y
        # Determine color mode ?
        if colorMode == 0:
            # Single color mode. Use previous selected color every iteration
            pass   # ???
    
        elif colorMode == 1:
    
            # Multi color mode
            # Randomly change one color in each iteration; makes more interesting patterns
            whichColor = random.randint(0,3) 
    
            if whichColor == 0:
                if (redBits < 1):
                    redStep = 1       
                if (redBits > 254):
                    redStep = -1          
                redBits += redStep
 
            elif whichColor == 1:
                if (greenBits < 1):
                    greenStep = 1
                if (greenBits > 254):
                    greenStep = -1
                greenBits += greenStep
            elif whichColor == 2:
                if (blueBits < 1):
                    blueStep = 1
                if (blueBits > 254):
                    blueStep = -1
                blueBits += blueStep
    
        elif colorMode == 2:
            # Random color mode 
            redBits   = random.randint(0,NUM_OF_COLOR_VALUES)
            greenBits = random.randint(0,NUM_OF_COLOR_VALUES)
            blueBits  = random.randint(0,NUM_OF_COLOR_VALUES)
          
          
        
        # Select new drawing color
        color = setColor(redBits, greenBits, blueBits)

        if (mcInside):
            # Moving circle is inside the fixed circle
            exprResult = (rDiff * t) / float(mcRadius)

            x = int(((rDiff * cos(t)) + (mcOffset * cos(exprResult)) + xOffset))
            y = int(((rDiff * sin(t)) - (mcOffset * sin(exprResult)) + yOffset))
    
        else:
    
            # Moving circle is outside the fixed circle
            exprResult = (rSum * t) / float(mcRadius)
            x = int(((rSum * cos(t)) - (mcOffset * cos(exprResult)) + xOffset))
            y = int (((rSum * sin(t)) - (mcOffset * sin(exprResult)) + yOffset))
        
        # Do drawing
        if (drawingModePoint):
            # Drawing individual points
            tft.drawPixel(x, y, color)
          
        else :
            # Drawing lines
            if (t > 0):
                tft.drawLine(prevx, prevy, x, y, color)
 


#*****************************************************************
#**                       Plasma Functions                      **
#*****************************************************************

NUM_OF_PLASMAS =4
PLASMA_TYPE_0  =0
PLASMA_TYPE_1  =1
PLASMA_TYPE_2  =2
PLASMA_TYPE_3  =3

def drawPlasma(plasmaType, paletteNumber):

    colorIndex = 0
    value = 0

    # Generate specified palette
    #generatePalette(paletteNumber)

    # Generate some factors to alter plasma
    f1 = float(random.randint(2, 64))
    f2 = float(random.randint(2, 64))
    f3 = float(random.randint(2, 64))
    
    print("Julia set")

    for x in range(WIDTH_LANDSCAPE):
        for y in range(HEIGHT_LANDSCAPE):
            # Determine plasma type
            if plasmaType == PLASMA_TYPE_0:     
                value = sin(sqrt((x - XMID) * (x - XMID) + (y - YMID) * (y - YMID)) / f1)
            elif plasmaType == PLASMA_TYPE_1: 
                value = (sin(x / f1) + sin(y / f1)) / 2.0
            elif plasmaType == PLASMA_TYPE_2:
                value = (sin(x / f1) + sin(y / f2) + sin((x + y) / f3)) / 3.0
            elif plasmaType == PLASMA_TYPE_3:   
                value  = sin(x / f1)
                value += sin(y / f2)
                value += sin(sqrt(((x - XMID) * (x - XMID)) + ((y - YMID) * (y - YMID))) / f3)
                value /= 3.0
                
              
            # Scale -1 ... +1 values to 0 ... 255
            value = (value * 128.0) + 128.0
            #print("Julia set, value = {:f}".format(value))
            #colorIndex = int(value) % 256
            color = setRandomColor() # palette[colorIndex].red,
                           #palette[colorIndex].green,
                           #palette[colorIndex].blue)
            tft.drawPixel(x, y, color)
    
  


#*****************************************************************
#**                   Display Pattern Functions                 **
#*****************************************************************

def circlesPattern():
    x = 0
    y= 0
    radius = 0

    #while (True):
    # Draw some random circles
    for i in range(70):

        color = setColor(random.randint(0,NUM_OF_COLOR_VALUES),
                         random.randint(0,NUM_OF_COLOR_VALUES),
                         random.randint(0,NUM_OF_COLOR_VALUES))

        radius = random.randint(0,50) + 2

        # Make sure to keep the circle's coordinates in bounds
        x = random.randint(0,MAX_X_LANDSCAPE)
        while (((x - radius) < 1) or ((x + radius) > MAX_X_LANDSCAPE - 1)):
            x = random.randint(0,MAX_X_LANDSCAPE)
      

        y = random.randint(0,MAX_Y_LANDSCAPE)
        while (((y - radius) < 1) or ((y + radius) > MAX_Y_LANDSCAPE - 1)):
            y = random.randint(0,MAX_Y_LANDSCAPE)
      
        # Draw some open and some filled circles
        flag = (random.randint(0,3) == 1)
        if not flag:
            tft.drawCircle(x, y, radius, color)
        else:
            tft.fillCircle(x, y, radius, color)
      
        #delay(0.002)
    
        checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()
  


def linesPattern():

    x=0
    y=0
    xPrev=0
    yPrev=0

    # Pick a random palette
    #paletteNumber = random.randint(0,NUM_OF_PALETTES)
    #generatePalette(paletteNumber)

    # Pick a random place to start within the palette
    #colorIndex = random.randint(0,PALETTE_SIZE)

    xPrev = WIDTH_LANDSCAPE  // 2
    yPrev = HEIGHT_LANDSCAPE // 2

    #while (True):

    for i in range(80):
        color = setRandomColor() #palette[colorIndex].red,
                   #palette[colorIndex].green,
                   #palette[colorIndex].blue)
        #colorIndex+= 1
        #colorIndex %= PALETTE_SIZE
        x = random.randint(0,MAX_X_LANDSCAPE)
        y = random.randint(0,MAX_Y_LANDSCAPE)
        tft.drawLine(x, y, xPrev, yPrev, color)
        xPrev = x
        yPrev = y
        #delay(0.006)
    
        checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()
  

def webPattern():

    ITERATIONS=16

    colorIndex = 0

    #while (True):

    #createHSVColor(ITERATIONS, colorIndex++, color)
    color = setRandomColor() #color.red, color.green, color.blue)

    for y in range(0,t240,5):
        tft.drawLine(0, y, int(y * 1.33), t239, color)

    #createHSVColor(ITERATIONS, colorIndex++, &color)
    color = setRandomColor ()
    #color.red, color.green, color.blue)

    for y in range(t239,0,-5):
        tft.drawLine(t319, y, int(y * 1.33), 0, color)
    

    #createHSVColor(ITERATIONS, colorIndex++, &color)
    color = setRandomColor ()#color.red, color.green, color.blue)

    for y in range(t239,0, -5):
        tft.drawLine(0, y, t320 - int(y * 1.33), 0, color)

    color = setRandomColor () #color.red, color.green, color.blue)

    for y in range(0,t240,5):
        tft.drawLine(t319, y, t320 - int(y * 1.33), t239, color)

    checkForTimeout()


def spirographPattern():
    drawSpirograph()

    checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()
  


def mandelbrotPattern():

    scale = 1.5

    # Pick a random scale factor
    scaleFactor = random.randint(0,4)
    if scaleFactor == 0:
        scale = 1.5
    elif scaleFactor == 1:
        scale = 1.25
    elif scaleFactor ==  2:
        scale = 1.1
    elif scaleFactor ==  3:
        scale = 2.0   
    elif scaleFactor ==  4:
        scale = 2.5
    
    # Determine if mandelbrot set members are colored or black
    paintBackground = (random.randint(0,2) == 1)

    # Draw the set with specified scale and palette
    drawMandelbrotSet(random.randint(0,NUM_OF_PALETTES), paintBackground, scale)

    # Force timeout after generation
    timeOut = 0

    #while (True):
    #  delay(10)
    # checkForTimeout()
  


def juliaPattern():

    # Generate a complex constant as seed for Julia set
    cReal = generateRandomFloat()
    cImag = generateRandomFloat()
  
    # Make sure this complex constant diverges at (0, 0)
    # This prevents some not so interesting Julia sets from being (slowly) rendered
    while (pointInMandelbrotSet(0, 0, cReal, cImag) == MANDELBROT_STEPS):
        cReal = generateRandomFloat()
        cImag = generateRandomFloat()
    
  
    # Draw the hopefully interesting Julia set
    drawJuliaSet(random.randint(0,NUM_OF_PALETTES), cReal, cImag)
  
    # Force timeout after generation
    timeOut = 0
  
    #while (True):
    #  delay(10)
    # checkForTimeout()
    


def bigPixelPattern():

    BORDER_WIDTH=16
    BPWidth     =60
    BPHeight    =40

    #while (True):
    numberOfColors = random.randint(0,NUM_OF_COLOR_VALUES)
    colorIndex = random.randint(0,numberOfColors)

    for countHoriz in range(4):
        for countVert in range(4):
            # Calculate color
            #createHSVColor(numberOfColors, colorIndex++, &color)
            color = setRandomColor() #color.red, color.green, color.blue)
    
            xPos = BORDER_WIDTH + countHoriz * (BPWidth + BORDER_WIDTH)
            yPos = BORDER_WIDTH + countVert * (BPHeight + BORDER_WIDTH)
    
            # Create filled rect
            tft.drawRect(xPos, yPos, xPos + BPWidth + 1, yPos + BPHeight + 1, color)
    delay(0.006)
          
    
    # Check for termination
    checkForTimeout()
  


def bigPixel2Pattern():

    # Fit three rows of four circles onto the display
    HBW  =16
    VBW   =15
    RADIUS=30

    #while (True):

    for row in range(3):
        for col in range(4):

            # Create random color for the circle
            color = setRandomColor() #random.randint(0,NUM_OF_COLOR_VALUES),
                         #random.randint(0,NUM_OF_COLOR_VALUES),
                         #random.randint(0,NUM_OF_COLOR_VALUES))
    
            # Calculate location of circle
            x = (col + 1) * (HBW + RADIUS) + (col * RADIUS)
            y = (row + 1) * (VBW + RADIUS) + (row * RADIUS)
    
            # Draw the filled circle
            tft.drawCircle(x, y, RADIUS, color)
    
    # Check for termination
    checkForTimeout()
  


# Support routine for pattern below
def drawCircleOfCircles(colorIndex, 
                        numberOfCircles, 
                        largeRadius, 
                        smallRadius):

    cx = WIDTH_LANDSCAPE  / 2
    cy = HEIGHT_LANDSCAPE / 2

    for i in range(numberOfCircles):
        # Calculate color
        #createHSVColor(numberOfCircles, colorIndex++, color)
        color=setRandomColor()#color.red, color.green, color.blue)
    
        angle = i * 2 * pi / numberOfCircles
        x = cx + cos(angle) * largeRadius
        y = cy + sin(angle) * largeRadius
        tft.fillCircle(int(x), int(y), int(smallRadius), color)
  


def circleOfCirclesPattern():

    width = WIDTH_LANDSCAPE
    scaleFactor= 0.0
    numberOfCircles= 0
    colorIndex = 0
    #while (True):
    for j in range(10):
        for i in range(3):
            numberOfCircles = 8 + (i * 8)
            scaleFactor = 0.21 + (i * 0.21)
        
            largeRadius = (width / 2) * scaleFactor
            largeCircle = 2 * pi * largeRadius
            smallRadius = (largeCircle / numberOfCircles) / 2
        
            drawCircleOfCircles(colorIndex, numberOfCircles, 
                                largeRadius, smallRadius)
            colorIndex += 2
            #delay(0.005)
        
            # Check for termination
            checkForTimeout()
    
 


def plasmaPattern():

  #while (True):
    plasmaType = random.randint(0,NUM_OF_PLASMAS)
    paletteNumber = random.randint(0,NUM_OF_PALETTES)

    # Draw the specified plasma with the specified palette
    drawPlasma(plasmaType, paletteNumber)

    # Check for timeout
    checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()
  


def concentricSquaresPattern():

    #colorIndex = random.randint(0,PALETTE_SIZE)

    x1= x2= y1= y2= 0

    xInc = 3
    yInc = 2

    #paletteNumber = random.randint(0,NUM_OF_PALETTES)
    #generatePalette(paletteNumber)

    #while (True):
    # Set initial coordinates
    x1 = XMID - 3
    x2 = XMID + 3
    y1 = YMID - 1
    y2 = YMID + 1
    
    while ((x1 >= 0) and (x2 < WIDTH_LANDSCAPE) and
      (y1 >= 0) and (y2 < HEIGHT_LANDSCAPE)):
    
        color = setRandomColor()
        #colorIndex+= 1
        #colorIndex %= PALETTE_SIZE
      
        tft.drawRect(x1, y1, x2, y2, color)
        x1 -= xInc
        x2 += xInc
        y1 -= yInc
        y2 += yInc
      
        delay(0.005)
      
    # Check for timeout
    checkForTimeout()
  

def concentricCirclesPattern():

    radius = 0
    radiusInc = 1
  
    # Pick a random palette
    #paletteNumber = random.randint(0,NUM_OF_PALETTES)
    #generatePalette(paletteNumber)
  
    # Pick a random place to start within the palette
    #colorIndex = random.randint(0,PALETTE_SIZE)
  
    #while (True):
  
    radius = 2

    while ((radius < XMID) and (radius < YMID)):

        color = setRandomColor()
        #colorIndex += 1
        #colorIndex %= PALETTE_SIZE
  
        tft.drawCircle(XMID, YMID, radius, color)
        radius += radiusInc
  
        delay(0.005)
    
    # Check for timeout
    checkForTimeout()
  


# Support routine for display pattern below
def drawRotatingText(radius, strng):
    x=0
    y=0

    for degrees in range(0,360,45):
        rads = degrees * pi / 180.0
        x = XMID - radius * cos(rads)
        y = YMID - radius * sin(rads)
    
        if (degrees <= 90):
            x += 8
            y -= 8
        
        color = setColor(0, 0, 0)
        print(strng, x, y, degrees)
        if (degrees == 0):
            delay(5)
        else :
            delay(3)
        
    
        color = setColor(255, 255, 255)
        print(strng, x, y, degrees)
        if (degrees == 0):
            delay(3)
        else:
            delay(2)
        
  


# Display revolving text messages
def textPattern():

    str1 = "Contemplator"
    str1Length =len(str1)
    str1PixelWidth = str1Length * 16
    radius1 = str1PixelWidth / 2

    str2 = "Python3 + tlkinter"
    str2Length = len(str2)
    str2PixelWidth = str2Length * 16
    radius2 = str2PixelWidth / 2

    # Set fill and background color to white
    tft.fillScr(setColor(255, 255, 255))
    #setBackColor(255, 255, 255)

    #while (True):
    #drawRotatingText(radius1, str1)
    create_text(20, 20, text=str1, anchor=NW)

    checkForTimeout()

    #drawRotatingText(radius2, str2)
    create_text(20, 40, text=str2, anchor=NW)

    checkForTimeout()
  


def vertPaletteLinesPattern():

  #while (True):
    # Pick a random palette
    paletteNumber = random.randint(0,NUM_OF_PALETTES)
    #generatePalette(paletteNumber)

    # Pick a random place to start within the palette
    colorIndex = random.randint(0,PALETTE_SIZE)
    for y in range(HEIGHT_LANDSCAPE):

        color = setRandomColor() #palette[colorIndex].red,
                   #palette[colorIndex].green,
                   #palette[colorIndex].blue)
        colorIndex +=1
        colorIndex %= PALETTE_SIZE

        tft.drawLine(MIN_X_LANDSCAPE, y, MAX_X_LANDSCAPE, y, color)
        delay(0.005)
    
    checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()
  


def horizPaletteLinesPattern():

  #while (True):
    # Pick a random palette
    paletteNumber = random.randint(0,NUM_OF_PALETTES)
    #generatePalette(paletteNumber)

    # Pick a random place to start within the palette
    colorIndex = random.randint(0,PALETTE_SIZE)
    for x in range(WIDTH_LANDSCAPE):

        color = setRandomColor() #palette[colorIndex].red,
                   #palette[colorIndex].green,
                   #palette[colorIndex].blue)
        #colorIndex+=1
        #colorIndex %= PALETTE_SIZE

        tft.drawLine(x, MIN_Y_LANDSCAPE, x, MAX_Y_LANDSCAPE, color)
        delay(0.005)
    
    checkForTimeout()
    delay(BETWEEN_PATTERN_DELAY_SECONDS)
    clrDisplay()

def burstPattern():

    # Randomly toggle burst background between black and gray
    if (random.randint(0,2) == 1):
        # Set background to gray
        tft.fillScreen(BLACK) #setColor(31, 63, 31))

    # Pick the attributes of the burst
    smallRadius = random.randint(8, 30)
    mediumRadius = random.randint(smallRadius + 10, 75)
    largeRadius = YMID
    
    degreeInc = 15
    
    # Pick the burst spoke pitch
    rand = random.randint(0,7)
    if rand ==  0:
        degreeInc = 6    
    elif rand == 1:
        degreeInc = 10    
    elif rand == 2:
        degreeInc = 12    
    elif rand == 3:
        degreeInc = 15   
    elif rand == 4:
        degreeInc = 18     
    elif rand == 5:
        degreeInc = 20   
    elif rand == 6:
        degreeInc = 30

    xi = xo = yi=  yo = 0
    rads = 0.0
    
    #numberOfSpokes = 360.0 / degreeInc
    colorIndex = 0
    inner = False
    
    # Pick the delay for this time through
    delayTime = random.randint(1, 10)/1000.0
    
    #while (True):
    
    for degree in range(0, 360, degreeInc):

        # Convert degrees to radians
        rads = degree* pi / 180.0

        xi = smallRadius * cos(rads) + XMID
        yi = smallRadius * sin(rads) + YMID

        if (inner):
            # Drawing shorter spokes
            xo = mediumRadius * cos(rads) + XMID
            yo = mediumRadius * sin(rads) + YMID
        
        else :
            # Drawing longer spokes
            xo = largeRadius * cos(rads) + XMID
            yo = largeRadius * sin(rads) + YMID
      
        # Toggle inner to outer and vise versa
        inner = not inner

        # Create longer spoke color

        #createHSVColor(numberOfSpokes, colorIndex, color)
        colorIndex += 1

        # Set spoke color
        color = setRandomColor()#color.red, color.green, color.blue)

        # Draw the spoke
        tft.drawLine(int(xi), int(yi), int(xo), int(yo), color)

        delay(delayTime)
    
    colorIndex += 2
    checkForTimeout()
  



def offsetCirclePattern():

    #struct RGB color
    color =  setRandomColor()
        
    even = (random.randint(0,2) == 0)
    i = 1
    while (i == 1):
        i+= 1

        numberOfColors = random.randint(0,NUM_OF_COLOR_VALUES)
        colorIndex = random.randint(0,numberOfColors)
        #radiusIncrement = random.randint(4, 14)
        radiusIncrement = 4
        #delayTime = random.randint(2, 10) / 10000.0
        delayTime = 0.0
    
        for radius in range(1,YMID,radiusIncrement):
    
            # Create and set color
            #createHSVColor(numberOfColors, colorIndex, color)
            colorIndex += 1
            color = setRandomColor()#color.red, color.green, color.blue)
    
            if (even):
                tft.drawCircle(radius , YMID, radius, color)
           
            else:
                tft.drawCircle(radius, radius, radius, color)
         
            delay(delayTime)
    
            # Create and set color
            #createHSVColor(numberOfColors, colorIndex, color)
            #colorIndex += 1
            color = setRandomColor() #color.red, color.green, color.blue)
            if (even):
                tft.drawCircle(WIDTH_LANDSCAPE - radius , YMID, radius, color)
           
            else:
                tft.drawCircle(WIDTH_LANDSCAPE - radius, radius, radius, color)
          
            delay(delayTime)
    
            # Create and set color
            #createHSVColor(numberOfColors, colorIndex, color)
            colorIndex += 1
            color = setRandomColor() #color.red, color.green, color.blue)
            if (even):
                tft.drawCircle(XMID , radius, radius, color)
         
            else :
                tft.drawCircle(radius, HEIGHT_LANDSCAPE - radius - 1, 
                           radius, color)
          
            delay(delayTime)
    
            # Create and set color
            #createHSVColor(numberOfColors, colorIndex, color)
            colorIndex += 1
            color = setRandomColor() #color.red, color.green, color.blue)
            if (even):
                tft.drawCircle(XMID , HEIGHT_LANDSCAPE - radius - 1, 
                           radius, color)
            
            else:
                tft.drawCircle(WIDTH_LANDSCAPE - radius,
                           HEIGHT_LANDSCAPE - radius - 1, radius, color)
          
            delay(delayTime)
            
       
            even = not even
    
            # Check for timeout
            checkForTimeout()
        delay(BETWEEN_PATTERN_DELAY_SECONDS)

        clrDisplay()
     
def draw1():
    wid = 1  #random.randint(1,4)
    for x in range(0, t319, 5):
        tk_rgb = setRandomColor()
        tft.drawLine(0,0,x,tft.height, tk_rgb)
        tft.drawLine(0,tft.height,x,0, tk_rgb)
        tft.drawLine(t319,0,x,tft.height, tk_rgb)
        tft.drawLine(t319,tft.height,x,0, tk_rgb) 
    return

index = 5 #0
MAX_INDEX = 19

def  cycle_display(index):
    if index == 1:
        print("Cat's cradle")
        draw1()
    elif index == 2:
        print("Offset circle")
        offsetCirclePattern()
    elif index == 3:
        print("Burst")
        burstPattern()
    elif index == 4:    
        print("Concentric circles")
        concentricCirclesPattern()
    elif index == 5:
        print("Web")
        webPattern()
    elif index == 6:
        print("Circle of circles")
        circleOfCirclesPattern()
    elif index == 7:
        print("Concentric squares")
        concentricSquaresPattern()
    elif index == 8:
        drawSpirograph()
    elif index == 9:
        print("lines")
        linesPattern()
    elif index == 10:
        print("Circles")
        circlesPattern()

def nextDisplay():
    global index, MAX_INDEX
    index += 1

    clrDisplay()
    cycle_display(index)
    if index >= MAX_INDEX:
        index = 0    


#--------------------------------------------------------------------



#--------------------------------------------------------------------
                                                                     
if __name__ == '__main__':                                           
                                                                     
    try:                                    
        print("Contemplator")
        print("Enter cntrl-C to quit")      
        setup()                             
        while (True):                       
            nextDisplay()                          
    except KeyboardInterrupt:               
        print("Keyboard interrupt, exiting")
        quit()            



