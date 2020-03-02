

import unittest
import os, re
from iopenscad.scanner import Scanner

class MyTestScanner(unittest.TestCase):

    def testEndChar(self):
        s = Scanner()
        str = s.scann("a"+os.linesep)
        end = s.findEndWithNewLine(str,1)
        self.assertEqual(end, len(str))

        str = s.scann("a"+os.linesep+"b")
        end = s.findEndWithNewLine(str,1)
        self.assertEqual(str[end], "b")

        str = s.scann("a"+os.linesep+os.linesep+"b")
        end = s.findEndWithNewLine(str,1)
        self.assertEqual(str[end], "b")


if __name__ == '__main__': 
    unittest.main()