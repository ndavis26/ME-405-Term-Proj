"""! @file main_v2.py
@author Nathaniel Davis
@date 3-13-24
"""

import pyb
import gc
from motor_driver_updated import MotorDriver
from encoder_reader_updated import Encoder 
from motorwithencoder_updated import MotoEncodo
from servo import Servo
from mlx_cam import MLX_Cam
import math
import time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern



def mastermind():
    S0_INIT = 0
    S1_BUTTON = 1 
    S2_WAIT = 2
    S3_CAM = 3
    S4_MOTOR = 4
    S5_FIRE = 5
    S6_RESET = 6
    
    state = S0_INIT
    while True:
        if(state == S0_INIT): # initializes system            
            # set up servo
            servpin = pyb.Pin.board.PB6
            servtimer = 4
            servchannel = 1
            serv = Servo(servpin, servtimer, servchannel)

            # set up flywheel output
            flypin = pyb.Pin.board.PC3
            flywheel = pyb.Pin(flypin, pyb.Pin.OUT_PP)
            flywheel.low()
            
            #set up button pin
            buttonpin = pyb.Pin.board.PC13
            button = pyb.Pin(buttonpin, pyb.Pin.IN)
            
            # motor pins
            mtrAplus = pyb.Pin.board.PB4
            Aplusch = 1
            mtrAminus = pyb.Pin.board.PB5
            Aminusch = 2
            mtrEN = pyb.Pin.board.PA10
            mtrtimer = 3

            # encoder pins
            encA = pyb.Pin.board.PC6
            encAch = 1
            encB = pyb.Pin.board.PC7
            encBch = 2
            readch = 8
            
            # set up motor driver
            moe = MotorDriver(mtrEN, mtrAplus, Aplusch,  mtrAminus, Aminusch, mtrtimer)
            # set up encoder
            enc = Encoder(encA, encB, readch, encAch, encBch)
            # set up motor control
            motorctrl = MotoEncodo(moe, enc)
            motorctrl.set_Kp(0.028)
            motorctrl.set_Ki(0.0007)
            
            
            # Setting up camera - referenced from mlx_cam.py
            
            # The following import is only used to check if we have an STM32 board such
            # as a Pyboard or Nucleo; if not, use a different library
            try:
                from pyb import info
            # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
            except ImportError:
                # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
                i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
            # OK, we do have an STM32, so just use the default pin assignments for I2C1
            else:
                i2c_bus = I2C(1)
            # Select MLX90640 camera I2C address, normally 0x33, and check the bus
            i2c_address = 0x33
            scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
            # Create the camera object and set it up in default mode
            camera = MLX_Cam(i2c_bus)
            camera._camera.refresh_rate = 1.0
            
            # move to state 1
            state = S1_BUTTON
            print("waiting for button press")
            
        elif(state == S1_BUTTON): # waits for button press
            if not button.value():
                state = S2_WAIT
                
        elif(state == S2_WAIT): # waits for 5 seconds before turning and firing         
            print('waiting to duel')
            time.sleep(5)
            state = S3_CAM
                
        elif(state == S3_CAM): # takes the currently stored camera info and creates an angle
            print("checking camera")
            image = None
            while not image:
                image = camera.get_image_nonblocking()
#             camera.ascii_art(image)
            csv = []
            for line in camera.get_csv(image, limits=(0, 99)):
                csv.append(sum([eval(i) for i in line.split(',')]))
            cam_row = csv.index(max(csv))
            angle = cam_row - 12.5
            print(angle)
            print("adjusting")
            state = S4_MOTOR
            
        elif(state == S4_MOTOR): # moves motor to desired angle
            setpoint = 1600 + (angle*05)
            motorctrl.set_setpoint(setpoint)
            if abs(enc.read()-setpoint) <= 5:
                moe.set_duty_cycle(0)
                time.sleep(0.5)
                print(f'desired setpoint: {setpoint}')
                print(f'final setpoint: {enc.read()}')
                state = S5_FIRE
 
        elif(state == S5_FIRE): # fire away!
            print("firing!")
            flywheel.high()
            firing = 250
            time.sleep(1.5)
            serv.ccw()
            time.sleep_ms(firing)
            serv.stop()
            time.sleep(0.5)
            serv.cw()
            time.sleep_ms(firing)
            serv.stop()
            time.sleep(0.5)
            serv.off()
            flywheel.low()
            state = S6_RESET
            
        elif(state == S6_RESET): # resets system
            setpoint = 0
            motorctrl.set_setpoint(setpoint)
            if abs(enc.read()-setpoint) <= 5:
                moe.set_duty_cycle(0)
                time.sleep(0.5)
                print(f'desired setpoint: {setpoint}')
                print(f'final setpoint: {enc.read()}')
                print("duel finished")
                state = S1_BUTTON
                print("waiting for button press")

if __name__ == "__main__":
    mastermind()
    