#!/usr/bin/env python
import os
import sys
import math
import logging
import numpy as np
import pandas as pd
import time
from numpy import maximum
from pandas import DataFrame
from pprint import pprint

"""
This script will do:
1) use centermap2indexlist.py to read centerlist and select one according to user input. (about 34.3seconds, 58 percent CPU usage)
2) genearate stocastic greedy random walk with probility distribution according to the speed in the nearby cells.
3) optimize random walk to similualte real world walking by assign a direction distribution. 
   For example, assign one direction out of 4 directions: NW, NE, SW, SE initially. Then,
   		        assign a probabiltiy dirP to the intended direction (eg. NW),
   		        assign probabiltiy dirsideP which is less than half of (1-dirP) to the two directions nearby (eg. NE, SW), 
   		        and assign (1-dirP-2*dirsideP) to the opposite direction of the intended direction.
4) This scripts generate 800 maps for the selected cell with the last map as the final travel cost map: NW100
   Map generation for 5 steps takes about 31.85 seconds with 60 percent CPU usage.
   To obtain a travelcost map for one cell, it takes at least 800*31.85 = 25480 seconds ~= 424 min ~= 7hrs.
   However, without log file and intermediate travelcost maps, the process will be much faster ==> set FASTNOLOG to 1 
   ==> about 1hr per map 
"""

FASTNOLOG = 1
ISEMP = 1

if (ISEMP == 1):
    TRAVELCOSTPATH = "./Data/costmaps"
    CENTERLIST="./Data/empcenterlist.txt"
else:
    TRAVELCOSTPATH = "./Data/costmaps"
    CENTERLIST="./Data/popcenterlist.txt"

SPEEDMAP = "./Data/speedmap.txt"
DIRPROBMAP = "./Data/dirprobmap.txt"
TRAVELCOSTMAP = "travelcostmap.txt"
HEADER = "./Input/arcGISheader.txt" 

CELLSIZE = 30 #meters
MAXCOST = 90 #minutes
MAXMOVE = 1000 #cell                    #if highest speed is 933 meters/min = 34.78 miles.hr = 56 km/hr, 1000*30*sqrt(2)/933 = 45.47min. If 90min, need 2000 steps
REPEATTIMES = 100
DIRP = 0.3                              #possibility to go to pre-selected direction, e.g. N
DIRNEARP = 0.2                          #possibiltiy to go to the two directions near the selected e.g.NW and NE
DIRSIDEP = 0.12                         #possibiltiy to go to the two directions at 90 degree difference e.g.W and E
DIROPP = 1-(DIRP+2*DIRNEARP+2*DIRSIDEP) #possibility to go to the other directions. e.g. S, SW, and SE #this should not be set to 0


def createdirectorynotexist(fname):
    """Create a directory if the directory does not exist.
       @param: fname is the full file path name
       @reference:[http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output]
    """
    if not os.path.exists(os.path.dirname(fname)):
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as exc: #Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def min(x, y):
    if math.isnan(x):
        return y
    if math.isnan(y):
        return x
    if x < y:
        return x
    else:
        return y
    

class RandomWalk():
    def __init__(self, cellx, celly, speedmap=SPEEDMAP, dirprobmap=DIRPROBMAP, 
        travelcostpath=TRAVELCOSTPATH, travelcostmap=TRAVELCOSTMAP, 
        maxcost=MAXCOST, maxmove=MAXMOVE, repeattimes=REPEATTIMES, cellsize=CELLSIZE, 
        dirP=DIRP, dirnearP = DIRNEARP, dirsideP=DIRSIDEP, diropP=DIROPP):
        """ Random Walk from one cell on a given map
        Update dirlist for walking in each direction.
        Update repeatcost and costaccumulated for each 2hrs move.
        @param: cellx and celly is the curretn position x and y indexies in speedmap.
        speedmap is a matrix with speed value meters/min in each cell and each cell is 30 meters.
                cellsize is the length of each cell.
                maxcost is the termiantion cost from current cell doing stocastic greedy random walk.
                maxmove is the maximum number of cells to move before termination.
                repeattimes is the times for each cell to conduct maxcost walks in each direction.
                dirP is the probabilty that goes for a pre-selected direction.
                dirsideP is the probabilty that goes for the two directions near pre-selected direction.
                diropP is the proabiltiy taht goes for the opposite direction of pre-selected direction.
                """
        # W: west, N: north, E: east, S:South
        #read in values
        self.speedmatrix=pd.read_csv(speedmap, skiprows=6, header=None, sep=r"\s+")
        self.dirprobmatrix=pd.read_csv(dirprobmap, skiprows=6, header=None, sep=r"\s+")
        self.cellx=cellx                           #initial starting cell x index
        self.celly=celly                           #initial starting cell y index
        self.distN = cellx                         #current cell x index
        self.distW = celly                         #current cell y index #(cellx, celly) = (0, 1) = (disN, disW)
        self.maxmove = maxmove
        self.distancetuple = self.speedmatrix.shape
        self.xmax = self.distancetuple[0]
        self.ymax = self.distancetuple[1]
        self.maxcost=maxcost
        self.cellsize=cellsize
        self.outfileheader = self.extractheader(HEADER)
        
        #initiliaze parameters
        self.costmap = pd.DataFrame(index=range(self.xmax), columns=range(self.ymax)) #initialize costmap with nan
        self.costmap = self.costmap.fillna(999)                                                               #initialize costmap with 999
        self.costmap.iloc[self.cellx, self.celly] = 0 # set the starting point cost to be 0
        self.costaccumulated = 0
        self.travelpathlist = []
        self.visited_dict = {}

        # select a seed for this cell to parallize the travelcost maps for each cell.
        # The seed of this cell is the product of the x and y axis positions of this cell.
        seedbase = self.cellx * self.celly
        np.random.seed(seedbase)

        self.walk8directions(travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)

    def walk8directions(self, travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP):
        """Walk in each of the 8 directions. 
        """
        self.walkeachdirection("N",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("NE",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("E",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("SE",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("S",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("SW",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("W",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.walkeachdirection("NW",travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP)
        self.costmap[self.costmap < 20] = 20
        if FASTNOLOG == 1:
            outcostfilename = self.outfilename(travelcostpath, travelcostmap, "NW", 100)
            self.outputmap(self.costmap, outcostfilename)

    def walkeachdirection(self, dirname, travelcostpath, travelcostmap, repeattimes, dirP, dirnearP, dirsideP, diropP):
        """Walk in one direction for <repeattimes> times. Each time generate an updated cost map
           that has accumulated result of previous runs.
           First get the direction probability distribution and then move 2hrs.
           Last, call outcostfilename to output the files into Data/costmaps folder.
        """
        count = 0
        for i in range(repeattimes): # try the converge times=repeattimes
            print dirname, i, "#####################################################################################"
            self.dirlist = self.getdirlist(dirname, dirP, dirnearP, dirsideP, diropP)
            self.move2hrs()
            if FASTNOLOG == 0:
                outcostfilename = self.outfilename(travelcostpath, travelcostmap, dirname, i)
                self.outputmap(self.costmap, outcostfilename)

    def outfilename(self, path, fname, dirname, count):
        """Modify filename "file.txt" to be "cell0_0/file_0_0_SE1.txt" for starting cell (0,0) on the first 2hrs run.
        """
        return path + "/cell" + "_" + str(self.cellx) + "_" + str(self.celly) + "/" + fname[:-4]\
                             + "_" + str(self.cellx) +"_" + str(self.celly) + "_" +dirname + str(count) + ".txt"

    def getdirlist(self, dirname, dirP, dirnearP, dirsideP, diropP):
        """ @input: dirname:  a direction name string
                    dirP:     possiblity to move to the selected direction 
                    dirnearP: possiblity to move to two directions near the selected
                    dirsideP: possiblity to move to two directions of 90 degrees to the selected
                    diropP:   possiblity to move to three other directions
            @return a list of possiblity distribution in the order of [N, S, W, E, NW, NE, SW, SE]
        """
        p0 = dirP
        p1 = dirnearP
        p2 = dirsideP
        p3 = diropP
        
        if dirname == "N":
            #                    [ 0   1   2   3   4   5    6   7 ]
            #                    [ N   NE  E   SE  S   SW   W  NW ]
            pl =                 [ p0, p1, p2, p3, p3, p3, p2, p1 ]
        elif dirname == "NE":
            pl =                 [ p1, p0, p1, p2, p3, p3, p3, p2 ]
        elif dirname == "E":
            pl =                 [ p2, p1, p0, p1, p2, p3, p3, p3 ]
        elif dirname == "SE":
            pl =                 [ p3, p2, p1, p0, p1, p2, p3, p3 ]
        elif dirname == "S":
            pl =                 [ p3, p3, p2, p1, p0, p1, p2, p3 ]
        elif dirname == "SW":
            pl =                 [ p3, p3, p3, p2, p1, p0, p1, p2 ]
        elif dirname == "W":
            pl =                 [ p2, p3, p3, p3, p2, p1, p0, p1 ]
        elif dirname == "NW":
            pl =                 [ p1, p2, p3, p3, p3, p2, p1, p0 ]
        
        #      [ N       S     W      E      NW     NE     SW     SE  ]
    #   print  [pl[0], pl[4], pl[6], pl[2], pl[7], pl[1], pl[5], pl[3]]  
        return [pl[0], pl[4], pl[6], pl[2], pl[7], pl[1], pl[5], pl[3]]
        
        
    def move2hrs(self):
        # reset values
        self.costaccumulated = 0
        print "costaccumulated: ", self.costaccumulated
        self.travelpathlist = [] # reset self.travelpathlist each time
        self.distN = self.cellx  #reset to starting cell
        self.distW = self.celly  #reset to starting cell
        print "celly, cellx: ", self.distN, self.distW

        # make continuous moves
        for i in range(self.maxmove):  # it is necessary to set up the upper number of moves
                                       # otherwise, in a small map, it may never exceed maxcost and not stop
            print i, " times=========================================================================="
            
            if self.costaccumulated < self.maxcost:
                print "costaccumulated: ", round(self.costaccumulated,2)
                self.makeonemove()
            else:
                print "exceed maxcost"
                print "costaccumulated: ", round(self.costaccumulated,2)
                break
        print self.travelpathlist
        
               
    def makeonemove(self):
        # === fetch current cell data ===
        distN = self.distN                           #distance to top boundary   (steps of moves)
        distS = self.xmax-1-distN                    #distance to bottom boundary  (steps of moves)
        distW = self.distW                           #distance to left boundary   (steps of moves) 
        distE = self.ymax-1-distW                    #distance to right boundary (steps of moves)
        pl = self.dirlist                            #direction possibility distribution
        
        print "current cell: ", "distN:", distN, " distW:", distW, " distS:", distS, " distE:", distE
        
        # if not meet the boundary, assign the speed in speed map,
        # and assign speed to be 0 otherwise.
        speedW = speedN = speedE = speedS = 0
        speedNW = speedNE = speedSW = speedSE = 0
        speedC = self.speedmatrix.iloc[distN, distW]
        costC = self.costmap.iloc[distN, distW]
        if distN != 0:
            speedN = self.dirprobmatrix.iloc[distN-1, distW]
        if distS != 0: 
            speedS = self.dirprobmatrix.iloc[distN+1, distW]
        if distW != 0: 
            speedW = self.dirprobmatrix.iloc[distN, distW-1]
        if distE != 0: 
            speedE = self.dirprobmatrix.iloc[distN, distW+1]
            
        if distN != 0 and distW != 0: 
            speedNW = self.dirprobmatrix.iloc[distN-1, distW-1]
        if distN != 0 and distE != 0:
            speedNE = self.dirprobmatrix.iloc[distN-1, distW+1]
        if distS != 0 and distW != 0:
            speedSW = self.dirprobmatrix.iloc[distN+1, distW-1]
        if distS != 0 and distE != 0:  
            speedSE = self.dirprobmatrix.iloc[distN+1, distW+1]
             
        print "dirproblist: ", round(speedN,2), round(speedS,2), round(speedW,2), round(speedE,2), \
                             round(speedNW,2), round(speedNE,2), round(speedSW,2), round(speedSE,2), round(speedC,2)
        
        # === caculate probability list ===
        #direction weight list, the direction has more probabiltiy are assigned a larger weight
        weightlist = [speedN*pl[0], speedS*pl[1], speedW*pl[2], speedE*pl[3], \
                   speedNW*pl[4], speedNE*pl[5], speedSW*pl[6], speedSE*pl[7]]
        print weightlist
        #normalization_factor will never be 0
        normfactor = (weightlist[0] + weightlist[1] + weightlist[2] + weightlist[3] + \
                    weightlist[4] + weightlist[5] + weightlist[6] + weightlist[7])
        print normfactor
        #p_list is the possiblity list to go which direction from current cell. 
        #p_list = weightlist/normalization_factor
        try:
            p_list = [weightlist[0]/normfactor, weightlist[1]/normfactor, weightlist[2]/normfactor, weightlist[3]/normfactor, \
                      weightlist[4]/normfactor, weightlist[5]/normfactor, weightlist[6]/normfactor, weightlist[7]/normfactor]
        except ZeroDivisionError:
            p_list = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
            print "divide by zero"
            
        print "plist: ", np.round(p_list,3)
            
        # === decide which direction to move ===
        #choose 1 value out of 8 values with p_list with possibility distribution
        move = np.random.choice(8, 1, p=p_list)[0]

        if move == 0:             #move to north
            self.distN -= 1
        elif move == 1:           #move to south
            self.distN += 1
        elif move == 2:           #move to west
            self.distW -= 1
        elif move == 3:           #move to east
            self.distW += 1
        elif move == 4:           #move to northwest
            self.distN -= 1
            self.distW -= 1
        elif move == 5:           #move to northeast
            self.distN -= 1
            self.distW += 1
        elif move == 6:           #move to southwest
            self.distN += 1
            self.distW -= 1
        else:                     #move to southeast
            self.distN += 1
            self.distW += 1
        
        speedCnew = self.speedmatrix.iloc[self.distN, self.distW]
            
        if move < 4:
            traveldisthalf = 30/2.0
        else:
            traveldisthalf = 30*math.sqrt(2.0)/2.0
    
        try:
            traveltime = traveldisthalf/speedC + traveldisthalf/speedCnew
        except ZeroDivisionError:
            traveltime = float("nan")
            print "divide by zero"
            
        print "move: ", move, ",distN: ", self.distN, ",distW: ", self.distW, \
              ",oldspeed: ", round(speedC,2), ", newspeed: ", round(speedCnew,2), ", traveltime: ", traveltime
        
        # === update the cost map ===
        #Update the travel time/cost from initial cell to the current cell
        #which is the traveltime of traveling one cell plus the previous traveling time costC
        #Note: update only if the current cost is smaller than the previous one
        cell = (self.distN, self.distW)
        costNew = min(self.costmap.iloc[cell], traveltime+costC)
        print "costC: ", costC, " costNew: ", costNew
        self.costaccumulated = costNew
        self.costmap.iloc[cell] = costNew

        self.travelpathlist.append((self.distN, self.distW, costNew))
        self.visited_dict[cell] = costNew

    def extractheader(self, headermap):
        with open(headermap, 'r') as h:
            header = h.read()
        return header

    def outputmap(self, matrix, travelcostmap):
        """Copy the header meta information from speedmap, and output travelcost/travelpath matrix to map
           @param: matrix is the matrix to be saved in outputfile, a .txt file.
        """
        # if travelcostmap's path directory does not exist, creat the directory.
        createdirectorynotexist(travelcostmap)
        with open(travelcostmap, 'w') as w:
            w.writelines(self.outfileheader)
        matrix.to_csv(path_or_buf=travelcostmap, sep=' ', index=False, header=False, mode = 'a') # append
            
        for (x,y) , val in self.visited_dict.iteritems():
            print "(" ,x, ",",y,")",val

def main(argv):
    start = time.time()
    cellnum = int(sys.argv[1])
    if cellnum >= 100:
        print "Error: the cellnum choice should be less than 100"
        exit(0)

    # read only one popcenter specified by cellnum from popcenterlist
    with open(POPCENTERLIST, 'r') as p:
        popcenterlist = p.readlines()
    (disW, disN, weight) = popcenterlist[cellnum].strip('\n').split(',')
    print disW, disN, weight

    # redirect stdout to log file
    logname = "./Data/costmaps/cell_" + disW + "_" + disN + "/log.txt"
    createdirectorynotexist(logname)
    sys.stdout = open(logname, 'w')

    RandomWalk(int(disW),int(disN)) #distW, distN
    end = time.time()
    print (end-start)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Error: Need an argument less than 99 as cellnum choice."
        exit(0)
    main(sys.argv[1:])
