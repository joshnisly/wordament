#!/usr/bin/python

import bisect
import unittest


def binsearch(search_word, sorted_list):
    ''' Returns index of match. '''
    return bisect.bisect_left(sorted_list, search_word)


class BinsearchTest(unittest.TestCase):
    def testSimple(self):
        options = ['b', 'bb', 'bc', 'cd']
        for index, option in enumerate(options):
            self.assertEquals(binsearch(options[index], options), index)
        self.assertEquals(binsearch('bbb', options), 2)
        self.assertEquals(binsearch('d', options), 4)
        self.assertEquals(binsearch('a', options), 0)
        self.assertEquals(binsearch('a', []), 0)

    def testHugeList(self):
        options = [x.strip() for x in open('wordlist.txt').readlines()]
        for index, option in enumerate(options):
            self.assertEquals(binsearch(options[index], options), index)
        for index, option in enumerate(options):
            encountered = binsearch(options[index] + 'a', options)
            self.assertEquals(encountered, index + 1)


if __name__ == '__main__':
    unittest.main()
