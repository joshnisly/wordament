#!/usr/bin/python

import draw
import motor

def adjust():
    motors = [
        motor.MotorDef(draw._X_MOTOR_PINS, 'x', 1, True),
        motor.MotorDef(draw._Y_MOTOR_PINS, 'y', 2)
    ]
    driver = motor.GpioMotorDriver(motors)
    last = None
    STEP_SIZE = 1
    while True:
        choice = raw_input('Enter lrupq:') or last
        movements = []
        if 'l' in choice:
            movements.append(motor.MotorMovement('x', True, STEP_SIZE))
        if 'r' in choice:
            movements.append(motor.MotorMovement('x', False, STEP_SIZE))
        if 'u' in choice:
            movements.append(motor.MotorMovement('y', True, STEP_SIZE))
        if 'd' in choice:
            movements.append(motor.MotorMovement('y', False, STEP_SIZE))
        if 'x' in choice:
            driver.move([
                motor.MotorMovement('x', False, STEP_SIZE),
            ])
            driver.move([
                motor.MotorMovement('y', True, STEP_SIZE)
            ])
            driver.move([
                motor.MotorMovement('x', True, STEP_SIZE),
                motor.MotorMovement('y', False, STEP_SIZE)
            ])
        if 'q' in choice:
            return

        driver.move(movements)

        last = choice

if __name__ == '__main__':
    adjust()
