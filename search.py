#!/usr/bin/python

import sys
import unittest

import binsearch

GRID_SIZE = 4

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


def load_from_string(letters):
    list_letters = []
    for letter in letters:
        if letter.isupper() and list_letters and list_letters[-1].isupper():
            list_letters[-1] += letter
        else:
            list_letters.append(letter)
    list_letters = [x.lower() for x in list_letters]
    return [list_letters[x*GRID_SIZE:(x+1)*GRID_SIZE] for x in range(0, GRID_SIZE)]


def load_list_from_file(path):
    return [x.strip().lower() for x in open(path).readlines()]


def find_words(grid, word_list):
    results = _find_words(grid, word_list)

    results = [{
        'word': x[0],
        'score': compute_score(x[0]),
        'snake': x[1]
    } for x in results]

    results.sort(key=lambda x: x['score'] / float(len(x['word'])), reverse=True)
    return results


def _find_words(grid, word_list):
    _validate_size(grid)

    results = []
    result_words = set()
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
                    return sorted(results)
                snake = (possible_starts.pop(),)
            continue

        assert snake

        search_str = _get_grid_chars(snake, grid)

        is_word, is_prefix = _check_word(search_str, word_list)
        if is_word and len(search_str) > 2 and not search_str in result_words:
            results.append((search_str, snake))
            result_words.add(search_str)
        if not is_prefix:
            bad_paths.add(snake)
            snake = snake[:-1]


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


class FixesTest(unittest.TestCase):
    def testWordDerived(self):
        matches = self._find('hncrtienvrdahede', ['derived'])
        self.assertEquals(matches, ['derived'])

    def testDuplicates(self):
        matches = self._find('asdfasdfasdfasdf', ['ass', 'sass'])
        self.assertEquals(matches, ['ass', 'sass'])

    def _find(self, letters, words):
        results = find_words(load_from_string(letters), words)
        return [x[0] for x in results]


if __name__ == '__main__':
    unittest.main()