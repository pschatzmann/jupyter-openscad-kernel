

import unittest
import os, re
from iopenscad.scanner import Scanner

class MyTestScanner(unittest.TestCase):

    def testEndChar(self):
        s = Scanner()
        self.assertEqual(s.findEndWithNewLine(s.scann("a"),1), 1)
        self.assertEqual(s.findEndWithNewLine(s.scann("a"+os.linesep+"b"),1), 1)
        self.assertEqual(s.findEndWithNewLine(s.scann("a"+os.linesep+os.linesep+"b"),1), 3)


if __name__ == '__main__': 
    unittest.main()