#!/usr/bin/python

import motor


_X_MOTOR_PINS = [17, 18, 21, 22]
_Y_MOTOR_PINS = [23, 24, 25, 27]


def draw_results(results):
    motors = [
        motor.MotorDef(_X_MOTOR_PINS, 'y'),
        motor.MotorDef(_Y_MOTOR_PINS, 'x', True)
    ]
    driver = motor.MotorDriver(motors)

    # Assume that we're starting at 0x0
    cur_pos = [0, 0]
    try:
        for result in results:
                result = results[0]
                print result
                for letter in result[1]:
                    _move_to_pos(letter, cur_pos, driver)
    finally:
        _move_to_pos([0, 0], cur_pos, driver)


def _move_to_pos(letter, cur_pos, driver):
    print 'Moving from %s -> %s...' % (cur_pos, letter)

    movements = []
    # Calculate x-axis movement
    _add_movement(cur_pos[0], letter[0], 'x', movements)
    _add_movement(cur_pos[1], letter[1], 'y', movements)

    driver.move(movements)
    cur_pos[:] = letter[:]


def _add_movement(old, new, motor_id, movements):
    if old != new:
        movements.append(motor.MotorMovement(motor_id, old > new, abs(old-new)))
