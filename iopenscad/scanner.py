import re, os

class Scanner:
    def scann(self, scad):
        words = re.split('(\W)', scad)
        return words

     # for a start tag we try to find the matching end tag: e.g for { }
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
    
    # find specified end charactror
    def findEnd1(self, words, end):
        wordPos = 0
        while wordPos<len(words):
            word = words[wordPos]
            if word==end:
                return wordPos+1
            wordPos+=1
            
        return len(words)

    # find the indicated end string by looking at the next num entries 
    def findEndString(self, words, end, num):
        wordPos = 0
        while wordPos<len(words):
            word = "".join(words[wordPos:wordPos+num])
            if word==end:
                return wordPos+num
            wordPos+=1
        return len(words)


    # find the next white space 
    def findEndWhiteSpace(self, words):
        wordPos = 0
        word = words[wordPos]
        while not word.strip() and wordPos<len(words)-1:
            wordPos+=1
            word = words[wordPos]            
        return wordPos
    
    # if the statement ends with a new line we add it to the statement
    def findEndWithNewLine(self, words, end):
        wordPos = end
        hasLF = False
        while wordPos<len(words):
            word = words[wordPos]
            if word==os.linesep:
                hasLF = True
                wordPos+=1              
            elif word=="":
                wordPos+=1              
            elif words[wordPos]:
                if hasLF: 
                    return wordPos-1 
                else: 
                    return end
            else:
                wordPos+=1              
        return len(words)       

