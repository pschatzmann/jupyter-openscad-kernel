###
# Unit Tests for the SCAD Kernel/Parser
#

import unittest
import os, re
from iopenscad.parser import Parser
from iopenscad.scanner import Scanner
from iopenscad.kernel import IOpenSCAD

class MyTest(unittest.TestCase):
    def strip(self, txt):
        return txt.replace(os.linesep,"").strip()

    def testConvert(self):
        cmd = os.linesep+" box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.setup()
        parser.parse(cmd)
        mime = parser.renderMime()
        f = open(mime, "rb")
        content = f.read()
        print(content)
        f.close()

    def testEmptyConvert(self):
        parser = Parser()
        parser.setup()
        mime = parser.renderMime()
        self.assertEqual(mime, None)

    def testLsMagic(self):
        cmd = os.linesep+" %lsmagic "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        self.assertEqual(parser.getSourceCode().strip(), "")
        self.assertTrue(parser.getMessages().startswith("Available Commands: "))

    def testCommand(self):
        cmd = os.linesep+" %command testCommand "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        self.assertEqual(parser.getSourceCode().strip(), "")
        self.assertEqual(parser.scadCommand, "testCommand")

    def testMime(self):
        cmd = os.linesep+" %mime application/openscad "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        self.assertEqual(parser.getSourceCode().strip(), "")
        self.assertEqual(parser.mime, "application/openscad")


    def testDisplay(self):
        cmd = os.linesep+" %display box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        resultPermanent = "".join([elem.sourceCode for elem in parser.getStatements()]) 
        self.assertEqual(resultPermanent.strip(), "")
        self.assertEqual(self.strip(parser.getSourceCode()), "box([1,1,1]);")


    def testDisplay2(self):
        cmd = os.linesep+"%%display "+os.linesep+"box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        resultPermanent = "".join([elem.sourceCode for elem in parser.getStatements()]) 
        self.assertEqual(resultPermanent.strip(), "")
        self.assertEqual(self.strip(parser.getSourceCode()), "box([1,1,1]);")

    def testDisplayCode(self):
        cmd = "cube([20,30,50]);"+os.linesep+"%displayCode "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        self.assertTrue(parser.getMessages().startswith("cube([20,30,50])"))

    def testSourceCode(self):
        cmd = os.linesep+" box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        resultPermanent = "".join([elem.sourceCode for elem in parser.getStatements()]) 
        self.assertEqual(self.strip(resultPermanent), "box([1,1,1]);")
        self.assertEqual(self.strip(parser.getSourceCode()), "box([1,1,1]);")

    def testModules(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep
        parser = Parser()
        parser.parse(cmd)
        result = parser.getStatementsOfType("module")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test")
        self.assertEqual(self.strip(result[0].sourceCode), "module test(){ box([1,1,1]);}")

    def testModulesUpdate(self):
        parser = Parser()
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep
        parser.parse(cmd)
        cmd = os.linesep+"module test(){ box([2,2,2]);} "+os.linesep
        parser.parse(cmd)
        result = parser.getStatementsOfType("module")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test")
        self.assertEqual(self.strip(result[0].sourceCode), "module test(){ box([2,2,2]);}")
        self.assertTrue(parser.getMessagesExt().startswith("Number of lines"))

    def testClose(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);}"+os.linesep+"%display test();"
        parser = Parser()
        parser.parse(cmd)
        self.assertEqual(self.strip(parser.getSourceCode()), "module test(){ box([1,1,1]);} test();")
        parser.close()
        self.assertEqual(parser.getSourceCode().strip(), "")
        self.assertEqual(parser.getMessages().strip(), "")

    def testClear(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep+"%display test();"
        parser = Parser()
        parser.parse(cmd)
        self.assertTrue(self.strip(parser.getSourceCode()))
        parser.parse("%clear")
        self.assertEqual(self.strip(parser.getSourceCode()), "")
        self.assertTrue("cleared" in parser.getMessages().strip())

    def testInclude(self):
        cmd = "%include https://raw.githubusercontent.com/pschatzmann/openscad-models/master/Pig.scad" 
        parser = Parser()
        parser.parse(cmd)
        self.assertEqual(len(self.strip(parser.getSourceCode())), 2185)
        self.assertTrue("Included" in parser.getMessages().strip())

    def testUse(self):
        cmd = "%use https://raw.githubusercontent.com/pschatzmann/openscad-models/master/Pig.scad" 
        parser = Parser()
        parser.parse(cmd)
        self.assertTrue("Included" in parser.getMessages().strip())

    def testDisplayText(self):
        cmd = "%mime text/plain"+os.linesep+" %display box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.setup()
        parser.parse(cmd)
        result = parser.renderMime()
        self.assertNotEqual(result, None)

    def testComment(self):
        cmd = "box([1,1,1]);"+os.linesep+" /* comment */ box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.setup()
        parser.parse(cmd)
        result = parser.getStatementsOfType("comment")
        self.assertEqual(len(result), 1)

    def testEndChar(self):
        s = Scanner()
        self.assertEqual(s.findEndWithNewLine(s.scann("a"),1), 1)
        self.assertEqual(s.findEndWithNewLine(s.scann("a"+os.linesep+"b"),1), 1)
        self.assertEqual(s.findEndWithNewLine(s.scann("a"+os.linesep+os.linesep+"b"),1), 3)


if __name__ == '__main__': 
    unittest.main() 

