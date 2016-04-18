#!/usr/bin/python

import argparse
import sys
import threading
import time
import unittest

import camera
import draw
import driver_thread
import search
import vision.grid

LETTERS = 'abcdefghijklmnopqrstuvwxyz'
SCORES = [2, 5, 3, 3, 1, 5, 4, 4, 2, 10, 6, 3, 4, 2, 2, 4, 2, 2, 2, 2, 4, 6, 6, 9, 5, 8]
LETTER_SCORES = dict(zip(LETTERS, SCORES))


def compute_score(word):
    total = sum([LETTER_SCORES[x] for x in word])
    if len(word) >= 8:
        return int(total * 2.5)
    if len(word) >= 6:
        return int(total * 2)
    if len(word) >= 5:
        return int(total * 1.5)
    return total


def load_grid_from_input():
    '''
    returns a two-dimensional 4x4 grid
    '''
    letters = raw_input('Enter grid in one dimension (%i chars)' % search.GRID_SIZE**2)
    letters = letters.lower()
    return search.load_from_string(letters)


class _LockedItem(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._item = None

    def set(self, item):
        self._lock.acquire()
        try:
            self._item = item
        finally:
            self._lock.release()

    def get(self):
        while True:
            item = self._try_get()
            if item is not None:
                return item

            time.sleep(0.01)

    def _try_get(self):
        self._lock.acquire()
        item = None
        try:
            item = self._item
        finally:
            self._lock.release()
        return item


class _DisplayThread(threading.Thread):
    def __init__(self, image_src, image_data_src):
        super(_DisplayThread, self).__init__()
        self._image_src = image_src
        self._image_data_src = image_data_src
        self.daemon = True

    def run(self):
        import cv2
        while True:
            image_data = self._image_data_src.get()
            image = self._image_src.get()
            image = vision.grid.warp_image_to_squares(image, image_data['orig_squares'])
            image = vision.grid.draw_squares(image, image_data['warped_squares'])
            image = vision.grid.draw_letters_at_squares(image, image_data['text'], image_data['warped_squares'])
            cv2.imshow('result', image)
            cv2.waitKey(100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--word-list', action='store')
    parser.add_argument('-g', '--grid', action='store')
    parser.add_argument('-c', '--camera', action='store_true')
    parser.add_argument('-s', '--standalone', action='store_true')
    args = parser.parse_args()

    word_list = sorted(search.load_list_from_file(args.word_list))

    if args.standalone:
        if args.grid:
            grid = search.load_list_from_file(args.grid)
        else:
            grid = load_grid_from_input()

        results = search.find_words(grid, word_list)
        results = [{
            'word': x[0],
            'score': compute_score(x[0]),
            'snake': x[1]
        } for x in results]
        results.sort(key=lambda x: x['score'] / float(len(x['word'])), reverse=True)

        draw.draw_results(results)
    else:
        image_data_obj = _LockedItem()
        image_obj = _LockedItem()
        camera_thread = camera.CameraThread(image_obj, args.camera)
        camera_thread.start()
        start_signal = threading.Event()
        break_signal = threading.Event()
        main_thread = driver_thread.DriverThread(image_obj, image_data_obj, word_list, start_signal, break_signal)
        main_thread.start()
        start_signal.set()

        display_thread = _DisplayThread(image_obj, image_data_obj)
        display_thread.start()

        try:
            while True:
                main_thread.join(100)
        except:
            break_signal.set()
            return


class FixesTest(unittest.TestCase):
    def testDerived(self):
        matches = self._find('hncrtienvrdahede', ['derived'])
        self.assertEquals(matches, ['derived'])

    def _find(self, letters, words):
        return [x[0] for x in search.find_words(search.load_from_string(letters), words)]

if __name__ == '__main__':
    if sys.argv[1] == '--unittest':
        del sys.argv[1]
        unittest.main()
    else:
        main()
