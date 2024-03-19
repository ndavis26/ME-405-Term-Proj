import pyb
import gc
import pyb
import cotask
import task_share
from motor_driver_updated import MotorDriver
from encoder_reader_updated import Encoder 
from motorwithencoder_updated import MotoEncodo
from servo import Servo
import time

# set up servo
servpin = pyb.Pin.board.PB6
servtimer = 4
servchannel = 1
serv = Servo(servpin, servtimer, servchannel)

# set up flywheel output
flypin = pyb.Pin.board.PC3
flywheel = pyb.Pin(flypin, pyb.Pin.OUT_PP)

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


