#!/usr/bin/python

import draw
import motor

def adjust():
    motors = [
        motor.MotorDef(draw._X_MOTOR_PINS, 'x'),
        motor.MotorDef(draw._Y_MOTOR_PINS, 'y', True)
    ]
    driver = motor.MotorDriver(motors)
    last = None
    while True:
        choice = raw_input('Enter lrupq:') or last
        if choice == 'l':
            driver.move([motor.MotorMovement('x', True, 0.25)])
        elif choice == 'r':
            driver.move([motor.MotorMovement('x', False, 0.25)])
        elif choice == 'u':
            driver.move([motor.MotorMovement('y', True, 0.25)])
        elif choice == 'd':
            driver.move([motor.MotorMovement('y', False, 0.25)])
        elif choice == 'q':
            return

        last = choice

if __name__ == '__main__':
    adjust()
