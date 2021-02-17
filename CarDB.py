import os
import sys
import json
import time
import redis as redis

from Constants import constants


class RedisHelper():

    def __init__(self, host):
        self.redis = redis.Redis(host=host)
   
    def _clean(self, str):
        if isinstance(str, bytes):
            return str.decode('unicode_escape')
        return str
     
    def read(self, name, clean=True):
        if not clean:
            return self.redis.get(name)
        else:
            return self._clean(self.redis.get(name))

    def write(self, name, value):
        return self.redis.set(name, value)
    
    def acquire_lock(self, lock, force=False):
        if force:
            self.redis.set(lock, "true")
            return 

        t1 = time.time()
        while(True):
            if self._clean(self.redis.get(lock)) == "false":
                self.redis.set(lock, "true")
                return
            else:
                if time.time() - t1 > constants.REDIS_TIMEOUT:
                    raise Exception("REDIS LOCK TIMEOUT")
                    sys.exit(1)
             
    def release_lock(self, lock, force=True):
        if force:
            self.redis.set(lock, "false")
            return 
        
        t1 = time.time()
        while(True):
            if self._clean(self.redis.get(lock)) == "true":
                self.redis.set(lock, "false")
                return
            else:
                if time.time() - t1 > constants.REDIS_TIMEOUT:
                    raise Exception("REDIS LOCK TIMEOUT")
                    sys.exit(1)


class CarDB:
   
    def __init__(self):
        self.db = RedisHelper(host=constants.REDIS_HOST)

    def initialize(self):
        # set staring parameters
        self.db.write(constants.REDIS_SPEED_VAR, str(constants.START_SPEED))
        self.db.write(constants.REDIS_STEER_VAR, str(constants.START_STEER))
        self.db.write(constants.REDIS_IMU_VAR, str(constants.IMU_READINGS))
        self.db.write(constants.REDIS_ENCODER_ENABLED_VAR, "false")
       
        # reset locks
        self.db.release_lock(lock=constants.REDIS_CAR_STATE_LOCK, force=True)
        self.db.release_lock(lock=constants.REDIS_ENCODER_LOCK, force=True)
 
    def set_car_speed_angle(self, speed, angle):
        # Normalize Speed 
        if speed > constants.MAX_SPEED:
            speed = constants.MAX_SPEED
        if speed < -constants.MAX_SPEED:
            speed = -constants.MAX_SPEED
        # Normalize steering angle
        if angle > constants.MAX_STEER:
            angle = constants.MAX_STEER
        if angle < -constants.MAX_STEER:
            angle = -constants.MAX_STEER
        
        # read now 
        self.db.acquire_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        self.db.write(constants.REDIS_SPEED_VAR, str(speed))
        self.db.write(constants.REDIS_STEER_VAR, str(angle))
        self.db.release_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        
    def get_car_speed_angle(self):
        # read now 
        self.db.acquire_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        speed = float(self.db.read(constants.REDIS_SPEED_VAR))
        angle = float(self.db.read(constants.REDIS_STEER_VAR))
        self.db.release_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        return speed, angle


    def set_encoder_state(self, enabled):
        msg = None
        if enabled:
            msg = "true" 
        if not enabled:
            msg = "false" 
        self.db.acquire_lock(lock=constants.REDIS_ENCODER_LOCK)
        self.db.write(constants.REDIS_ENCODER_ENABLED_VAR, msg)
        self.db.release_lock(lock=constants.REDIS_ENCODER_LOCK)
    
    def get_encoder_state(self):
        self.db.acquire_lock(lock=constants.REDIS_ENCODER_LOCK)
        enabled = self.db.read(constants.REDIS_ENCODER_ENABLED_VAR)
        self.db.release_lock(lock=constants.REDIS_ENCODER_LOCK)
        if enabled == "true":
            return True
        if enabled == "false":
            return False
    
    def set_curr_speed(self, rps):
        self.db.acquire_lock(lock=constants.REDIS_ENCODER_LOCK)
        self.db.write(constants.REDIS_ENCODER_RPS, str(rps))
        self.db.release_lock(lock=constants.REDIS_ENCODER_LOCK)

    def get_curr_speed(in_mps=False):
        self.db.acquire_lock(lock=constants.REDIS_ENCODER_LOCK)
        rps = float(self.db.read(constants.REDIS_ENCODER_RPS))
        self.db.release_lock(lock=constants.REDIS_ENCODER_LOCK)
        if in_mps:
            return (2 * math.pi * constants.WHEEL_RADIUS) * rps
        else:
            return rps
        
    def set_imu(self, roll, pitch, yaw):
        yaw = self.yaw
        roll = self.roll
        pitch = self.pitch     
        self.db.acquire_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        self.db.write(constants.REDIS_IMU_VAR, str(yaw))
        self.db.write(constants.REDIS_IMU_VAR, str(pitch))
        self.db.write(constants.REDIS_IMU_VAR, str(roll))
        self.db.release_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        
    def get_imu(self):
        self.db.acquire_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        yaw = float(self.db.read(constants.REDIS_IMU_VAR))
        pitch = float(self.db.read(constants.REDIS_IMU_VAR))
        roll = float(self.db.read(constants.REDIS_IMU_VAR))
        self.db.release_lock(lock=constants.REDIS_CAR_STATE_LOCK)
        return yaw, pitch, roll




if __name__ == "__main__":
    db = CarDB()
    import pdb; pdb.set_trace()
