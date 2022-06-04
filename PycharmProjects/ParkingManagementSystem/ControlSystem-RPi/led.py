import RPi.GPIO as GPIO
from time import sleep

class Led_Controller():
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green

    def red_on(self):
        self.all_off()
        GPIO.output(self.red, GPIO.HIGH)

    def green_on(self):
        self.all_off()
        GPIO.output(self.green, GPIO.HIGH)

    def yellow_on(self):
        self.all_off()
        GPIO.output(self.yellow, GPIO.HIGH)

    def all_off(self):
        GPIO.output(self.red, GPIO.LOW)
        GPIO.output(self.yellow, GPIO.LOW)
        GPIO.output(self.green, GPIO.LOW)

