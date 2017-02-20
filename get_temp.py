#!/usr/bin/env python3

from Adafruit_IO import *
import time
import DHT22
import pigpio
import DHT22
import datetime


# Adafruit io 
aio = Client('10b2825458e547d8adf6aca7d9633341')

# Intervals of about 2 seconds or less will eventually hang the DHT22.
INTERVAL=10
nextTime=time.time()+INTERVAL

pi = pigpio.pi()

s = DHT22.sensor(pi, 4, LED=27, power=8)

#pin for heat on/off
heatRelay = 19
pi.set_mode(heatRelay, pigpio.OUTPUT)


systemStatus= 'OFF'  
targetTemp = 68  
remoteTemp=68
remoteSwitch= False
awayTemp=58
homeTemp=68
nightTemp=58
#get the temps from the web
try:
    data=aio.receive("on-off")
    remoteSwitch = data.value
    data=aio.receive("target-temp")
    remoteTemp=int(data.value)
    targetTemp=int(data.value)
    data=aio.receive("night-temp")
    nightTemp=int(data.value)
except: 
    print("Cloud unreachable, using built-in values for startup")

while True:


   if ( time.time() >= nextTime ): 
      s.trigger()

      time.sleep(0.2)

      temp = s.temperature()*9.0/5+32

      try:
          aio.send('t-temp',temp )
          aio.send('t-humid',s.humidity() )
          data=aio.receive("on-off")
          remoteSwitch = data.value
          data=aio.receive("target-temp")
          remoteTemp=int(data.value)
          data=aio.receive("someone-home")
          if ( remoteTemp != targetTemp ):
              targetTemp=remoteTemp
              homeTemp=remoteTemp
              print ('Remote temp change.  New temp is', targetTemp)
          if (data.value == "yes"):
              someoneHome=True
              targetTemp=homeTemp
          else:
              someoneHome=False
              targetTemp=awayTemp
#          print( remoteSwitch, remoteTemp, data.value)
      except:
          print('Adafruit send failed, skipping update')
      else:
          print("{} {:3.2f} {:3.2f} ".format( s.humidity(), temp, s.staleness(), ))
          print ("Home:",someoneHome," targetTemp:", targetTemp)

      nextTime += INTERVAL
      if ( remoteSwitch != systemStatus ):
          if (remoteSwitch == 'ON'):
              pi.write(heatRelay,1)
              systemStatus='ON'
              print ('System switched on remotely')
          else:
              pi.write(heatRelay,0)
              systemStatus='OFF'
              print('System switched off remotely')
      if (systemStatus == 'ON'):
          if ( temp < targetTemp-1 ):
              pi.write(heatRelay,1)
          else:
              pi.write(heatRelay,0)

      timeNow=datetime.datetime.now()
      print (timeNow.hour, timeNow.minute)

s.cancel()
pi.stop()
