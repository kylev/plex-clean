#!/usr/bin/python

import cStringIO
import unittest

from Plex import *


class REUtils(unittest.TestCase):
    """Utility functions in the Regexp world."""
    def test_c2r(self):
        self.assertEqual([97, 104],
                         Regexps.chars_to_ranges('abcdefg'))

    def test_c2r_rev(self):
        self.assertEqual([97, 104],
                         Regexps.chars_to_ranges('gfedcba'))


class QuotedString(unittest.TestCase):
    def setUp(self):
        self.lex = Lexicon(
            [(Str("'") + Rep(AnyBut("'")) + Str("'"), TEXT),
             ])

    def tearDown(self):
        self.lex = None

    def test_basic(self):
        """Basic in-out of single-quoted text"""
        in_text = "'this is quoted text'"
        s = Scanner(self.lex, cStringIO.StringIO(in_text))

        value, text = s.read()
        self.assertEqual(in_text, text)

        value, text = s.read()
        self.assertTrue(value is None)

    def test_multiline(self):
        """Allow multiline single-quoted"""
        in_text = "'this is\nmultiline quoted text'"
        s = Scanner(self.lex, cStringIO.StringIO(in_text))

        value, text = s.read()
        self.assertEqual(in_text, text)

        value, text = s.read()
        self.assertTrue(value is None)


if __name__ == '__main__':
    unittest.main()

