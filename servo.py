#!/usr/bin/python

import sys
import time

_UP_POS = 43
_DOWN_POS = 55


class Servo(object):
    def __init__(self, pin):
        self._pin = pin
        self._is_up = False
        self.move_up()

    def move_up(self):
        if not self._is_up:
            self._write_pos(_UP_POS)
            self._is_up = True

    def move_down(self):
        if self._is_up:
            self._write_pos(_DOWN_POS)
            self._is_up = False

    def _write_pos(self, pos):
        try:
            with open('/dev/servoblaster', 'w') as output:
                command = 'P1-%i=%i%%\n' % (self._pin, pos)
                output.write(command)
        except Exception:
            pass
        else:
            time.sleep(0.15)

if __name__ == '__main__':
    servo = Servo(7)
    if sys.argv[1].lower() == 'up':
        servo.move_up()
    else:
        servo.move_down()
