#!/usr/bin/env python
#from StringIO import StringIO
import numpy as np
import pandas as pd
import math
import os
import time
from numpy import maximum
from pandas import DataFrame
from pprint import pprint
import multiprocessing
import thread

"""
This script will do:
1) convert costmap for each pop/emp center into attractive map
2) overlap 100 attractive maps according to their weights
3) round all float values to integers
"""

ISEMP = 0

if ISEMP == 1:
    CENTERLIST = "./Data/empcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps-emp"
    ATTRACTIVEMAP = "./Data/attrmap-emp.txt"
else:
    CENTERLIST = "./Data/popcenterlist.txt"
    TRAVELCOSTPATH = "./Data/costmaps"
    ATTRACTIVEMAP = "./Data/attrmap-pop.txt"

SPEEDMAP = "./Data/speedmap.txt"
TRAVELCOSTMAP = "travelcostmap.txt"
HEADER = "./Input/arcGISheader.txt"


def outfilename(cellx, celly, path, fname, dirname, count):
    """Modify filename "file.txt" to be "cell0_0/Data/file_0_0_SE1.txt" for starting cell (0,0) on the first 2hrs run.
    """
    return path + "/cell" + "_" + str(cellx) + "_" + str(celly) + "/" + fname[:-4] \
                         + "_" + str(cellx) +"_" + str(celly) + "_" +dirname + str(count) + ".txt"
                        
def costmap2attrmap(costmap):
    try:
        costmatrix = pd.read_csv(costmap, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
        costmatrix.replace(to_replace=0.0, value=0.001)
    except IOError as e:
        raise e
        return costmatrix

    attmatrix = 1/costmatrix
    #pprint(attmatrix)
    return attmatrix

def extractheader(header):
    with open(header, 'r') as h:
        header = h.read()
    return header
    
def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    header = extractheader(HEADER)
    attinxcol = speedmap.shape
    indexlen = attinxcol[0]
    columnlen = attinxcol[1]
    attrmap = pd.DataFrame(index=range(indexlen), columns=range(columnlen)) #initialize costmap with nan
    attrmap = attrmap.fillna(0)    #initialize costmap with 0

    with open(CENTERLIST, 'r') as p:
        centerlist = p.readlines()

    for i in range(99):
        (disW, disN, weight) = centerlist[i].strip('\n').split(',')
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        try:
           newattrmap = costmap2attrmap(costmapfile)
        except IOError:
            print "file not found: ", outfilename
            continue
        print "\nstart adding...\n"
        start = time.time()
        attrmap = attrmap + (int)weight*newattrmap
        end = time.time()
        print "done map using time: "
        print (end-start)
   
    #attrmap.replace([np.inf, -np.inf], np.nan) 
    #normalizer = np.matrix(attrmap).max()
    #attrmap /= normalizer
    with open(ATTRACTIVEMAP, 'w') as w:
        w.writelines(header)
    attrmap.round() # round to integer
    attrmap.to_csv(path_or_buf=ATTRACTIVEMAP, sep=' ', index=False, header=False, mode = 'a') # append

if __name__ == "__main__":
    main()
    
    
    

