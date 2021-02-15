import json
import functools


def send_command(func):
    @functools.wraps(func)
    def wrapper(*args,  **kwargs):
        cmd_dict = func(*args, **kwargs)
        inpipe = args[0].inpipe
        inpipe.send(cmd_dict)
        return True
    return wrapper
    

class SerialCommands:
    def __init__(self, inpipe):
        self.inpipe = inpipe

    @send_command
    def drive(self, speed, steer=0.0):
        data = {}
        speed, steer = float(speed), float(steer)
        if speed == 0.0:
            data['action'] = 'BRAK'
        else:
            data['action'] = 'MCTL'
            data['speed'] = float(speed)
        data['steerAngle'] = float(steer)
        return data

    @send_command
    def encoder_state(self, enabled):
        data = {}
        data['action'] = 'ENPB'
        data['activate'] = enabled 
        return data
