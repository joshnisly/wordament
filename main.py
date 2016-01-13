#!/usr/bin/python

import argparse
import sys
import unittest

import draw
import search


def load_grid_from_input():
    '''
    returns a two-dimensional 5x5 grid
    '''
    letters = raw_input('Enter grid in one dimension (%i chars)' % search.GRID_SIZE**2)
    letters = letters.lower()
    return search.load_from_string(letters)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--word-list', action='store')
    parser.add_argument('-g', '--grid', action='store')
    args = parser.parse_args()

    if args.grid:
        grid = search.load_list_from_file(args.grid)
    else:
        #grid = search.load_from_string('eerddnawsecloile')
        grid = search.load_grid_from_input()

    word_list = sorted(search.load_list_from_file(args.word_list))

    print grid
    print '\n'.join(grid)

    print len(word_list)

    results = search.find_words(grid, word_list)
    results.sort(key=lambda x: len(x[0]), reverse=True)
    print '\n'.join([x[0] for x in results])
    return

    print len(results)

    draw.draw_results(results)


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

