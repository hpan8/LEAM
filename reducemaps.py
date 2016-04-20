#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
import math
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint
from centermap2indexlist import centermap2indexlist

DEBUG = 2
if DEBUG == 1:
    SPEEDMAP = "./Data/speedmaptest_1.txt"
    TRAVELCOSTMAP = "./Data/travelcostmaptest_#.txt"
elif DEBUG == 2:
    SPEEDMAP = "./Data/speedmap-cut.txt"
    TRAVELCOSTPATH = "./Data/costmaps"
    TRAVELCOSTMAP = "travelcostmap-cut.txt"
else:
    SPEEDMAP = "./Data/speedmap.txt"
    TRAVELCOSTMAP = "./Data/travelcostmap.txt"

"""
This script will do:
1) convert costmap for each pop/emp center into attractive map
2) overlap 100 attractive maps according to their weights
"""

def outfilename(cellx, celly, path, fname, dirname, count):
    """Modify filename "file.txt" to be "cell0_0/file_0_0_SE1.txt" for starting cell (0,0) on the first 2hrs run.
    """
    return path + "/cell" + "_" + str(cellx) + "_" + str(celly) + "/" + fname[:-4]\
                         + "_" + str(cellx) +"_" + str(celly) + "_" +dirname + str(count) + ".txt"
                        
def costmap2attrmap(costmap):
    costmatrix = pd.read_csv(costmap, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
    attmatrix = 1/costmatrix
    pprint(attmatrix)
    return attmatrix
    
def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    attinxcol = speedmap.shape
    indexlen = attinxcol[0]
    columnlen = attinxcol[1]
    attrmap = pd.DataFrame(index=range(indexlen), columns=range(columnlen)) #initialize costmap with nan
    attrmap = attrmap.fillna(0)    #initialize costmap with 0
    for i in range(100):
        (disW, disN, weight) = centermap2indexlist('./Data/toppopascii.txt')[i]
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        newattrmap = costmap2attrmap(costmapfile)
        attrmap = attrmap + weight*newattrmap

if __name__ == "__main__":
    main()
    
    
    

