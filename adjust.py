#!/usr/bin/python

import draw
import motor

def adjust():
    motors = [
        motor.MotorDef(draw._X_MOTOR_PINS, 'x', 1, True),
        motor.MotorDef(draw._Y_MOTOR_PINS, 'y', 2)
    ]
    driver = motor.AdaMotorDriver(motors)
    last = None
    STEP_SIZE = 1
    while True:
        choice = raw_input('Enter lrupq:') or last
        if choice == 'l':
            driver.move([motor.MotorMovement('x', True, STEP_SIZE)])
        elif choice == 'r':
            driver.move([motor.MotorMovement('x', False, STEP_SIZE)])
        elif choice == 'u':
            driver.move([motor.MotorMovement('y', True, STEP_SIZE)])
        elif choice == 'd':
            driver.move([motor.MotorMovement('y', False, STEP_SIZE)])
        elif choice == 'q':
            return

        last = choice

if __name__ == '__main__':
    adjust()
