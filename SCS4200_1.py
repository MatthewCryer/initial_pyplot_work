import argparse
__author__ = 'MattC'

parser = argparse.ArgumentParser(description= \
 'Script to batch plot all non mem plot SCS output files in the path folder, dependent upon file name, keywords are time, Voc, Isc, gatestep, output, gate, break')
parser.add_argument('-path', help='Path where files to be plotted are', required=True)
args = parser.parse_args()

print ("The path you want to use is %s" % args.path)
#print ('This will plot %s with %s on the x-axis and %s on the y-axis' % (args.f, args.x, args.y))

path = args.path

assert path.endswith('/'), 'Path needs to end with /'

import os
import xlrd
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

#print (os.path.abspath(path))

targetdir = (path + 'Images') #need to make the full path externally to the otherwise the if stmnt doesn't work - makedirs creates the dir in it's home folder

if not os.path.exists(targetdir):
    print ('Doesn\'t think it is there')
    os.makedirs(targetdir)
    print('The folder %s was created' % targetdir)
else:
    print ('Thinks it is there')
    print('The folder %s already exists' % targetdir)


for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles=[f for f in files if f.endswith('.xls') and 'break' not in f and 'mem' not in f and 'me2' not in f] #this ensures break and mem files are not pulled through
    #print (xlsfiles)


#def extractdatasinglesheet(files, path, outputdictofdicts):
filestoplot = dict()
ftpwmst = dict()
for idx,f in enumerate(xlsfiles):
    try:
        if "mem" in f:
            continue
        wb = xlrd.open_workbook(os.path.join(root, f))
        s = (len(wb.sheets()) - 2)
        sheet1 = wb.sheet_by_index(0)
        rip = [[sheet1.cell_value(r, c) for c in range(sheet1.ncols)] for r in range(sheet1.nrows)]
        data = rip
        ripasarray = np.asarray(rip)
        del data[0]
        datanew = np.asarray(data)
        if ripasarray.shape[1] <= 5 or "time" in f:
            st = 1
        else:
            st = int(ripasarray.shape[1] / 4)
            ftpwmst[idx] = {'filename' : os.path.splitext(f)[0], 'sheets' : s, 'steps' : st, 'x' : "DrainV"}
            continue #pushes partially full dict entries into a seperate dict for step format files
        if "gate" in f or "transfer" in f:
            x = 'GateV'
        elif "time" in f:
            x = 'Time'
        else:
            x = [cell for cell in ripasarray[0,:] if (cell == 'DrainV' or cell == 'Voltage')]
            #x = 'DrainV'
        y = [cell for cell in ripasarray[0,:] if (cell == 'DrainI' or cell == 'Current')]
        xcol = np.where( x == ripasarray[0,:])
        xcolint = xcol[0][0]
        ycol = np.where( y == ripasarray[0,:])
        ycolint = ycol[0][0]
        if x == 'Time':
            trV = int(datanew.shape[0])
            trR = 'No'
        elif round(datanew[0, xcolint]) == round(datanew[(datanew.shape[0] - 1), xcolint]): #compares rounded values as if sweeping from -15 to 15 it will be 14.99
            trV = int(datanew.shape[0] / 2)
            trR = 'Yes'
        else:
            trV = int(datanew.shape[0])
            trR = 'No'
            assert datanew[:trV, xcolint].shape == datanew[:, xcolint].shape, 'Trace is not full data range'
        filestoplot[idx] = {'filename' : os.path.splitext(f)[0], 'sheets' : s, 'steps' : st, 'x' : x, 'xcolindex' : xcolint, 'y' : y, 'ycolindex' : ycolint,
                            'tracerequired' : trR, 'tracevalue' : trV, 'dataheaders' : ripasarray[0,:] , 'datanoheaders' : datanew}
        assert x == filestoplot[idx]['dataheaders'][filestoplot[idx]['xcolindex']], 'x header does not match location'
        assert y == filestoplot[idx]['dataheaders'][filestoplot[idx]['ycolindex']], 'y header does not match location'
    except Exception as e:
        print(f)
        print(e)
        continue

labeldict = {'DrainI' : "Current $I_{ds}$ (A)", 'DrainV' : "Voltage $V_{ds}$ (V)", 'GateV' : "GateV (V)", 'Time' : "Time (s)"} #defines the label wanted for each type of plot

ftpwmstrR = [filestoplot[f] for f in filestoplot if filestoplot[f]['sheets'] > 1 and filestoplot[f]['tracerequired'] == 'Yes' ]  #file to plot with multiple sheets and half trace
ftpwmsnotr = [filestoplot[f] for f in filestoplot if (filestoplot[f]['sheets'] > 1 and filestoplot[f]['tracerequired'] == 'No') ]  #file to plot with multiple sheets

idxtodel1 = []
for f in filestoplot:
    for k,v in filestoplot[f].items():
        if k == 'sheets':
            if v > 1:
                idxtodel1.append(f)

fstopen1trR = [] #makes a list of the files with multiple sheets that need to be re-opened to get the extra information
for i in range(len(ftpwmstrR)):
    ftopen = str(ftpwmstrR[i]['filename'] + '.xls')
    fstopen1trR.append(ftopen)

fstopen1notr = [] #makes a list of the files with multiple sheets that need to be re-opened to get the extra information
for i in range(len(ftpwmsnotr)):
    ftopen = str(ftpwmsnotr[i]['filename'] + '.xls')
    fstopen1notr.append(ftopen)

idxtodel2 = []
for f in filestoplot:
    for k,v in filestoplot[f].items():
        if k == 'steps':
            if v > 1:
                idxtodel2.append(f)

fstopen2 = []
for f in ftpwmst: #makes a list of the file names that have multiple steps in the first sheet, from the dictionary ftpwmst
    ftopen = str(ftpwmst[f]['filename'] + '.xls')
    fstopen2.append(ftopen)

for k in list(filestoplot.keys()): #cleans trace files and multi sheet files out
    if k in idxtodel1 or idxtodel2:
        del filestoplot[k]

"""Plotting the single step, single sheet datasets remaining in files to plot (a dict of dicts), still change plot type for trace requirement"""

for f in filestoplot:
    try:
        plt.locator_params(axis='y', nbins=20)
        figsingle = plt.figure()
        axsingle = figsingle.add_subplot(1, 1, 1)
        axsingle.set_prop_cycle(cycler('color', ['r', 'r']) + cycler('linestyle', ['-', '--']))
        datanew = filestoplot[f]['datanoheaders']
        if filestoplot[f]['tracerequired'] == 'No':  #round(datanew[0, xcolint]) == round(datanew[(datanew.shape[0] - 1), xcolint])
            trace = filestoplot[f]['tracevalue']
            axsingle.plot( datanew[:trace, filestoplot[f]['xcolindex']], datanew[:trace, filestoplot[f]['ycolindex']])
        else:
            trace = filestoplot[f]['tracevalue']
            axsingle.plot( datanew[:trace, filestoplot[f]['xcolindex']], datanew[:trace, filestoplot[f]['ycolindex']])
            axsingle.plot( datanew[trace:, filestoplot[f]['xcolindex']], datanew[trace:, filestoplot[f]['ycolindex']])
        #legend = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        if [filestoplot[f]['x']] == 'Time':
            maxval = max(datanew[:trace, filestoplot[f]['ycolindex']])
            minval = min(datanew[:trace, filestoplot[f]['ycolindex']])
            majorLocator = MultipleLocator((maxval-minval)/200)
            axsingle.yaxis.set_major_locator(majorLocator)
        axsingle.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        axsingle.tick_params(axis='both', direction='out', top='off', right='off')
        axsingle.set_xlabel(labeldict[filestoplot[f]['x']])
        #axsingle.set_xlabel(filestoplot[f]['x'])
        axsingle.set_ylabel(labeldict[filestoplot[f]['y']])
        #axsingle.set_ylabel(filestoplot[f]['y'])
        axsingle.set_title(filestoplot[f]['filename'], y = 1.05)
        axsingle.axis('tight')
        axsingle.axhline(y=0, color='k', linestyle='solid')
        axsingle.axvline(x=0, color='k', linestyle='solid')
        axsingle.grid('on', 'both', 'y')
        figsingle.savefig('%sImages/%s.png' % (path, filestoplot[f]['filename']))
        plt.close()
    except Exception as e:
        print(f)
        print(e)
        continue

for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles2 = [_ for _ in files if _ in fstopen1trR ]
    #print (xlsfiles2)

for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles3 = [_ for _ in files if _ in fstopen1notr ]
    #print (xlsfiles3)

for f in xlsfiles2:
    try:
        plt.locator_params(axis='y', nticks=10)
        wb = xlrd.open_workbook(os.path.join(root, f))
        count = 0
        figm = plt.figure()
        axm = figm.add_subplot(1, 1, 1)
        axm.set_prop_cycle(cycler('color', ['r', 'c', 'g', 'm', 'b', 'darkorange', 'y', 'maroon', 'lime', 'k']) * cycler('linestyle', ['-', '--']))
        #axm.set_prop_cycle([plt.cm.cool(i) for i in np.linspace(0, 1, 10)])
        for s in range(len(wb.sheets())):
            if s == 1 or s == 2:
                pass
            else:
                sheet = wb.sheet_by_index(s)
                rip = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                data = rip
                ripasarray = np.asarray(rip)
                del data[0]
                datanew = np.asarray(data)
                #if ripasarray.shape[1] <= 4:
                    #st = 1
                #else:
                    #st = int(ripasarray.shape[1] / 4)
                if "gate" in f or "Gate" in f or "transfer" in f:
                    x = 'GateV'
                elif "time" in f or "Time" in f:
                    x = 'Time'
                else:
                    x = 'DrainV'
                y = 'DrainI'
                xcol = np.where( x == ripasarray[0,:] )
                xcolint = xcol[0][0]
                ycol = np.where( y == ripasarray[0,:])
                ycolint = ycol[0][0]
                trV = int(datanew.shape[0] / 2)
                trR = 'Yes'
                trace = trV
                count += 1
                axm.plot( datanew[:trace, xcolint], datanew[:trace, ycolint], label = count)
                axm.plot( datanew[trace:, xcolint], datanew[trace:, ycolint])
        axm.legend(loc='best', fancybox=True, framealpha=0.5)
        axm.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        axm.tick_params(axis='both', direction='out', top='off', right='off')
        axm.set_xlabel(labeldict[x])
        axm.set_ylabel(labeldict[y])
        axm.set_title(f.strip('.xls'), y = 1.05)
        axm.axis('tight')
        axm.axhline(y=0, color='k', linestyle='solid')
        axm.axvline(x=0, color='k', linestyle='solid')
        #plt.grid(linestyle='solid')
        figm.savefig('%sImages/%s.png' % (path, f))
        plt.close()
    except Exception as e:
        print(f)
        print(e)
        continue

for f in xlsfiles3:
    try:
        plt.locator_params(axis='y', nticks=10)
        wb = xlrd.open_workbook(os.path.join(root, f))
        count = 0
        figm = plt.figure()
        axm = figm.add_subplot(1, 1, 1)
        axm.set_prop_cycle(cycler('color', ['r', 'r', 'g', 'g', 'b', 'b', 'y', 'y', 'k', 'k']) * cycler('linestyle', ['-']))
        #axm.set_prop_cycle([plt.cm.cool(i) for i in np.linspace(0, 1, 10)])
        for s in range(len(wb.sheets())):
            if s == 1 or s == 2:
                pass
            else:
                sheet = wb.sheet_by_index(s)
                rip = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                data = rip
                ripasarray = np.asarray(rip)
                del data[0]
                datanew = np.asarray(data)
                #if ripasarray.shape[1] <= 4:
                    #st = 1
                #else:
                    #st = int(ripasarray.shape[1] / 4)
                if "gate" in f or "Gate" in f or "transfer" in f:
                    x = 'GateV'
                elif "time" in f or "Time" in f:
                    x = 'Time'
                else:
                    x = 'DrainV'
                y = 'DrainI'
                xcol = np.where( x == ripasarray[0,:] )
                xcolint = xcol[0][0]
                ycol = np.where( y == ripasarray[0,:])
                ycolint = ycol[0][0]
                trV = int(datanew.shape[0])
                trR = 'No'
                trace = trV
                count += 1
                axm.plot( datanew[:trace, xcolint], datanew[:trace, ycolint], label = count)
                #axm.plot( datanew[trace:, xcolint], datanew[trace:, ycolint])
        axm.legend(loc='best', fancybox=True, framealpha=0.5)
        axm.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        axm.tick_params(axis='both', direction='out', top='off', right='off')
        axm.set_xlabel(labeldict[x])
        axm.set_ylabel(labeldict[y])
        axm.set_title(f.strip('.xls'), y = 1.05)
        axm.axis('tight')
        axm.axhline(y=0, color='k', linestyle='solid')
        axm.axvline(x=0, color='k', linestyle='solid')
        #plt.grid(linestyle='solid')
        figm.savefig('%sImages/%s.png' % (path, f))
        plt.close()
    except Exception as e:
        print(f)
        print(e)
        continue

#print (fstopen2)

for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles4 = [_ for _ in files if _ in fstopen2 ]
    #print (xlsfiles4)

for f in xlsfiles4: #have changed columns in each run from 4 to 3
    try:
        plt.locator_params(axis='y', nticks=10)
        wb = xlrd.open_workbook(os.path.join(root, f))
        figm = plt.figure()
        axm = figm.add_subplot(1, 1, 1)
        axm.set_prop_cycle(cycler('color', ['r', 'c', 'g', 'm', 'b', 'darkorange', 'y', 'maroon', 'lime', 'k']) * cycler('linestyle', ['-'])) #change dashes back in for trace ones
        for s in range(len(wb.sheets())):
            if s == 1 or s == 2:
                pass
            else:
                sheet = wb.sheet_by_index(s)
                rip = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                ripasarray = np.asarray(rip)
                noheaders = np.delete(ripasarray, 0, 0)
                locs = np.where( '' == ripasarray)
                datanew = np.delete(noheaders, locs[1], 1)
                steps = int(datanew.shape[1] / 3)
                DrainIcol = np.where( 'DrainI(1)' == ripasarray[0,:3] )
                # DrainIindex = [0,DrainIcol[0][0]]
                DrainVcol = np.where( 'DrainV(1)' == ripasarray[0,:3] )
                # DrainVindex = [0,DrainVcol[0][0]]
                GateVcol = np.where( 'GateV(1)' == ripasarray[0,:3] )
                # GateVindex = [0,GateVcol[0][0]]
                GateVlabel = ((ripasarray[0,GateVcol[0][0]]).split('('))[0]
                #trV = int(datanew.shape[0] / 2)
                #trR = 'Yes'
                #trace = trV
                for i in range(steps):
                    plotlabel = str(GateVlabel + ' @ ' + str(round(float(datanew[0, (GateVcol[0][0] + (3*i))]), 0)))
                    plt.plot( datanew[:,(DrainVcol[0][0] + (3*i) )], datanew[:,(DrainIcol[0][0] + (3*i) )], label=plotlabel) #change around depending upon plot type
                    #plt.plot( datanew[trace:,(DrainVcol[0][0] + (3*i) )], datanew[trace:,(DrainIcol[0][0] + (3*i) )])
        axm.legend(loc='best', fancybox=True, framealpha=0.5, ncol=3)
        axm.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        axm.tick_params(axis='both', direction='out', top='off', right='off')
        axm.set_xlabel(labeldict["DrainV"])
        axm.set_ylabel(labeldict["DrainI"])
        axm.set_title(f.strip('.xls'), y = 1.05)
        axm.axis('tight')
        #axm.set_ylim(-1E-4, 1E-4)
        axm.axhline(y=0, color='k', linestyle='solid')
        axm.axvline(x=0, color='k', linestyle='solid')
        #plt.grid(linestyle='solid')
        figm.savefig('%sImages/%s.png' % (path, f))
        plt.close()
    except Exception as e:
        print(f)
        print(e)
        continue
