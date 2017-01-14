#!  /usr/bin/python
import time, sys, re, os

def ping(IP, number = 1):
    pinged = False
    if IP == None:
        return False
    else:
        lifeline = re.compile(r"(\d) received")
        report = ("No response","Partial Response","Alive")         
        for i in range(0,number):
            pingaling = os.popen("ping -q -c 2 "+IP,"r")
            sys.stdout.flush()
            while 1==1:
               line = pingaling.readline()
               if not line: break
               igot = re.findall(lifeline,line)
               if igot:
                if int(igot[0])==2:
                    pinged = True
                else:
                    pass
        return pinged


def reset_wlan():
    os.system('sudo service networking restart') 
    #os.system('sudo ifdown --force wlan0') 
    #os.system('sudo ifup wlan0')
    #os.system('sudo killall python')

while 1==1:
    count = 0
    while not ping('192.168.192.1'):
        reset_wlan()
        time.sleep(60)
        count += 1
        if count > 2:
            pass
            os.system('sudo reboot')    
    time.sleep(60)    