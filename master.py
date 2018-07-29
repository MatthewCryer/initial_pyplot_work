import argparse
__author__ = 'MattC'

parser = argparse.ArgumentParser(description= \
 'Script to batch plot all SCS output files in the path folder, dependent upon file name, keywords are time, Voc, Isc, gatestep, output, gate, break, mem')
parser.add_argument('-path', help='Path where files to be plotted are', required=True)
args = parser.parse_args()

print ("The path you want to use is %s" % args.path)


path = args.path

assert path.endswith('/'), 'Path needs to end with /'

import os

newpath = "%sSplitCycles/" % path

os.system("python cyclesheetsplitter.py -p %s" % path)

os.system("python SCS4200_1.py -p %s" % newpath)

"""os.system("python 2axisIVtime.py -p %s" % newpath)

os.system("python me2.py -p %s" % newpath)"""  % optional variants
