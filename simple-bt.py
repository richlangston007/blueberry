# file: inquiry.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: performs a simple device inquiry followed by a remote name request of
#       each discovered device
# $Id: inquiry.py 401 2006-05-05 19:07:48Z albert $
#

import bluetooth
import time

phones = ["6C:72:E7:A7:C4:92","90:B9:31:97:87:46"]
phonesHome = []
lastSeen= time.time()
home=False
#time to wait before turning down the heat
delayTime=1*60
#time to wait between bt scans
pause=1*60

#first figure out who is home
for phone in phones:
    thisPhone = bluetooth.lookup_name(phone)
    if ( thisPhone != "None" ):
        phonesHome.append(thisPhone)

print ('Currently visible phones',phonesHome)

while True:
    for phone in phones:
        thisPhone = bluetooth.lookup_name(phone)
        if ( thisPhone != None ):
            lastSeen=time.time()
            print (thisPhone, 'is home')
            break
    if ( time.time()-lastSeen >= delayTime): 
        Home=False
        print ('no one is home')
    time.sleep(pause)
