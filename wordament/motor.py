#!/usr/bin/python

try:
    import RPi.GPIO as GPIO
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
    FAKE_MOTORS = False
except ImportError:
    FAKE_MOTORS = True

import threading
import time


class MotorDef(object):
    def __init__(self, pins, motor_id, ada_id, auto_reverse=False):
        self.pins = pins
        self.motor_id = motor_id
        self.auto_reverse = auto_reverse
        self.ada_id = ada_id


class MotorMovement(object):
    def __init__(self, motor_id, reverse, squares):
        self.motor_id = motor_id
        self.reverse = reverse
        self.squares = squares


class AdaMotorDriver(object):
    _STEPS_PER_SQUARE = 43
    def __init__(self, motors):
        if FAKE_MOTORS:
            return
        self._hat = Adafruit_MotorHAT()
        self._motors = {x.motor_id: x for x in motors}
        self._motor_objs = {}
        for motor in motors:
            self._motor_objs[motor.motor_id] = self._hat.getStepper(200, motor.ada_id)
            self._motor_objs[motor.motor_id].setSpeed(300)

    def __del__(self):
        if FAKE_MOTORS:
            return
        for motor in self._motors.values():
            print 'exiting for', motor.ada_id
            self._hat.getMotor(motor.ada_id).run(Adafruit_MotorHAT.RELEASE)
            time.sleep(0.01)

    def move(self, movements):
        if FAKE_MOTORS:
            return
        threads = [threading.Thread(target=self._move, args=[x]) for x in movements]
        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

    def _move(self, movement):
        motor = self._motor_objs[movement.motor_id]
        reverse = self._motors[movement.motor_id].auto_reverse != movement.reverse
        dir = Adafruit_MotorHAT.BACKWARD if reverse else Adafruit_MotorHAT.FORWARD
        steps = int(movement.squares * self._STEPS_PER_SQUARE)
        motor.step(steps, dir, Adafruit_MotorHAT.SINGLE)


class GpioMotorDriver(object):
    _SLEEP_INTERVAL = 7 / 1000.0
    _STEPS_PER_SQUARE = 11

    def __init__(self, motors):
        if FAKE_MOTORS:
            return
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self._motors = {x.motor_id: x for x in motors}
        for motor in motors:
            for pin in motor.pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, False)

    def __del__(self):
        if FAKE_MOTORS:
            return
        for motor in self._motors.values():
            for pin in motor.pins:
                GPIO.output(pin, False)

    def move(self, movements):
        if FAKE_MOTORS:
            return
        threads = [threading.Thread(target=self._move, args=[x]) for x in movements]
        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

    def _move(self, movement):
        time.sleep(self._SLEEP_INTERVAL)
        pins = self._motors[movement.motor_id].pins
        steps = int(movement.squares * self._STEPS_PER_SQUARE)
        reverse = self._motors[movement.motor_id].auto_reverse != movement.reverse
        movement_sequence = reversed(self._movement_sequence) if reverse else self._movement_sequence
        pin_vals = [zip(pins, x) for x in movement_sequence]
        for ignored in range(0, steps):
            for pin_set in pin_vals:
                for pin, val in pin_set:
                    GPIO.output(pin, val != 0)
                time.sleep(self._SLEEP_INTERVAL)

    _unipolar_movement_sequence = [
        [1, 0, 0, 1],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]

    _movement_sequence = [
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1],
    ]


def test():
    _X_MOTOR_PINS = [17, 18, 21, 22]
    _Y_MOTOR_PINS = [23, 24, 25, 27]
    x_motor = MotorDef(_X_MOTOR_PINS, 'x', 0)
    y_motor = MotorDef(_Y_MOTOR_PINS, 'y', 0)
    driver = GpioMotorDriver([x_motor, y_motor])
    driver.move([MotorMovement('y', True, 1), MotorMovement('x', True, 1)])
    driver.move([MotorMovement('y', False, 1), MotorMovement('x', False, 1)])


if __name__ == '__main__':
    test()

