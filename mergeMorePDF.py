import re,os,operator
from PyPDF2 import PdfFileReader, PdfFileMerger, utils

runningDt = os.getcwd()
BDSDDt = runningDt + '/BDSD' #where the BDSD and content.txt are put in
tableDt = runningDt + '/testtable' #where the testtablePDF are put in.
contentTXT = BDSDDt + '/content.txt'
BDSDFullName = ''
BDSDName = ''

#follows are variables for test table PDF files.
testItems = []
testPages = []
testTableFullName = []
testTableName = []
testTableDict = {}

#
#RE patern for test table file name like 'R0-032 1_2.1 LL PZR Press SI.pdf'
#token: _2.1  we can use m.group(2) as test item number.
reTableItem1_1='.*?'	# Non-greedy match on filler
reTableItem1_2='(_)'	# Any Single Character 1
reTableItem1_3='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1
reTableItem1_4='( )'	# Any Single Character 2
rgTableItem1 = re.compile(reTableItem1_1+reTableItem1_2+reTableItem1_3+reTableItem1_4,re.IGNORECASE|re.DOTALL)

#
#RE patern for test table file name like 'R0-032 1_2.1.1 LL PZR Press SI.pdf'
#token: _2.1.1  we can use m.group(2+3+4) as test item number.
reTableItem2_1='.*?'	# Non-greedy match on filler
reTableItem2_2='(_)'	# Any Single Character 1
reTableItem2_3='(\\d+)'	# Integer Number 1
reTableItem2_4='(\\.)'	# Any Single Character 2
reTableItem2_5='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1
reTableItem2_6='( )'	# White Space 1
rgTableItem2 = re.compile(reTableItem2_1+reTableItem2_2+reTableItem2_3+reTableItem2_4+reTableItem2_5+reTableItem2_6,re.IGNORECASE|re.DOTALL)

#
#RE partern for test table file name like 'R0-032 1_2.1-D LL PZR Press SI.pdf'
#token: _2.1-D, we will use group(2~6) for test item name
reTableItem3_1='.*?'	# Non-greedy match on filler
reTableItem3_1='.*?'	# Non-greedy match on filler
reTableItem3_2='(_)'	# Any Single Character 1
reTableItem3_3='(\\d+)'	# Integer Number 1
reTableItem3_4='(\\.)'	# Any Single Character 2
reTableItem3_5='(\\d+)'	# Integer Number 2
reTableItem3_6='(-)'	# Any Single Character 3
reTableItem3_7='(D)'	# Any Single Character 4
rgTableItem3 = re.compile(reTableItem3_1+reTableItem3_2+reTableItem3_3+reTableItem3_4+reTableItem3_5+reTableItem3_6+reTableItem3_7,re.IGNORECASE|re.DOTALL)

#
#RE partern for test table file name like 'R0-032 1_2.1.1-D LL PZR Press SI.pdf'
#token: _2.1.1-D, we could use group(2~8) for test item name
reTableItem4_1='.*?'	# Non-greedy match on filler
reTableItem4_2='(_)'	# Any Single Character 1
reTableItem4_3='(\\d+)'	# Integer Number 1
reTableItem4_4='(\\.)'	# Any Single Character 2
reTableItem4_5='(\\d+)'	# Integer Number 2
reTableItem4_6='(\\.)'	# Any Single Character 3
reTableItem4_7='(\\d+)'	# Integer Number 3
reTableItem4_8='(-)'	# Any Single Character 4
reTableItem4_9='(D)'	# Any Single Character 5
rgTableItem4 = re.compile(reTableItem4_1+reTableItem4_2+reTableItem4_3+reTableItem4_4+reTableItem4_5+reTableItem4_6+reTableItem4_7+reTableItem4_8+reTableItem4_9,re.IGNORECASE|re.DOTALL)

#
#RE patern for BDSD page name like:'1.12-D  -  1/7'
#token: 1/ (only first logic page of every test)
reBDSDFirstPageNum1='.*?'	# Non-greedy match on filler
reBDSDFirstPageNum2='  '	# Uninteresting: ws
reBDSDFirstPageNum3='.*?'	# Non-greedy match on filler
reBDSDFirstPageNum4='(  )'	# White Space 1
reBDSDFirstPageNum5='(1)'	# Integer Number 1
reBDSDFirstPageNum6='(\\/)'	# Any Single Character 1
rgBDSDFirstPageNum = re.compile(reBDSDFirstPageNum1+reBDSDFirstPageNum2+reBDSDFirstPageNum3+reBDSDFirstPageNum4+reBDSDFirstPageNum5+reBDSDFirstPageNum6,re.IGNORECASE|re.DOTALL)

#
#RE pattern for BDSD page name like '1.12-D  -  1/7' 
#token: whitespace+whitespace+-+whitespace+whitespace
reBDSDPageNum1='.*?'	# Non-greedy match on filler
reBDSDPageNum2='(\\s+)'	# White Space 1
reBDSDPageNum3='(-)'	# Any Single Character 1
reBDSDPageNum4='(\\s+)'	# White Space 2
reBDSDPageNum5='(\\d+)'	# Integer Number 1
rgBDSDPageNum = re.compile(reBDSDPageNum1+reBDSDPageNum2+reBDSDPageNum3+reBDSDPageNum4+reBDSDPageNum5,re.IGNORECASE|re.DOTALL)


def dictIncrement(dictThing,currentPage,pageIncrement):
    for key,value in dictThing.iteritems():
        if value >= int(currentPage):
            dictThing[key] = value + pageIncrement
    return dictThing 

def testItemPattern(BDSDPage):
    testItem = ''
    if rgBDSDFirstPageNum.search(BDSDPage) != None:
        m =rgBDSDFirstPageNum.search(BDSDPage) 
        #hereafter for loop is used to generate test item number for BDSDPage    
        for i in range(0,len(BDSDPage)):
            if BDSDPage[i] != ' ':
                testItem += BDSDPage[i]
            else:
                break

    else:
        print "Error:\nfile name '%s' is wrong, please check it!" % BDSDPage
    
    return testItem

def BDSDContentFillter(fname):
    testItems = []
    testPages = []
    with open(fname) as f:
        content = f.readlines()
    page = -1
    for BDSDPage in content:
        pageFillter = rgBDSDPageNum.search(BDSDPage)
        firstPageFillter = rgBDSDFirstPageNum.search(BDSDPage)
        if pageFillter != None:
            page += 1

        if firstPageFillter != None:
            testItems.append(testItemPattern(BDSDPage))
            testPages.append(page)

    testItemsPages = dict(zip(testItems,testPages))
    return testItemsPages

#
#catch names of all pdffiles in destination directory of test tables.
#An filename list should be returned.
#
def walkTableDirectory(tableDt):
    global testTableFullName, testTableName, testTableDict
    getList = []
    getName = []
    list_dirs = os.walk(tableDt) 
    for root, dirs, files in list_dirs: 
        for f in files:
            filePathName = root +'/' + f
            if f[0] != '.' and f.endswith('.pdf'):
                getList.append(filePathName) 
                getName.append(f)
        testTableFullName = list(getList) 
        testTableName = list(getName)
    testTableDict = dict(zip(testTableFullName, testTableName))

def walkBDSDDirectory(BDSDDt):
    global BDSDFullName,BDSDName
    getList = []
    getName = []
    list_dirs = os.walk(BDSDDt) 
    for root, dirs, files in list_dirs: 
        for f in files:
            filePathName = root +'/' + f
            if f[0] != '.' and f.endswith('.pdf'):
                getList.append(filePathName) 
                getName.append(f)
        BDSDFullName = list(getList) 
        BDSDName = list(getName)

#
#get test item number from name of test table PDF file.
#called in manipulatePDF()
def getTestItem(testTableName):
    testItem = ''
    if rgTableItem1.search(testTableName) != None:
        m = rgTableItem1.search(testTableName)
        testItem = m.group(2)
    elif rgTableItem2.search(testTableName) != None:
        m = rgTableItem2.search(testTableName)
        testItem = m.group(2)+m.group(3)+m.group(4)
    elif rgTableItem3.search(testTableName) != None:
        m = rgTableItem3.search(testTableName)
        testItem = m.group(2)+m.group(3)+m.group(4)+m.group(5)+m.group(6)
    elif rgTableItem4.search(testTableName) != None:
        m = rgTableItem4.search(testTableName)
        testItem = m.group(2)+m.group(3)+m.group(4)+m.group(5)+m.group(6)+m.group(7)+m.group(8)
    else:
        print "Error:\nfile name '%s' is wrong, please check it!" % testTableName

    return testItem
#
#Manipulate PDF files. Insert test table into logic diagram by page number.
#
def manipulatePDF():
    global BDSDFullName,contentTXT
    global testTableName, testTableFullName,testTableDict
    input0 = PdfFileReader(file(BDSDFullName[0],'rb'))
    merger1 = PdfFileMerger()
    numBDSD = input0.getNumPages()
    merger1.append(fileobj = input0, pages = (0,numBDSD)) #generate an instance for BDSD file
    pageIncrement = 0 
    i=0 #count how many test tables are inserted to BDSD file.
    tableCount = 0
    testItemsPagesInitial = BDSDContentFillter(contentTXT)
    exceptCount = False
    for testTable in testTableDict:
        try:
            startPage = int(testItemsPagesInitial[getTestItem(testTableDict[testTable])])
        except KeyError as k:
            exceptCount = True
            print "\nError: '%s'" % testTable
            print "Above file is failed to merge into BDSD. You may want to abort this process and check both:\n    1. file name of test table, or\n    2. BDSD page number."
        position = startPage 
        fileObj = PdfFileReader(file(testTable,'rb'))
        tableCount += 1
        pages = range(0, fileObj.getNumPages())
        merger1.merge(position , fileObj, pages)
        i += 1
        currentPage = startPage
        pageIncrement = fileObj.getNumPages()
        testItemsPagesInitial = dictIncrement(testItemsPagesInitial,currentPage,pageIncrement)
#open testtable and put all pages of it into a reader object.
#for page in range(0,1):
    try:
        merger1.write(open('merger output.pdf','wb'))
    except:
        utils.PdfReadError()
        print "\nError: There's an error occured during generate the final output PDF file, please feedback this issue to ChuRui, thanks a lot.\n"
    if exceptCount:
        print "Warning: output PDF file couldn't be used in case there is an Error.\n"
    else:
        print "%d Test Tables successfully merged to %s, please check the output file." % tableCount, BDSDFullName[0]

    
walkTableDirectory(tableDt)
walkBDSDDirectory(BDSDDt)
manipulatePDF()
raw_input('Press any key to quit...')
