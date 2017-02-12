#!/usr/bin/env python3

from Adafruit_IO import *

import time

import DHT22

import pigpio

import DHT22


# Adafruit io 
aio = Client('f7379eb7d7d240c98f559ba13e7c3295')

# Intervals of about 2 seconds or less will eventually hang the DHT22.
INTERVAL=10
nextTime=time.time()+INTERVAL

pi = pigpio.pi()

s = DHT22.sensor(pi, 4, LED=27, power=8)

#pin for heat on/off
heatRelay = 19
pi.set_mode(heatRelay, pigpio.OUTPUT)


#default temperature
targetTemp = 68

while True:


   if ( time.time() >= nextTime ): 
      s.trigger()

      time.sleep(0.2)

      temp = s.temperature()*9.0/5+32

      print("{} {:3.2f} {:3.2f} {} {} {} {}".format(
         s.humidity(), temp, s.staleness(),
         s.bad_checksum(), s.short_message(), s.missing_message(),
         s.sensor_resets()))
      aio.send('t-temp',temp )
      aio.send('t-humid',s.humidity() )
      nextTime += INTERVAL
      if ( temp < targetTemp-1 ):
          pi.write(heatRelay,1)
      else:
          pi.write(heatRelay,0)



s.cancel()

pi.stop()

