from time import sleep

# finite state machine for controlling the car parking gate

class GateController:
    # states of the gate
    CLOSED = 0
    OPENING = 1
    OPEN1 = 2
    OPEN2 = 3
    CLOSING = 4

    # constant for SERVO duty cycle
    SERVO_CLOSE = 1
    SERVO_OPEN = 5

    # constant for state lasting time
    GREEN_OPEN = 300 # turn on green led for 3 secs at the OPEN1 state
    YELLOW_OPEN = 100 # turn on yellow led for 1 secs at the OPEN2 state

    def __init__(self, servo, led_controller):
        self.state = self.CLOSED
        self.duty_cycle = self.SERVO_CLOSE
        self.timer = 0
        self.servo = servo
        self.led_controller = led_controller

    def _next(self, new_state):
        self.state = new_state
        if self.state == self.CLOSED:
            self.servo.ChangeDutyCycle(0)
            return
        elif self.state == self.OPENING:
            self.led_controller.green_on()
            return
        elif self.state == self.OPEN1:
            self.servo.ChangeDutyCycle(0)
            self.timer = self.GREEN_OPEN
            return
        elif self.state == self.OPEN2:
            self.led_controller.yellow_on()
            self.timer = self.YELLOW_OPEN
            return
        elif self.state == self.CLOSING:
            self.led_controller.red_on()
            return
        else:
            raise ValueError('unknown state')

    def signal_received(self):
        if self.state == self.CLOSED:
            self._next(self.OPENING)
            return
        elif self.state == self.OPENING:
            return
        elif self.state == self.OPEN1:
            self._next(self.OPENING)
            return
        elif self.state == self.OPEN2:
            self._next(self.OPENING)
            return
        elif self.state == self.CLOSING:
            self._next(self.OPENING)
            return
        else:
            raise ValueError('unknown state')


    def tick(self):
        if self.state == self.CLOSED:
            return
        elif self.state == self.OPENING:
            if (self.duty_cycle < self.SERVO_OPEN):
                self.duty_cycle += 0.1
                self.servo.ChangeDutyCycle(self.duty_cycle)
                sleep(0.1)
                return
            self._next(self.OPEN1)
            return
        elif self.state == self.OPEN1:
            if self.timer > 0:
                self.timer -= 1
                return
            self._next(self.OPEN2)
            return
        elif self.state == self.OPEN2:
            if self.timer > 0:
                self.timer -= 1
                return
            self._next(self.CLOSING)
        elif self.state == self.CLOSING:
            if (self.duty_cycle > self.SERVO_CLOSE):
                self.duty_cycle -= 0.1
                self.servo.ChangeDutyCycle(self.duty_cycle)
                sleep(0.1)
                return
            self._next(self.CLOSED)
            return
        else:
            raise ValueError('unknown state')

    def close_gate(self):
        self._next(self.CLOSING)




