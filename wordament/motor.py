#!/usr/bin/python

try:
    import RPi.GPIO as GPIO
    FAKE_MOTORS = False
except ImportError:
    FAKE_MOTORS = True

import threading
import time

_STEPS_PER_SQUARE = 192
_SLEEP_INTERVAL = 2 / 1000.0


class MotorDef(object):
    def __init__(self, pins, motor_id, auto_reverse=False):
        self.pins = pins
        self.motor_id = motor_id
        self.auto_reverse = auto_reverse


class MotorMovement(object):
    def __init__(self, motor_id, reverse, squares):
        self.motor_id = motor_id
        self.reverse = reverse
        self.squares = squares


class MotorDriver(object):
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
            time.sleep(1)
            return
        threads = [threading.Thread(target=self._move, args=[x]) for x in movements]
        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

    def _move(self, movement):
        time.sleep(_SLEEP_INTERVAL)
        pins = self._motors[movement.motor_id].pins
        steps = int(movement.squares * _STEPS_PER_SQUARE)
        reverse = self._motors[movement.motor_id].auto_reverse != movement.reverse
        movement_sequence = reversed(self._movement_sequence) if reverse else self._movement_sequence
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
    _X_MOTOR_PINS = [17, 18, 21, 22]
    _Y_MOTOR_PINS = [23, 24, 25, 27]
    x_motor = MotorDef(_X_MOTOR_PINS, 'x')
    y_motor = MotorDef(_Y_MOTOR_PINS, 'y')
    driver = MotorDriver([x_motor, y_motor])
    driver.move([MotorMovement('y', True, 4), MotorMovement('x', True, 4)])
    driver.move([MotorMovement('y', False, 4), MotorMovement('x', False, 4)])


if __name__ == '__main__':
    test()

