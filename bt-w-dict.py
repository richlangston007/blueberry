#!/usr/bin/python
#Check to see if anyone is home

import bluetooth
import time
import sys
from Adafruit_IO import *


sys.stdout =open("/home/pi/bluberry/logs/bt-out.log","w")
sys.stderr =open("/home/pi/bluberry/logs/bt-err.log","w")
print "Starting Bluetooth detection process"
sys.stdout.flush()
time.sleep(30)
#open the file bluetooth-devices and get the BT addresses of our phones
phones={}

try:
    devfile=open("/home/pi/bluberry/bluetooth-devices","r")
    temp=file.readlines(devfile)
    for i in temp:
        phones[i.rstrip("\n")]="away"
    devfile.close()
except:
    sys.exit("Can't read bluetooth-devices.  Does it exist?")
#
# Adafruit io
aio = Client('10b2825458e547d8adf6aca7d9633341')

lastSeen= time.time()
home=False
#time to wait before turning down the heat
delayTime=1*60
#time to wait between bt scans
pause=3*60

#first figure out who is home
for phone in phones:
    thisPhone = bluetooth.lookup_name(phone)
    if ( thisPhone != None ):
        phones[phone]="home"
        print (thisPhone, " is home")

print (phones)
while True:
    for phone in phones:
        thisPhone = bluetooth.lookup_name(phone)
        if ( thisPhone != None ):
            lastSeen=time.time()
            phones[phone] = "home"
            print (thisPhone, 'is home')
            try:
                aio.send("someone-home","yes")
            except:
                print("Adafruit cloud timeout/issue")
            break
    if ( time.time()-lastSeen >= delayTime):
        Home=False
        print ('no one is home')
        try:
            aio.send("someone-home","no")
        except:
            print("Adafruit cloud timeout/issue")
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(pause)
