import pyb
import gc
import pyb
import cotask
import task_share
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


def task2_motorcontrol(shares):
    """!
    motor controller that constantly attmepts to
    reach the setpoint set in the intertask variable "motor_setpoint."
    """
    S0_INIT = 0
    S1_UPDATE_MOTOR = 1
     
    state = S0_INIT
    while True:
        ir_angle, motor_setpoint = shares
        if(state == S0_INIT):
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
            motorctrl.set_Kp(0.3)
            motor_setpoint.put(1600)
            
            state = S1_UPDATE_MOTOR
            yield
        elif(state == S1_UPDATE_MOTOR):
            setpoint = motor_setpoint.get()
            motorctrl.set_setpoint(setpoint)
            print(f'setpoint: {setpoint}, current location: {enc.read()}')
            yield
 
if __name__ == "__main__": 
    
    # create intertask data here
    ir_angle = task_share.Share('h', thread_protect=True, name="IR Angle")
    motor_setpoint = task_share.Share('h', thread_protect=True, name="Motor Setpoint")
    
    # create tasks
#     task1 = cotask.Task(task1_mm, name="Mastermind", priority=1, period=10, profile=True, trace=False, shares=(ir_angle, motor_setpoint))
    task2 = cotask.Task(task2_motorcontrol, name="Motor Control", priority=3, period=10, profile=True, trace=False, shares=(ir_angle, motor_setpoint))
#     task3 = cotask.Task(task3_camera, name="Camera", priority=2, period=50,profile=True, trace=False, shares=(ir_angle, motor_setpoint))
#     cotask.task_list.append(task1)
    cotask.task_list.append(task2)
#     cotask.task_list.append(task3)
    
    # clean up memory
    gc.collect()
    
    # create scheduler
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    