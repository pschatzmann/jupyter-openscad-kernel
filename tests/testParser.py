###
# Unit Tests for the SCAD Kernel/Parser
#

import unittest
import os, re
from iopenscad.parser import Parser
from iopenscad.kernel import IOpenSCAD

class MyTestParser(unittest.TestCase):
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
        self.assertEqual(len(self.strip(parser.getSourceCode())), 2192)
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

    def testMultipleComment(self):
        parser = Parser()
        cmd = "// test"+os.linesep
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("comment")), 1)
        cmd = "// test"+os.linesep
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("comment")), 1)
        cmd = "// test"
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("comment")), 1)

    def testMultipleStatement(self):
        parser = Parser()
        cmd = "test();"+os.linesep
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("-")), 1)
        cmd = "test();"+os.linesep
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("-")), 1)
        cmd = "test();"
        parser.parse(cmd)
        self.assertEqual(len(parser.getStatementsOfType("-")), 1)

    def testEquals(self):
        p = Parser()
        str = "a=1;"+os.linesep+"b=2;"+os.linesep
        p.parse(str)
        stmts = p.getStatements()
        self.assertEqual(len(stmts), 2)
        self.assertEqual(stmts[0].sourceCode, "a=1;"+os.linesep)
        self.assertEqual(stmts[1].sourceCode, "b=2;"+os.linesep)
        

if __name__ == '__main__': 
    unittest.main() 

