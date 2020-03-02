##
#  Simple Parser and Renderer for SCAD commands. This implements the Kernel
#  support functionality which is needed
#
import urllib
import os.path
import subprocess
import tempfile
import os
import re
import logging
import urllib
import urllib.request
from iopenscad.scanner import Scanner
 

##
# Manages a library of include files. We support reference includes (which are
# dynamically added to the source code ) and file includes (which download the
# url into a file)  
##     
class IncludeLibrary:
    dictionary = dict()
    
    ## Adds a library by name   
    @classmethod
    def addRef(self, name, url):
        inc = IncludeRef(name, url)
        self.dictionary[name] = inc
        return inc

    def addFile(self, name, url):
        inc = IncludeFile(name, url)
        self.dictionary[name] = inc
        return inc
    
    @classmethod
    def get(self, name):
        return self.dictionary.get(name)
              
        
##
# Provides the content that is included as String
##
class IncludeRef:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.content = None

    def getContent(self):
        if not self.content:
            f = urllib.request.urlopen(self.url)
            self.content = f.read().decode(encoding='UTF-8') 
            f.close()   
        return self.content    

    def str(self):
        return self.name
    
    def resolve(self):
        return self.content

    def ref(self):
        return self.url


###   
# Downloads file from URL if it does not exist
##
class IncludeFile:
   
    def __init__(self, name, url):
        self.url=""
        self.content=""
        self.absolutePath=""
        self.content=""
        self.name = name
        if not os.path.isfile(name):
            self.createPath(name)
            self.url = url
            f = urllib.request.urlopen(url)
            self.content = f.read().decode(encoding='UTF-8')    
            text_file = open(name, "wt")
            text_file.write(self.content)
            text_file.close()
            
        if (name.startswith(os.sep)):
            self.absolutePath = name
        else:
            self.absolutePath = os.path.join(os. getcwd(), name)
            
    def createPath(self, name):
        right = name.rfind(os.sep)
        path = name[0:right]
        if (path and not os.path.isfile(path)):
            os.makedirs(path) 

    def getContent(self):
        if not self.content:
            f = urllib.request.urlopen("file://"+self.absolutePath)
            self.content = f.read().decode(encoding='UTF-8')   
        return self.content    

    def str(self):
        return self.name    
    
    def ref(self):
        return self.absolutePath

    def resolve(self):
        return "include("+self.absolutePath+")"
    

##
# Converter which translates a scad text into a file of the indicated mime type.
# There are currently 2 command line tools that can be used: openscad and
# openjscad.
## 
class MimeConverter:
    def __init__(self):
        self.messages = ""
        self.tmpFiles = []
        self.resultFile = None
        self.isError = False

    def clear(self):
        self.messages = ""
        self.isError = False

    def convert(self, scadCommand, scadCode, mime):
        self.clear()
        if scadCode.strip():
            logging.info(scadCode)  
            resultExt = self.mimeToExtension(mime)

            fd, self.resultFile = tempfile.mkstemp(suffix="."+resultExt, prefix=None, dir=None, text=True)
            self.tmpFiles.append(self.resultFile)
            
            if resultExt == 'txt':
                with open(fd, 'w') as f:
                    f.write(scadCode)
            else:
                self.execute(scadCommand, scadCode)
            return self.resultFile
        else:
            logging.warning('Empty SCAD Code!')  

        return None

    def saveAs(self, scadCommand, scadCode, fileName):
        self.resultFile = fileName
        self.execute(scadCommand, scadCode)

    
    def execute(self, openSCADConvertCommand, scadCode):
        # Open the file for writing.
        fd, inPath  = tempfile.mkstemp(suffix=".scad", prefix=None, dir=None, text=True)
        with open(fd, 'w') as f:
            f.write(scadCode)

        command = openSCADConvertCommand+" "+inPath+" -o "+self.resultFile
        # openjscad example001.jscad -o test.stl
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            self.messages+=line.decode("utf-8") 

        retval = p.wait()
        self.isError = retval != 0
        os.remove(inPath)
        return retval
    
    def mimeToExtension(self, mime):
        list = mime.split("/")
        if len(list)!=2:
            raise Exception('Invalid mime type: {}'.format(mime))
        result = list[1]
        if mime=="text/plain":
            result = "txt"
        if mime=="applicatioin/openscad":
            result = "txt"
        return result
    
    def getMessages(self):
        return self.messages
    
    def close(self):
        for file in self.tmpFiles:
            try:
                os.remove(file)
            except Exception as err:
                logging.error(err)  

        self.tmpFiles = []
          

class Setup:
    def setup(self, scadCommand):
        # if the scadCommand is defined there is nothing to do
        if scadCommand:
            return scadCommand
        
        mc = MimeConverter()
        testSCAD = "cube([1,1,1]);"

        # check for openscad
        scadCommand = "openscad"
        if mc.convert(scadCommand,testSCAD,"image/png")==0:
            return scadCommand
        
        # check for openjscad
        scadCommand = "openjscad"
        if mc.convert(scadCommand, testSCAD,"image/png")==0:
            return scadCommand

        # Default command if nothing is supported
        scadCommand = "openscad"
        return scadCommand

    def openSCADLinux(self, scadCommand):
        from sys import platform
        if platform == "linux" or platform == "linux2":
            try:
                os.environ['DISPAY']
                return scadCommand
            except Exception:
                return "xvfb-run --auto-servernum --server-num=99 openscad"
        return scadCommand


##
# Stores a single SCAD "statememnt". For our purpose we just consider a subset 
# which is relevant to prevent redundant code.
##
class Statement:

    def __init__(self, statementTypePar, sourceCode):
        self.statementType = statementTypePar
        self.sourceCode = "".join(sourceCode)
        self.name = "-"
        if statementTypePar == "=" :
            self.name = self.sourceCode.split("=")[0].strip()
        elif statementTypePar == "include":
            self.name = self.extract(sourceCode,"<",">")
        elif statementTypePar == "use":
            self.name = self.extract(sourceCode,"<",">")
        elif statementTypePar == "module":
            self.name = self.extract(sourceCode,"module","(")
        elif statementTypePar == "function":
            self.name = self.extract(sourceCode,"function","(")
        elif statementTypePar == "comment":
            self.name = self.sourceCode.strip() 
        elif statementTypePar == "-":
            self.name = self.sourceCode.strip() 
            
    ## Logic to find the name with the help of a start and end tag
    def extract(self, wordList,fromStr,toStr):
        start = wordList.index(fromStr)+1
        end = wordList.index(toStr)
        return "".join(wordList[start:end]).strip()
    
    def str(self):
        return self.sourceCode

    
## 
# The kernal can submit the same code multiple times. The major goal of this parser 
# is to prevent duplicate definitions (mainly of modules or functions)
##

class Parser:
    lsCommands = ["%clear", "%display", "%displayCode","%%display","%%displayCode", "%mime", "%command", "%lsmagic", "%include", "%use", "%saveAs"]
        
    def __init__(self):
        self.statements = []
        self.tempStatement = Statement("-",[])
        self.messages = ""
        self.mime = "image/png"
        self.converter = MimeConverter()
        self.scadCommand = ""
        self.isError = False
        self.displayRendered = False
        self.scanner = Scanner()


    def getStatements(self):
        return self.statements

    def getStatementsOfType(self, statementType):
        result = []
        for s in self.statements:
            if s.statementType == statementType:
                result.append(s)
        return result

    def getSourceCode(self):
        ## persistend code
        result = "".join([elem.sourceCode for elem in self.getStatements()]) 
        result += os.linesep
        ## temporary display code
        result += self.tempStatement.sourceCode
        result = result.replace(u'\xa0', u' ')
        return result
    
    def lineCount(self):
        return self.getSourceCode().count('\n') 

    def addMessages(self, newMessage):
        if self.messages.strip():
            self.messages = self.messages + os.linesep + newMessage
        else:
            self.messages = newMessage

    def getMessages(self):
        return self.messages

    def getMessagesExt(self):
        result = self.messages
        # if there is nothing to display we give at least some info
        if not result.strip() and not self.displayRendered:
            result = "Number of lines of OpenSCAD code: "+str(self.lineCount())+os.linesep
        return result

    def clearMessages(self):
        self.messages = ""
        self.isError = False
   
    def parse(self, scad):
        self.displayRendered = False
        self.clearMessages()
        self.tempStatement = Statement("-",[])
        words = self.scanner.scann(scad)
        end = 1
        while len(words)>0 and end>0:
            if not words[0].strip():
                ## collect white space
                end = self.scanner.findEndWhiteSpace(words)
                if "".join(words[0:end])!="":
                    statement = Statement("whitespace",words[0:end])
                    self.insertStatement(statement)
            elif "/*" == "".join(words[0:3]):
                end = self.scanner.findEndString(words,"*/", 3)
                end = self.scanner.findEndWithNewLine(words,end)
                statement = Statement("comment", words[0:end])
                self.insertStatement(statement)
            elif "//" == "".join(words[0:3]):
                end = self.scanner.findEnd1(words,os.linesep)
                statement = Statement("comment", words[0:end])
                self.insertStatement(statement)
            elif "%include" == "".join(words[0:2]):
                end = self.processInclude(words)
            elif "%use" == "".join(words[0:2]):
                end = self.processUse(words)
            elif words[0] in ["include", "use"]:
                end = self.statements.index(";")
                end = self.scanner.findEndWithNewLine(words,end)
                statement = Statement(words[0], words[0:end])
                self.insertStatement(statement)
            elif words[0] == "module":
                end = self.scanner.findEnd2(words,"{","}")
                end = self.scanner.findEndWithNewLine(words,end)
                statement = Statement("module",words[0:end])
                self.insertStatement(statement)
            elif "%clear" == "".join(words[0:2]):
                end = 2                
                self.close()
                self.addMessages( "SCAD code buffer has been cleared")
            elif "%%displayCode" == "".join(words[0:4]):
                self.displayRendered = True
                end = len(words)
                self.tempStatement = Statement(None,words[4:end])
                self.addMessages( self.getSourceCode())
            elif "%displayCode" == "".join(words[0:2]):
                end = self.scanner.findEnd1(words,os.linesep)
                tmpCode = "".join(words[2:end])
                self.addMessages( self.getSourceCode()+tmpCode)
            elif "%display" == "".join(words[0:2]):
                self.displayRendered = True
                end = self.scanner.findEnd1(words,os.linesep)
                self.tempStatement = Statement(None,words[2:end])
            elif "%%display" == "".join(words[0:4]):
                self.displayRendered = True
                end = len(words)
                self.tempStatement = Statement(None,words[4:end])
            elif "%saveAs" == "".join(words[0:2]):
                end = self.processSaveAs(words)
            elif "%mime" == "".join(words[0:2]):
                end = self.scanner.findEnd1(words,os.linesep)
                mime = "".join(words[2:end]).strip()
                if mime:
                    self.mime = mime
                self.addMessages( "The display mime type is '"+self.mime+"'")
            elif "%command" == "".join(words[0:2]):
                end = self.scanner.findEnd1(words,os.linesep)
                command =  "".join(words[2:end]).strip()
                if command:
                    self.setScadCommand(command)
                self.addMessages("The display command is '"+self.getScadCommand()+"'")
            elif "%lsmagic" == "".join(words[0:2]):
                end = 2
                commandsTxt = " ".join(self.lsCommands)
                self.addMessages("Available Commands: "+ commandsTxt )
            else: 
                end = self.processDefault(words)

            ## use unprocessed tail for next iteration    
            words = words[end:]

    def renderMime(self):
        result = None
        try:
            code = self.getSourceCode().strip()

            if code:
                result = self.converter.convert(self.scadCommand, code, self.mime)
                self.addMessages(self.converter.getMessages())
                self.isError = self.converter.isError

        except Exception as err:
            self.isError = True
            self.addMessages("Could render OpenSCAD code: "+str(err))  
               
        return result

    def saveAs(self, fileName):
        code = self.getSourceCode().strip()
        self.converter.saveAs(self.scadCommand, code, fileName)

    def insertStatement(self, newStatement):
        if  newStatement.statementType in ["module","=","comment","-"]:
            for i in range(len(self.statements)):
                current = self.statements[i]
                if current.name == newStatement.name and current.statementType == newStatement.statementType:
                    self.statements[i] = newStatement
                    return            
        self.statements.append(newStatement)

    ## Determines the currently defined module names
    def getModuleNames(self):
        result = []
        for s in self.statements:
            if (s.statementType=='module'):
                result.append(s.name+"();")   
        return result
 
    ## Determines the installed scad programs
    def setup(self):
        self.scadCommand = Setup().setup(self.scadCommand)
        return self.scadCommand
    
    def setScadCommand(self, cmd):
        self.scadCommand = cmd
        
    def getScadCommand(self):
        return self.scadCommand

    def getIncludeString(self, words, end):
        url = "".join(words[2:end]).strip()
        lib = IncludeLibrary.get(url)
        if not lib:
            lib = IncludeLibrary.addRef(url,url)
        includeString = lib.getContent().strip()
        return includeString

    def processInclude(self, words):
        end = self.scanner.findEnd1(words,os.linesep)
        try:
            scadCode = self.getIncludeString(words, end)
            useParser = Parser()
            useParser.parse(scadCode)
            count = 0
            for statement in useParser.statements:
                self.insertStatement(statement)
                count += 1
            self.addMessages("Included number of statements: "+str(count)) 
        except Exception as err:
            self.isError = True
            self.addMessages("Could not include file: "+str(err))  
        return end

    def processUse(self, words):
        end = self.scanner.findEnd1(words,os.linesep)
        try:
            scadCode = self.getIncludeString(words, end)
            useParser = Parser()
            useParser.parse(scadCode)
            count = 0
            for statement in useParser.statements:
                if (statement.statementType in ["include","use","module","function","=","whitespace","comment"]):
                    self.insertStatement(statement)
                    count += 1
            self.addMessages("Included number of statements: "+str(count)) 
        except Exception as err:
            self.isError = True
            self.addMessages("Could not include file: "+str(err))  
        return end

    def processSaveAs(self, words):
        end = self.scanner.findEnd1(words,os.linesep)
        try:
            fileName = "".join(words[2:end]).strip()
            self.saveAs(fileName)
            self.addMessages("File '" +fileName+ "' created")
        except Exception as err:
            self.addMessages("Could not save file: "+str(err))  
        return end

    def processDefault(self, words):
        if words[0:1]=="%":
            end = self.scanner.findEnd1(words,os.linesep)
            self.addMessages("Unsupported Command: "+"".join(words[0:end]))  
        else:
            end = self.scanner.findEnd1(words,";")
            end = self.scanner.findEndWithNewLine(words,end)

            newStatementWords = words[0:end]
            cmd = "".join(newStatementWords)
            if (not cmd or cmd.strip().endswith(";")):
                statementType = "-"
                if "function" in newStatementWords: 
                    statementType = "function"
                elif "=" in newStatementWords: 
                    statementType = "="     
                elif not cmd and os.linesep in  newStatementWords :
                    statementType = "whitespace"     
                statement = Statement(statementType, newStatementWords)
                self.insertStatement(statement)
            else:
                self.addMessages("Syntax error: this cell does not contain valid OpenSCAD code" )
                self.isError = True
        return end

    def close(self):
        self.clearMessages()
        self.statements = []
        self.converter.close()
        self.tempStatement = Statement("-",[])

        