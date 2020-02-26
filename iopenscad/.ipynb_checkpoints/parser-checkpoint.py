import urllib
import os.path
import subprocess
import tempfile
import os
import re

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
    name=""
    url=""
    content=""

    def __init__(self, name, url):
        self.name = name
        self.url = url
        f = urllib.request.urlopen(url)
        self.content = f.read().decode(encoding='UTF-8')   
        
    def getContent(self, url):
        if not self.content:
            f = urllib.request.urlopen(url)
            self.content = f.read().decode(encoding='UTF-8')   
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
    name=""
    url=""
    content=""
    absolutePath=""
    content=""
   
    def __init__(self, name, url):
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
    messages = ""
    tmpFiles = []
    resultFile = None

    def clear(self):
        self.messages = ""

    def convert(self, scadCode, mime):
        self.clear()
        if (scadCode.strip()):
            resultExt = self.mimeToExtension(mime)
            self.execute(scadCode, resultExt)
            return self.resultFile
        return None
    
    def execute(self, scadCode, resultExt):
        fd, self.resultFile = tempfile.mkstemp(suffix="."+resultExt, prefix=None, dir=None, text=True)
        self.tmpFiles.append(self.resultFile)
        
        # Open the file for writing.
        fd, inPath  = tempfile.mkstemp(suffix=".scad", prefix=None, dir=None, text=True)
        with open(fd, 'w') as f:
            f.write(scadCode)

        # openjscad example001.jscad -o test.stl
        command = Parser.getScadCommand()+" "+inPath+" -o "+self.resultFile
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            self.messages+=line.decode("utf-8") 

        retval = p.wait()
        os.remove(inPath)
        return retval
    
    def mimeToExtension(self, mime):
        list = mime.split("/")
        if len(list)!=2:
            raise Exception('Invalid mime type: {}'.format(mime))
        return list[1]
    
    def getMessages(self):
        return self.messages
    
    def close(self):
        for file in self.tmpFiles:
            try:
                os.remove(file)
            except Exception as inst:
                print(inst)

        self.tmpFiles = []
          

##
# Stores a single SCAD "statememnt". For our purpose we just consider a subset 
# which is relevant to prevent redundant code.
##
class Statement:
    statementType = "-"
    name = "-"
    sourceCode = ""

    def __init__(self, statmentType, sourceCode):
        self.statementType = statmentType
        self.sourceCode = "".join(sourceCode)
        
        if statmentType == "=" :
            self.name = self.sourceCode.split("=")[0].strip()
        elif statmentType == "include":
            self.name = self.extract(sourceCode,"<",">")
        elif statmentType == "use":
            self.name = self.extract(sourceCode,"<",">")
        elif statmentType == "module":
            self.name = self.extract(sourceCode,"module","(")
        elif statmentType == "function":
            self.name = self.extract(sourceCode,"function","(")
            
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
    statements = []
    tempStatement = Statement("-",[])
    messages = ""
    mime = "model/stl"
    converter = MimeConverter()
    scadCommand = ""
   
    def getStatements(self):
        return self.statements

    def getSourceCode(self):
        ## persistend code
        result = ' '.join([elem.sourceCode for elem in self.getStatements()]) 
        result += os.linesep
        ## temporary display code
        result += self.tempStatement.sourceCode
        return result
    
    def getMessages(self):
        return self.messages

    def clear(self):
        self.messages = ""
    
    def parse(self, scad):
        self.clear()
        words = re.split('(\W)', scad)
        end = 1
        while len(words)>0 and end>0:
            if not words[0].strip():
                ## collect white space
                end = self.findEndWhiteSpace(words)
                statement = Statement("-",words[0:end])
                self.insertStatement(statement)
            elif words[0] in ["include", "use"]:
                end = self.statements.index(";")
                statement = Statement(words[0], words[0:end])
                self.insertStatement(statement)
            elif words[0] == "module":
                end = self.findEnd2(words,"{","}")
                statement = Statement("module",words[0:end])
                self.insertStatement(statement)
            elif "%display" == words[0]:
                end = self.findEnd1(words,os.linesep)
                self.tempStatement = Statement("%",words[1:end])
            elif "%%display" == words[0]:
                end = len(words)-1
                self.tempStatement = Statement("%%",words[1:end])
            elif ("%mime" == words[0]):
                end = self.findEnd1(words,os.linesep)
                self.mime = "".join(words[1,end]).strip()
            elif ("%command" == words[0]):
                end = self.findEnd1(words,os.linesep)
                command =  "".join(words[1,end]).strip()
                self.setScadCommand(command)
            elif ("%lsmagic" == words[0]):
                self.messages += "%display %%display %mime %command %lsmagic %library"                
            elif ("%include" == words[0]):
                end = self.findEnd1(words,os.linesep)
                url = "".join(words[1,end]).strip()
                lib = IncludeLibrary.get(url)
                if not lib:
                    lib = IncludeLibrary.addRef(url,url)
                    print("Loaging", url)
                includeString = lib.getContent()
                statement = Statement("-",[includeString])
                self.insertStatement(statement)
            else: 
                end = self.findEnd1(words,";")
                newStatementWords = words[0:end]
                statementType = "-"
                if "function" in newStatementWords: 
                    statementType = "function"
                elif "=" in newStatementWords: 
                    statementType = "="                                                      
                statement = Statement(statementType, newStatementWords)
                self.insertStatement(statement)

            ## use unprocessed tail for next iteration    
            words = words[end:]


    def renderMime(self):
        result = self.converter.convert(self.getSourceCode(), self.mime)
        self.messages += self.converter.getMessages
        return result
           
    def findEnd2(self, words, start, end):
        index = 0
        wordPos = 0
        started = False
        while wordPos<len(words):
            word = words[wordPos]
            if word == start:
                index +=1
                started = True
                           
            if word == end:
                index -=1
                
            if started and index==0:
                return wordPos+1
            
            wordPos +=1
            
        return wordPos
    
    def findEnd1(self, words, end):
        wordPos = 0
        while wordPos<len(words):
            word = words[wordPos]
            if word==end:
                return wordPos+1
            wordPos+=1
            
        return len(words)
    
    def findEndWhiteSpace(self, words):
        wordPos = 0
        word = words[wordPos]
        while not word.strip() and wordPos<len(words)-1:
            wordPos+=1
            word = words[wordPos]
            
        return wordPos

    def insertStatement(self, newStatement):
        if not newStatement.statementType in ["-","%","%%"]:
            for i in range(len(self.statements)):
                current = self.statements[i]
                if current.name == newStatement.name and current.statementType == newStatement.statementType:
                    self.statements[i] = newStatement
                    return
        self.statements.append(newStatement)

    def getModuleNames(self):
        result = []
        for s in self.statements:
            if (s.statementType=='module'):
                result.append(s.name+"();")   
        return result
 
    ## Determines the installed scad programs
    @classmethod
    def setup(self):
        # if the scadCommand is defined there is nothing to do
        if self.scadCommand:
            return self.scadCommand
        
        test = "cube([1,1,1]);"
        mc = MimeConverter()
        # check for openscad
        self.scadCommand = "openscad"
        if mc.execute(test,"stl")==0:
            return self.scadCommand
        
        # check for openjscad
        self.scadCommand = "openjscad"
        if mc.execute(test,"stl")==0:
            return self.scadCommand

        return ""
    
    @classmethod
    def setScadCommand(self, cmd):
        self.scadCommand = cmd
        
    @classmethod
    def getScadCommand(self):
        return self.scadCommand

    def close(self):
        self.converter.close()

         