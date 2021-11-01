pollingrate = 0.01
ip="10.101.97.3"
port = 8000

#Imports
from pythonosc import udp_client
from inputs import devices,get_gamepad
import math
import threading
import time
import os
import sys
from math import *


client = udp_client.SimpleUDPClient(ip, port)

print("Starting controller check.")
if devices.gamepads != []:
    print("Gamepad connected.")
else:
    print("No gamepad connected.")
    sys.exit()

Page = 1 #Default Page
class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    #Test Inputs
    def read(self):
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        return [x, y]


    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1

    
if __name__ == "__main__":
    joy = XboxController()
    while True:
        time.sleep(pollingrate)
        if abs(round(joy.LeftJoystickX, 3)) >= 0.1:
            X = (joy.LeftJoystickX)
        else:
            X = 0
        if abs(round(joy.LeftJoystickY, 3)) >= 0.1:
            Y = (joy.LeftJoystickY)
        else:
            Y = 0

        #X=float(input("X Value: "))
        #Y=float(input("Y Value: "))

        tilt=sqrt(X**2+Y**2)
        chord=sqrt((0-X)**2 + (tilt-Y)**2)
        try:
            if chord == 0:
                angle = 0
            elif chord == 2*tilt:
                angle = math.pi
            else:
                angle=2*(asin(chord/(2*tilt)))
        except:
            print("something went wrong to make this zero")
            input("Confirm")
            angle=0
        finaltilt = str(int(round(tilt*90, 0)))
        if joy.LeftJoystickX > 0:
            finalangle = str(int(round(angle * (180/math.pi), 0)))
        elif joy.LeftJoystickX < 0:
            finalangle = str(int(round(-1*(angle * (180/math.pi)), 0)))
        else:
            finalangle = 0
        print(finalangle, finaltilt)
        client.send_message("/eos/chan/246/param/tilt/", finaltilt)
        client.send_message("/eos/chan/246/param/pan/", finalangle)

        

        


