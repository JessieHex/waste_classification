from picamera import PiCamera
import time
import serial
import os
import requests
import RPi.GPIO as GPIO
import sqlite3
from datetime import datetime
from gate import GateController
from led import Led_Controller
from threading import Timer
import logging
import traceback
import sys

# This class is for gate controller
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class AccessControlSystem():
    HC05 = '00:22:04:30:24:06' # the address of the bluetooth
    TOKEN= 'c8fc3b41afa2afcabd413eef3205eebcafb051b8' # Token for plate recognizer API
    PIC_PATH = r'/home/pi/car.jpg'
    DB_PATH = r'/home/pi/parking.db'
    LOG_PATH = r'/home/pi/debug.log'
    SERVO_PIN = 17
    RED_PIN = 22
    YELLOW_PIN = 23
    GREEN_PIN = 24

    def __init__(self):
        # set up pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.YELLOW_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)

        # config error logging file
        logging.basicConfig(filename=self.LOG_PATH, level=logging.DEBUG, format='%(asctime)s:%(name)s:%(message)s')
        print('connecting database')
        self.db = sqlite3.connect(self.DB_PATH)
        self.led = Led_Controller(self.RED_PIN, self.YELLOW_PIN, self.GREEN_PIN)
        self.servo = GPIO.PWM(self.SERVO_PIN, 50) # 50 HZ PMW
        self.servo.start(0)
        self.gate_controller = GateController(self.servo, self.led)
        self.timer = RepeatTimer(0.01, lambda: self.gate_controller.tick()) # time unit in gate controller in 0.01 sec
        self.timer.start()
        self.camera = PiCamera(resolution=(640, 360))
        self.camera.rotation = 180
        print('warming up camera')
        self.camera.start_preview()
        time.sleep(2)  # Camera warm-up time
        self.connect_bluetooth()

    def connect_bluetooth(self):
        print('connecting bluetooth')
        if os.path.exists('/dev/rfcomm0') == False:
            bind_bluetooth = 'sudo rfcomm bind 0 ' + self.HC05
            os.system(bind_bluetooth)
            time.sleep(1)
        self.bluetoothSerial = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=1)  # read data every 1 second

    def take_photo(self):
        self.camera.capture('car.jpg')

    # check if the licence in the database and not expired
    def enquiry(self, licence):
        licence = licence.upper()
        cur = self.db.cursor()
        cur.execute('SELECT expiry_date FROM parking WHERE licence=?', (licence,))
        rows = cur.fetchall()
        if len(rows) == 0:
            return False # licence number not in system
        else:
            expiry_date = datetime.strptime(rows[0][0], "%Y-%m-%d")
            return expiry_date >= datetime.now()

    def recognize_plate(self):
        fp = open(self.PIC_PATH, 'rb')
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            files=dict(upload=fp),
            headers={'Authorization': "Token " + self.TOKEN}, timeout=3)
        return response

    def clean(self):
        self.gate_controller.close_gate() # make sure the gate is closed when exit the program
        self.db.close()
        self.camera.stop_preview()
        self.camera.close()
        GPIO.cleanup()
