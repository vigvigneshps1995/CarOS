import os
import sys
import json
import time

from multiprocessing import Pipe, Process, Event
from serialhandler.serialhandler import SerialHandler
from serialhandler.serialcommands import SerialCommands
from Constants import constants
from CarDB import CarDB


class CarDriver():

    def __init__(self):

        # inititalize
        self.db = CarDB()
        self.db.initialize()
        self.encoder = None

        
        # open pipes to communicate with the serial process
        seralR, seralS = Pipe(duplex = False)       # for serial communication 
        encdrR, encdrS = Pipe(duplex = False)       # for encoder communication
        outpipe = {"ENPB": encdrS}

        # initialize serial worker thread
        print ("Establishing connection to MCU...")
        SerialHandler([seralR], [outpipe]).start()
        self.serial_cmd = SerialCommands(seralS)

        # set encoder state to enabled
        self.encoder = self.db.get_encoder_state()
        print ("Current encoder state: ", self.encoder)
        print ("Enabling encoder ...")
        self.serial_cmd.encoder_state(enabled=True)
        self.db.set_encoder_state(enabled=True)
        self.encoder = True 
        print ("Current encoder state: ", self.encoder)
        
        # start encoder reading process
        print ("Spwan encoder process...")

        while True:
            self.start_car()
            time.sleep(3)

    def start_car(self):
        speed, steer = self.db.get_car_speed_angle()
        self.serial_cmd.drive(speed, steer)
        


if __name__ == "__main__":
    car = CarDriver()

