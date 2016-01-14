#!/usr/bin/python

import unittest

import motor
import servo


_X_MOTOR_PINS = [17, 18, 21, 22]
_Y_MOTOR_PINS = [23, 24, 25, 27]
_SERVO_PIN = 7


def draw_results(results):
    motors = [
        motor.MotorDef(_X_MOTOR_PINS, 'y'),
        motor.MotorDef(_Y_MOTOR_PINS, 'x', True)
    ]
    driver = motor.MotorDriver(motors)
    touch_servo = servo.Servo(_SERVO_PIN)
    touch_servo.move_up()

    # Assume that we're starting at 0x0
    cur_pos = [0, 0]
    def _draw_word(word):
        print word
        for letter in word[1]:
            _move_to_pos(letter, cur_pos, driver)
            touch_servo.move_down()
        touch_servo.move_up()
        results.remove(word)

    try:
        while True:
            result = results[0]

            interim_word = _find_interim_word(cur_pos, result[1][0], results[1:])
            if interim_word:
                _draw_word(interim_word)

            _draw_word(result)

    finally:
        touch_servo.move_up()
        _move_to_pos([0, 0], cur_pos, driver)


def _find_interim_word(cur_pos, target_pos, words):
    print 'interim:', cur_pos, target_pos
    def _calc_dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    base_dist = _calc_dist(cur_pos, target_pos)

    for word in words:
        if base_dist > _calc_dist(cur_pos, word[1][0]) + _calc_dist(word[1][-1], target_pos):
            print 'interim:', word
            return word

    return None


def _move_to_pos(letter, cur_pos, driver):
    print 'Moving from %s -> %s...' % (cur_pos, letter)

    movements = []
    # Calculate x-axis movement
    _add_movement(cur_pos[0], letter[0], 'x', movements)
    _add_movement(cur_pos[1], letter[1], 'y', movements)

    cur_pos[:] = letter[:]
    driver.move(movements)


def _add_movement(old, new, motor_id, movements):
    if old != new:
        movements.append(motor.MotorMovement(motor_id, old > new, abs(old-new)))

class InterimWordTest(unittest.TestCase):
    def testDerived(self):
        words = [
            ('first', [(3, 3), (4, 3), (4, 4)]),
            ('second', [(1, 1), (4, 3), (4, 4), (2, 2)]),
            ('third', [(3, 3), (4, 3), (4, 4)]),
        ]
        interim = _find_interim_word([0, 0], words[0][1][0], words[1:])
        self.assertEquals(interim[0], 'second')
        interim = _find_interim_word([0, 0], words[1][1][0], words[2:])
        self.assertEquals(interim, None)


if __name__ == '__main__':
    unittest.main()

