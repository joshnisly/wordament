#!/usr/bin/python

import RPi.GPIO as GPIO
import threading
import time

_STEPS_PER_SQUARE = 40
_SLEEP_INTERVAL = 4 / 1000.0


class MotorDef(object):
    def __init__(self, pins, motor_id):
        self.pins = pins
        self.motor_id = motor_id


class MotorMovement(object):
    def __init__(self, motor_id, reverse, squares):
        self.motor_id = motor_id
        self.reverse = reverse
        self.squares = squares


class MotorDriver(object):
    def __init__(self, motors):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self._motors = {x.motor_id: x for x in motors}
        for motor in motors:
            for pin in motor.pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, False)

    def __del__(self):
        for motor in self._motors.values():
            for pin in motor.pins:
                GPIO.output(pin, False)

    def move(self, movements):
        threads = [threading.Thread(target=self._move, args=[x]) for x in movements]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def _move(self, movement):
        time.sleep(_SLEEP_INTERVAL)
        pins = self._motors[movement.motor_id].pins
        steps = movement.squares * _STEPS_PER_SQUARE
        movement_sequence = reversed(self._movement_sequence) if movement.reverse else self._movement_sequence
        pin_vals = [zip(pins, x) for x in movement_sequence]
        for ignored in range(0, steps):
            for pin_set in pin_vals:
                for pin, val in pin_set:
                    GPIO.output(pin, val != 0)
                time.sleep(_SLEEP_INTERVAL)

    _movement_sequence = [
        [1, 0, 0, 1],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]


def test():
    x_motor = MotorDef([17, 18, 21, 22], 'x')
    driver = MotorDriver([x_motor])
    driver.move([MotorMovement('x', False, 1)])
    driver.move([MotorMovement('x', True, 1)])


if __name__ == '__main__':
    test()

