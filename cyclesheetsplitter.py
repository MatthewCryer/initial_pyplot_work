import argparse
__author__ = 'MattC'

parser = argparse.ArgumentParser(description= \
 'Script to split out sheets from an initial file with multiple sheets')
parser.add_argument('-path', help='Path where files which need to be split are', required=True)
args = parser.parse_args()

print ("The path you want to use is %s" % args.path)
#print ('This will plot %s with %s on the x-axis and %s on the y-axis' % (args.f, args.x, args.y))

path = args.path

assert path.endswith('/'), 'Path needs to end with /'

import os
import xlrd
from xlutils.copy import copy
import xlwt
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

#print (os.path.abspath(path))

for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles=[f for f in files if f.endswith('.xls') and 'break' not in f ] #this ensures break files are not pulled through
    #print (xlsfiles)

targetdir = (path + 'SplitCycles/') #need to make the full path externally to the otherwise the if stmnt doesn't work - makedirs creates the dir in it's home folder

if not os.path.exists(targetdir):
    os.makedirs(targetdir)

for f in xlsfiles:
    try:
        wb = xlrd.open_workbook(os.path.join(root, f), on_demand=True)
        sheetlist = []
        for i,j in zip(wb.sheet_names(), wb.sheets()):
            sheetlist.append([i,j])
        for k in sheetlist:
            if k[0] == "Settings":
                sheetlist.remove(k)
        for h in sheetlist:
            if h[0] == "Calc":
                sheetlist.remove(h)
        sheets = [ sheet[1] for sheet in sheetlist ]
        for sheet in sheets:
            newwb = copy(wb)
            newwb._Workbook__worksheets = [ worksheet for worksheet in newwb._Workbook__worksheets if worksheet.name == sheet.name ]
            if sheet.name == "Data":
                sheet.name = "Cycle1"
            newwb.save(targetdir + f.strip(".xls") + "_" + sheet.name + ".xls")
    except Exception as e:
        print(f)
        print(e)
        continue
