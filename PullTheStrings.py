import os, os.path, re

rootDir = '.' # look down from this directory
outputFile = 'strings.csv' # output table of strings to this file
pattern1 = "(?P<quote>['"+r'"`])(?P<words>.*?)(?<![\\])(?P=quote)'
pattern2 = "(?m)<(?P<tag>[A-Za-z\-]+).*?>(?P<innerHTML>.*?)<\/(?P=tag)>"
pattern3 = "@{4}.*?\?>"
pattern4 = "@{4}[^(?>)]*"
inString = re.compile(pattern1)
inTags = re.compile(pattern2, re.DOTALL)
inPhp = re.compile(pattern3, re.DOTALL)
phpNoEnd = re.compile(pattern4, re.DOTALL)
StringArray = [['filename', 'line#', 'index/pos', 'type', 'string', 'length', 'line']] # format: filename, line#, quotIndex, quotType, string, length of string, line

def quotType(st):
    if st == '"':
        return "DQ"
    elif st == "'":
        return "SQ"
    elif st == '`':
        return "BQ"
    elif st == '>':
        return "HTML"
    else:
        return "Unknown"


def CheckContent(fname, st, pos=0):
    #print st
    if len(st) < 1:
        return True
    global inTags, StringArray
    res = True
    nFound = 0
    for cont in inTags.finditer(st):
        nFound += 1
        if not (CheckContent(fname, cont.group("innerHTML"), cont.start("innerHTML")+pos)):
            StringArray += [[fname,'pos',cont.start("innerHTML")+pos, quotType('>'), cont.group("innerHTML")]]
    if nFound == 0:
        res = False
    return res

def CheckTheFile(fname):
    global inPhp, StringArray
    f = open(fname)
    Content = f.read()
    f.close()
    c = Content.replace("<?php", "@@@@")
    if phpNoEnd.match(c):
        return
    Comtent = inPhp.sub('',c)
    #print Content
    #print '\n\n*********************************' + fname + '********************************\n\n'
    if not(CheckContent(fname, Comtent)):
        StringArray += [[fname,'pos',0, quotType('>'), Comtent]]


def pullTheStrings(filename):
    global StringArray, inString
    # extract all between quotes and put into an array
    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    lineCount = 0
    for line in lines:
        lineCount+=1
        quotIndex = 0
        for mo in inString.finditer(line):
            #print (mo.group("quote"))
            if len(mo.group("words")) > 0:
                StringArray += [[filename, lineCount, quotIndex, quotType(mo.group("quote")), mo.group("words"), len(mo.group("words")), line.replace('\r', '').replace('\n','') ]]
            quotIndex += 1
    alllines = '\n'.join(lines)

    #print (filename + ', ' + repr(lineCount))


def saveTheWorld():
    # save the array as a .csv file
    global outputFile, StringArray
    SaveString = ''
    for line in StringArray:
        SaveString += '"' + line[0] + '";' + repr(line[1]) + ';' + repr(line[2]) + ';' + line[3] + ';"' + line[4].replace('"', '""') + '";' + repr(line[5]) + ';"' + line[6].replace('"', '""') +'"\n'
    f = open(outputFile, 'w')
    f.write(SaveString)
    f.close()
    #print "Saved to [" + outputFile + ']'
    #print repr(StringArray)

for root, dirs, files in os.walk(rootDir):
    for fname in files:
        if os.path.splitext(fname)[1] in ['.php', '.js', '.css', '.sql']:
            pullTheStrings(os.path.join(root,fname))
        if os.path.splitext(fname)[1] in ['.php']:
            CheckTheFile(os.path.join(root,fname))
saveTheWorld()

#print (pattern1)
