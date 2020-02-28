###
# Unit Tests for the SCAD Kernel/Parser
#

import unittest
import os
from iopenscad.parser import Parser

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
        parser1 = Parser()
        parser1.parse(cmd)
        self.assertEqual(parser1.getSourceCode().strip(), "")
        self.assertEqual(self.strip(parser1.getMessages()), "Available Commands: %clear %display %displayCode %%display %mime %command %lsmagic %include %saveAs")

    def testCommand(self):
        cmd = os.linesep+" %command testCommand "+os.linesep
        parser2 = Parser()
        parser2.parse(cmd)
        self.assertEqual(parser2.getSourceCode().strip(), "")
        self.assertEqual(parser2.scadCommand, "testCommand")

    def testMime(self):
        cmd = os.linesep+" %mime application/openscad "+os.linesep
        parser3 = Parser()
        parser3.parse(cmd)
        self.assertEqual(parser3.getSourceCode().strip(), "")
        self.assertEqual(parser3.mime, "application/openscad")


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


    def testSourceCode(self):
        cmd = os.linesep+" box([1,1,1]); "+os.linesep
        parser5 = Parser()
        parser5.parse(cmd)
        resultPermanent = "".join([elem.sourceCode for elem in parser5.getStatements()]) 
        self.assertEqual(self.strip(resultPermanent), "box([1,1,1]);")
        self.assertEqual(self.strip(parser5.getSourceCode()), "box([1,1,1]);")

    def testModules(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep
        parser6 = Parser()
        parser6.parse(cmd)
        result = parser6.getStatementsOfType("module")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test")
        self.assertEqual(self.strip(result[0].sourceCode), "module test(){ box([1,1,1]);}")

    def testModulesUpdate(self):
        parser7 = Parser()
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep
        parser7.parse(cmd)
        cmd = os.linesep+"module test(){ box([2,2,2]);} "+os.linesep
        parser7.parse(cmd)
        result = parser7.getStatementsOfType("module")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "test")
        self.assertEqual(self.strip(result[0].sourceCode), "module test(){ box([2,2,2]);}")

    def testClose(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);}"+os.linesep+"%display test();"
        parser8 = Parser()
        parser8.parse(cmd)
        self.assertEqual(self.strip(parser8.getSourceCode()), "module test(){ box([1,1,1]);} test();")
        parser8.close()
        self.assertEqual(parser8.getSourceCode().strip(), "")
        self.assertEqual(parser8.getMessages().strip(), "")

    def testClear(self):
        cmd = os.linesep+"module test(){ box([1,1,1]);} "+os.linesep+"%display test();"
        parser9 = Parser()
        parser9.parse(cmd)
        self.assertEqual(self.strip(parser9.getSourceCode()), "module test(){ box([1,1,1]);}  test();")
        parser9.parse("%clear")
        self.assertEqual(self.strip(parser9.getSourceCode()), "")
        self.assertTrue("cleared" in parser9.getMessages().strip())

    def testInclude(self):
        cmd = "%include https://raw.githubusercontent.com/pschatzmann/openscad-models/master/Pig.scad" 
        parser9 = Parser()
        parser9.parse(cmd)
        self.assertEqual(len(self.strip(parser9.getSourceCode())), 2192)
        self.assertTrue("Included" in parser9.getMessages().strip())


    def testDisplayText(self):
        cmd = "%mime text/plain"+os.linesep+" %display box([1,1,1]); "+os.linesep
        parser = Parser()
        parser.setup()
        parser.parse(cmd)
        result = parser.renderMime()
        self.assertNotEqual(result, None)




if __name__ == '__main__': 
    unittest.main() 

