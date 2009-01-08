#!/usr/bin/python

import unittest

from Plex import Regexps


class REUtils(unittest.TestCase):
    def test_c2r(self):
        print Regexps.chars_to_ranges(list('abcdefg'))


if __name__ == '__main__':
    unittest.main()

