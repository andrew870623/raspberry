"""This example is for Raspberry Pi (Linux) only!
   It will not work on microcontrollers running CircuitPython!"""
 
import os
import math
import time
import sys
 
import busio
import board
 
import numpy as np
import pygame
from pygame.locals import *
from scipy.interpolate import griddata
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("/home/pi/Desktop/carematch-c8be7-firebase-adminsdk-w2so4-0d76be5ef4.json")
firebase_admin.initialize_app(cred)
db=firestore.client()

 
from colour import Color
 
import adafruit_amg88xx
 
i2c_bus = busio.I2C(board.SCL, board.SDA)
 
#low range of the sensor (this will be blue on the screen)
MINTEMP = 21.
 
#high range of the sensor (this will be red on the screen)
MAXTEMP = 30.
 
#how many color values we can have
COLORDEPTH = 1024
 
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
 
#initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index
 
#sensor is an 8x8 grid so lets do a square
height = 720
width = 720
 
#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))
 
#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]
 
displayPixelWidth = width/ 30
displayPixelHeight = height/ 30
 
lcd = pygame.display.set_mode((width, height))
 
lcd.fill((255, 0, 0))
 
pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0, 0, 0))
pygame.display.update()
 
#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))
  
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
 
#let the sensor initialize
time.sleep(.1)
 
while True:
    #print(sensor.pixels)
    x=str(sensor.pixels)
    #read the pixels
    pixels = []
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
 
    #perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
 
    #draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)],
                             (displayPixelHeight * ix, displayPixelWidth * jx,
                              displayPixelHeight, displayPixelWidth))
 
    pygame.display.update()
    doc={"pixels":x}
    
    for event in pygame.event.get():
        #if event.type == pygame.MOUSEBUTTONUP:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print("keypress detected")
                collection_ref=db.collection("pixels")
                collection_ref.add(doc)
            if event.key == pygame.K_z:
                pygame.quit()
                sys.exit()
                    
