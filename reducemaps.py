#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
import math
import os
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint
from centermap2indexlist import centermap2indexlist

CENTERMAP = "./Data/pop_center.txt"
SPEEDMAP = "./Data/speedmap.txt"
TRAVELCOSTPATH = "./Data/costmaps"
TRAVELCOSTMAP = "travelcostmap.txt"
ATTRACTIVEMAP = "./Data/attrmap.txt"


"""
This script will do:
1) convert costmap for each pop/emp center into attractive map
2) overlap 100 attractive maps according to their weights

"""

def outfilename(cellx, celly, path, fname, dirname, count):
    """Modify filename "file.txt" to be "cell0_0/Data/file_0_0_SE1.txt" for starting cell (0,0) on the first 2hrs run.
    """
    return path + "/cell" + "_" + str(cellx) + "_" + str(celly) + "/" + fname[:-4]\
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

def extractheader(speedmap):
    with open(speedmap, 'r') as r:
        lines = r.readlines()
        lines = [l for l in lines[:6]] # 6 is the number of header rows
        return lines
    
def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    header = extractheader(SPEEDMAP)
    attinxcol = speedmap.shape
    indexlen = attinxcol[0]
    columnlen = attinxcol[1]
    attrmap = pd.DataFrame(index=range(indexlen), columns=range(columnlen)) #initialize costmap with nan
    attrmap = attrmap.fillna(0)    #initialize costmap with 0
    centerlist = centermap2indexlist(CENTERMAP)
    for i in range(99):
        (disW, disN, weight) = centerlist[i]
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        try:
           newattrmap = costmap2attrmap(costmapfile)
        except IOError:
            print "file not found: ", outfilename
            continue
        attrmap = attrmap + weight*newattrmap
        print "done 1 map"
    attrmap.replace([np.inf, -np.inf], np.nan)
 
    
    with open(ATTRACTIVEMAP, 'w') as w:
        w.writelines(header)
    matrix.to_csv(path_or_buf=ATTRACTIVEMAP, sep=' ', index=False, header=False, mode = 'a') # append

if __name__ == "__main__":
    main()
    
    
    

