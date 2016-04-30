#!/usr/bin/python

import threading

import draw
import search
import vision.grid


class DriverThread(threading.Thread):
    def __init__(self, image_retriever, image_data_sink, word_list, start_signal, break_signal):
        super(DriverThread, self).__init__()
        self._image_retriever = image_retriever
        self._image_data_sink = image_data_sink
        self._word_list = word_list
        self._start_signal = start_signal
        self._break_signal = break_signal
        self._orig_squares = None
        self._warped_squares = None
        self._text = None
        self.daemon = True

    def run(self):
        while True:
            # See if we should start
            self._image_data_sink.set(None)

            self._start_signal.wait()

            self._read_board()

            self._image_data_sink.set({
                'orig_squares': self._orig_squares,
                'warped_squares': self._warped_squares,
                'text': self._text
            })

            if self._break_signal.isSet():
                continue

            # Find words
            grid = search.load_from_string(self._text)
            results = search.find_words(grid, self._word_list)

            # Draw words
            draw.draw_results(results, self._break_signal)

    def _read_board(self):
        while True:
            if self._break_signal.isSet():
                return

            image = self._image_retriever.get()
            if image is None:
                continue

            result = vision.grid.find_grid_squares(image)
            if not result:
                continue
            self._orig_squares = result['square_rows']

            warped_image = vision.grid.warp_image_to_squares(image, self._orig_squares)

            warped_grid_squares = vision.grid.find_grid_squares(warped_image)
            if not warped_grid_squares:
                continue

            self._warped_squares = warped_grid_squares['square_rows']

            self._text = vision.grid.squares_to_text(warped_image, self._warped_squares)
            if len(self._text) != search.GRID_SIZE**2:
                continue

            return



