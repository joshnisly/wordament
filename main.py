#!/usr/bin/python

import argparse
import sys
import unittest

import search


def load_grid_from_input():
    '''
    returns a two-dimensional 5x5 grid
    '''
    letters = raw_input('Enter grid in one dimension (%i chars)' % search.GRID_SIZE**2)
    letters = letters.lower()
    return load_from_string(letters)


def load_from_string(letters):
    return [letters[x*search.GRID_SIZE:(x+1)*search.GRID_SIZE] for x in range(0, search.GRID_SIZE)]


def load_list_from_file(path):
    return [x.strip().lower() for x in open(path).readlines()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--word-list', action='store')
    parser.add_argument('-g', '--grid', action='store')
    args = parser.parse_args()

    if args.grid:
        grid = load_list_from_file(args.grid)
    else:
        grid = load_grid_from_input()

    word_list = sorted(load_list_from_file(args.word_list))

    print grid
    print '\n'.join(grid)

    print len(word_list)

    results = search.find_words(grid, word_list)
    results.sort(key=lambda x: len(x))
    print '\n'.join(results)

    print len(results)


class FixesTest(unittest.TestCase):
    def testDerived(self):
        matches = self._find('hncrtienvrdahede', ['derived'])
        self.assertEquals(matches, ['derived'])

    def _find(self, letters, words):
        return [x[0] for x in search.find_words(load_from_string(letters), words)]


if __name__ == '__main__':
    if sys.argv[1] == '--unittest':
        del sys.argv[1]
        unittest.main()
    else:
        main()
