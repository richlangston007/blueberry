#!/usr/bin/env python3

from Adafruit_IO import *
import time
import DHT22
import pigpio
import DHT22
import datetime
import sys

#sys.stdout =open("/home/pi/bluberry/logs/main-out.log","w")
#sys.stderr =open("/home/pi/bluberry/logs/main-err.log","w")

# Adafruit io
aio = Client('10b2825458e547d8adf6aca7d9633341')


#keyFile=open("/home/pi/bluberry/adafruit-key.txt","r")
#temp=file.readlines(keyFile)
#print ("key ",temp)
#aio=Client([temp.rstrip("\n")])
#devfile.close()
#except:
#        sys.exit("Can't read bluetooth-devices.  Does it exist?")

# Intervals of about 2 seconds or less will eventually hang the DHT22.
INTERVAL=60
nextTime=time.time()+INTERVAL

pi = pigpio.pi()

s = DHT22.sensor(pi, 4, LED=27, power=8)

#pin for heat on/off
heatRelay = 19
pi.set_mode(heatRelay, pigpio.OUTPUT)

temp=68.0
systemStatus= 'ON'
targetTemp = 68
remoteTemp=68
remoteSwitch= "ON"
awayTemp=58
homeTemp=68
nightTemp=58
newNightTemp=0
nightTime=[22,10]
wakeTime=[6,30]
night = False
firstTime=True
someoneHome = True
#get data from the web
try:
    data=aio.receive("on-off")
    remoteSwitch = data.value
    data=aio.receive("target-temp")
    remoteTemp=int(data.value)
    targetTemp=int(data.value)
    data=aio.receive("night-temp")
    newNightTemp=int(data.value)
except:
    print("Cloud unreachable, using built-in values for startup")

while True:
     sys.stdout.flush()
     sys.stderr.flush()

#read the sensor every INTERVAL
     if ( time.time() >= nextTime ):
        s.trigger()
        time.sleep(0.2)
        temp = s.temperature()*9.0/5+32
#        humid = float(str(s.humidity))
#        if humid < 0:
#            humid=0
#   need bounds checking for humidity
#        if (int(s.humidity) < 0):
#             humidity=0
#        else:
#            humidity=s.humidity()
        nextTime += INTERVAL
        print ("times ",time.time(), nextTime)
#
#exchange data with the cloud, including bluetooth status from bt script
#
        try:
              aio.send('t-temp',temp )
              aio.send('t-humid',s.humidity() )
              data=aio.receive("on-off")
              remoteSwitch = data.value
              data=aio.receive("target-temp")
              remoteTemp=int(data.value)
              data=aio.receive("night-temp")
              newNightTemp=int(data.value)
              data=aio.receive("someone-home")
              if (data.value == "yes"):
                  someoneHome=True
              else:
                  someoneHome=False
              print( remoteSwitch, remoteTemp, data.value)
        except:
              print('Adafruit send failed, skipping update ')
        else:
              print("{} {:3.2f} {:3.2f} ".format( s.humidity(), temp, s.staleness(), ))
              print ("Home:",someoneHome," targetTemp:", targetTemp)


#
#deciscion making
#
# Was the system just turned off via the web?
     if ( remoteSwitch != systemStatus ):
          if (remoteSwitch == 'ON'):
              pi.write(heatRelay,1)
              systemStatus='ON'
              print ('System switched on remotely')
          else:
              pi.write(heatRelay,0)
              systemStatus='OFF'
              print('System switched off remotely')
# did the remote DAY or NIGHT  temp change?
     if ( homeTemp != remoteTemp ):
              homeTemp=remoteTemp
              print ('Remote temp change.  New temp is', homeTemp)
     if (newNightTemp != nightTemp):
              nightTemp=newNightTemp
              print ("Night temp set remotely")
# See if it is night time and adjust for setback.
# if no one is home, stay at the away temp
# otherwise, it's daytime.  Still need to check if no on is home
     now=datetime.datetime.now()
     timeNow=now.time()

     if (timeNow >= datetime.time(nightTime[0],nightTime[1])) or ( now.time() <= datetime.time(wakeTime[0],wakeTime[1])):

          night=True
          if ( someoneHome is True ):
              targetTemp=nightTemp
#              print('in night mode')
          else:
              targetTemp=awayTemp
     else:
          night=False
          if ( someoneHome is True ):

              targetTemp=homeTemp
          else:
              targetTemp=awayTemp

# if thet system is on, and it's less than target, turn on heat
     if (systemStatus == 'ON'):
          if ( temp < targetTemp-1 ):
              pi.write(heatRelay,1)
          else:
              pi.write(heatRelay,0)


s.cancel()
pi.stop()
