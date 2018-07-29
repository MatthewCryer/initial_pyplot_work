import argparse
__author__ = 'MattC'

parser = argparse.ArgumentParser(description= \
 'Script to batch plot all Itime plots, keyword time')
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
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#print (os.path.abspath(path))

targetdir = (path + 'Annotated_Images') #need to make the full path externally to the otherwise the if stmnt doesn't work - makedirs creates the dir in it's home folder

if not os.path.exists(targetdir):
    print ('Doesn\'t think it is there')
    os.makedirs(targetdir)
    print('The folder %s was created' % targetdir)
else:
    print ('Thinks it is there')
    print('The folder %s already exists' % targetdir)

for root,dir,files in os.walk(path, topdown=False): #the topdown tells the script to look at the collection of files directly in path last
    xlsfiles=[f for f in files if 'time' in f] #this ensures break files are not pulled through
    #print (xlsfiles)

def reducelist(a):
    reducedlist = []
    roundedlist = []
    for i in a:
        if int(i) not in set(roundedlist):
            reducedlist.append(i)
            roundedlist.append(int(i))
    return reducedlist

labeldict = {'DrainI' : "Current $I_{ds}$ (A)", 'DrainV' : "Voltage $V_{ds}$ (V)", 'GateV' : "GateV (V)", 'Time' : "Time (s)"} #defines the label wanted for each type of plot

for f in xlsfiles:
    try:
        wb = xlrd.open_workbook(os.path.join(root, f))
        s = (len(wb.sheets()) - 2)
        sheet1 = wb.sheet_by_index(0)
        rip = [[sheet1.cell_value(r, c) for c in range(sheet1.ncols)] for r in range(sheet1.nrows)]
        data = rip
        ripasarray = np.asarray(rip)
        del data[0]
        datanew = np.asarray(data)
        x = 'Time'
        y = 'DrainI'
        xcol = np.where( x == ripasarray[0,:])
        xcolint = xcol[0][0]
        ycol = np.where( y == ripasarray[0,:])
        ycolint = ycol[0][0]
        timevalues = datanew[:, xcol]
        currentvalues = datanew[:, ycol]
        T = []
        I = []
        for i in timevalues:
            T.append(i[0][0])
        npT = np.array(T)
        for i in currentvalues:
            I.append(i[0][0])
        npI = np.array(I)
        dT = np.gradient(npT)
        npdI = np.gradient(npI, dT, edge_order=2) #just do this with T and dT plot dI/dT then for T then filter the noise out the outliers are the PC response
        sigma = np.std(npdI)
        mean = np.mean(npdI)
        dI = npdI.tolist()
        #for i in npdI:
            #dI.append(i[0])
        #dIvsT = np.column_stack(T, dI)\
        biggrads = []
        for i,j in zip(T,dI):
            if j > (mean + (3 * sigma)) and i > 5:
                biggrads.append(i)
        biggradstouse = reducelist(biggrads)
        Iatbig = []
        for i,j in zip(T,I):
            if i in biggradstouse:
                Iatbig.append(j)
        smallgrads = []
        for i,j in zip(T,dI):
            if j < (mean - (3 * sigma)) and i > 5:
                smallgrads.append(i)
        smallgradstouse = reducelist(smallgrads)
        Iatsmall = []
        for i,j in zip(T,I):
            if i in smallgradstouse:
                Iatsmall.append(j)

        #plt.locator_params(axis='y', nbins=20) #don't know if this is doing anything
        figsingle = plt.figure()
        axsingle = figsingle.add_subplot(1, 1, 1)
        axsingle.set_prop_cycle(cycler('color', ['r', 'r']) + cycler('linestyle', ['-', '--']))
        axsingle.plot( datanew[:, xcolint], datanew[:, ycolint]) # does placement of this matter
        maxval = max(datanew[:, ycolint])
        minval = min(datanew[:, ycolint])
        majorLocator = MultipleLocator((maxval-minval)/20) #OR IF THIS IS
        axsingle.yaxis.set_major_locator(majorLocator)
        #axsingle.plot( datanew[:, xcolint], datanew[:, ycolint]) # does placement of this matter
        axsingle.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        axsingle.tick_params(axis='both', direction='out', top='off', right='off')
        axsingle.set_xlabel(labeldict[x])
        #axsingle.set_xlabel(filestoplot[f]['x'])
        axsingle.set_ylabel(labeldict[y])
        #axsingle.set_ylabel(filestoplot[f]['y'])
        axsingle.set_title(f, y = 1.05)
        axsingle.axis('tight')
        axsingle.axhline(y=0, color='k', linestyle='solid')
        axsingle.axvline(x=0, color='k', linestyle='solid')
        axsingle.grid('on', 'both', 'y')

        for i,j in zip(biggradstouse, Iatbig):
            axsingle.annotate(('%.4E' % j), xy = (i,j), xytext = (i,(j + 3 * ((maxval-minval)/20))), arrowprops=dict(facecolor='black', shrink=0.05), annotation_clip = False)
        for i,j in zip(smallgradstouse, Iatsmall):
            axsingle.annotate(('%.4E' % j), xy = (i,j), xytext = (i,(j + 3 * ((maxval-minval)/20))), arrowprops=dict(facecolor='black', shrink=0.05), annotation_clip = False)

        figsingle.savefig('%sAnnotated_Images/%s_annotated.png' % (path, f))
        plt.close()

    except Exception as e:
        print(f)
        print(e)
        continue
