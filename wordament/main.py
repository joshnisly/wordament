#!/usr/bin/python

import argparse
import sys
import unittest

import binsearch

GRID_SIZE = 4


def load_grid_from_input():
    '''
    returns a two-dimensional 5x5 grid
    '''
    letters = raw_input('Enter grid in one dimension (%i chars)' % GRID_SIZE**2)
    letters = letters.lower()
    return [letters[x*GRID_SIZE:(x+1)*GRID_SIZE] for x in range(0, GRID_SIZE)]


def load_list_from_file(path):
    return [x.strip().lower() for x in open(path).readlines()]


def _validate_size(grid):
    assert len(grid) == GRID_SIZE
    for row in grid:
        assert len(row) == GRID_SIZE


def _get_grid_chars(snake, grid):
    return ''.join([grid[x[0]][x[1]] for x in snake])


def _check_word(search_word, list):
    ''' Returns (is_found, is_prefix) '''
    pos = binsearch.binsearch(search_word, list)
    if pos == -1 or pos >= len(list):
        return False, False
    if list[pos] == search_word:
        return True, pos < len(list) - 1 and list[pos+1].startswith(search_word)
    elif list[pos].startswith(search_word):
        return False, True

    return False, False


def _get_random_move(snake, bad_snakes):
    cur_pos = snake[-1]
    possibilities = []
    if cur_pos[0] > 0:
        possibilities.append((cur_pos[0] - 1, cur_pos[1]))  # North

        if cur_pos[1] > 0:
            possibilities.append((cur_pos[0] - 1, cur_pos[1] - 1))  # Northwest

    if cur_pos[0] < GRID_SIZE-1:
        possibilities.append((cur_pos[0] + 1, cur_pos[1]))  # East

        if cur_pos[1] < GRID_SIZE-1:
            possibilities.append((cur_pos[0] + 1, cur_pos[1] + 1))  # Southeast

    if cur_pos[1] > 0:
        possibilities.append((cur_pos[0], cur_pos[1] - 1))  # West

        if cur_pos[0] < GRID_SIZE-1:
            possibilities.append((cur_pos[0] + 1, cur_pos[1] - 1))  # Southwest

    if cur_pos[1] < GRID_SIZE-1:
        possibilities.append((cur_pos[0], cur_pos[1] + 1))

        if cur_pos[0] > 0:
            possibilities.append((cur_pos[0] - 1, cur_pos[1] + 1))  # Northeast
    # Don't allow the snake to eat itself
    possibilities = filter(lambda x: not x in snake, possibilities)

    # Don't go down any bad paths
    possibilities = filter(lambda x: snake + (x,) not in bad_snakes, possibilities)
    return snake + (possibilities[0],)


def _adjust_start(starts, grid):
    bad_paths = tuple((starts[-1], x) for x in starts[:-1])
    dummy_snake = _get_random_move((starts[-1],), bad_paths)
    assert len(dummy_snake) == 2
    new_start = dummy_snake[-1]
    return new_start,


def _get_all_grid_points():
    points = []
    for x in range(0, GRID_SIZE):
        for y in range(0, GRID_SIZE):
            points.append((x, y))
    return points


def find_words(grid, word_list):
    print grid
    results = set()
    possible_starts = _get_all_grid_points()
    snake = (possible_starts.pop(),)
    bad_paths = set()
    while True:
        try:
            snake = _get_random_move(snake, bad_paths)
        except IndexError:
            bad_paths.add(snake)
            while snake and snake in bad_paths:
                snake = tuple(snake[:-1])

            if not snake:
                if not possible_starts:
                    return list(results)
                snake = (possible_starts.pop(),)
            continue

        assert snake

        search_str = _get_grid_chars(snake, grid)

        is_word, is_prefix = _check_word(search_str, word_list)
        if is_word and len(search_str) > 2:
            results.add(search_str)
        if not is_prefix:
            bad_paths.add(snake)
            snake = snake[:-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--word-list', action='store')
    parser.add_argument('-g', '--grid', action='store')
    args = parser.parse_args()

    if args.grid:
        grid = load_list_from_file(args.grid)
    else:
        grid = load_grid_from_input()
    _validate_size(grid)

    word_list = sorted(load_list_from_file(args.word_list))

    print grid
    print '\n'.join(grid)

    print len(word_list)

    results = find_words(grid, word_list)
    results.sort(key=lambda x: len(x))
    print '\n'.join(results)

    print len(results)


class FixesTest(unittest.TestCase):
    def testDerived(self):
        matches = self._find('hncrtienvrdahede', ['derived'])
        self.assertEquals(matches, ['derived'])

    def _find(self, letters, words):
        return find_words([letters[x*GRID_SIZE:(x+1)*GRID_SIZE] for x in range(0, GRID_SIZE)], words)


if __name__ == '__main__':
    if sys.argv[1] == '--unittest':
        del sys.argv[1]
        unittest.main()
    else:
        main()
