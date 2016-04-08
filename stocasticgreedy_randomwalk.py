#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
import math
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint

"""
This script will do:
1) genearate stocastic greedy random walk with probility distribution according to the speed in the nearby cells.
2) optimize random walk to similualte real world walking by assign a direction distribution. 
   For example, assign one direction out of 4 directions: NW, NE, SW, SE initially. Then,
   		        assign a probabiltiy dirP to the intended direction (eg. NW),
   		        assign probabiltiy dirsideP which is less than half of (1-dirP) to the two directions nearby (eg. NE, SW), 
   		        and assign (1-dirP-2*dirsideP) to the opposite direction of the intended direction.
   We will experiment on the dirP and dirsideP values.

reference: 
[1]http://pages.physics.cornell.edu/~sethna/StatMech/ComputerExercises/PythonSoftware/RandomWalk.py
[2]https://mktstk.wordpress.com/2015/01/05/simulating-correlated-random-walks-with-copulas/
[3]Viswanathan, Viswa, Anup K. Sen, and Soumyakanti Chakraborty. "Stochastic Greedy Algorithms." 
   International Journal on Advances in Software Volume 4, Number 1 & 2, 2011 (2011).
"""

DEBUG = 2
if DEBUG == 1:
    SPEEDMAP = "./Data/speedmaptest_1.txt"
    TRAVELCOSTMAP = "./Data/travelcostmaptest_#.txt"
    TRAVELPATHMAP = "./Data/travelpathmaptest_#.txt"
elif DEBUG == 2:
    SPEEDMAP = "./Data/speedmap-cut.txt"
    TRAVELCOSTMAP = "./Data/travelcostmap-cut.txt"
    TRAVELPATHMAP = "./Data/travelpathmap-cut.txt"
else:
    SPEEDMAP = "./Data/speedmap.txt"
    TRAVELCOSTMAP = "./Data/travelcostmap.txt"
    TRAVELPATHMAP = "./Data/travelpathmap.txt"

CELLSIZE = 30 #meters
MAXCOST = 120 #minutes
DIRP = 0.4                              #possibility to go to pre-selected direction, e.g. N
DIRNEARP = 0.2                          #possibiltiy to go to the two directions near the selected e.g.NW and NE
DIRSIDEP = 0.1                          #possibiltiy to go to the two directions at 90 degree difference e.g.W and E
DIROPP = 1-(DIRP+2*DIRNEARP+2*DIRSIDEP) #possibility to go to the other directions. e.g. S, SW, and SE

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
    def __init__(self, cellx, celly, speedmap, travelcostmap, dirname="SE", maxcost=MAXCOST, \
        cellsize=CELLSIZE, dirP=DIRP, dirnearP = DIRNEARP, dirsideP=DIRSIDEP, diropP=DIROPP):
        """ Random Walk from one cell on a given map
        @param: cellx and celly is the curretn position x and y indexies in speedmap.
        speedmap is a matrix with speed value meters/min in each cell and each cell is 30 meters.
                cellsize is the length of each cell.
                maxcost is the termiantion cost from current cell doing stocastic greedy random walk.
                dirP is the probabilty that goes for a pre-selected direction.
                dirsideP is the probabilty that goes for the two directions near pre-selected direction.
                diropP is the proabiltiy taht goes for the opposite direction of pre-selected direction.
                """
        # W: west, N: north, E: east, S:South
        self.speedmatrix=pd.read_csv(speedmap, skiprows=6, header=None, sep=r"\s+")
        self.cellx=cellx                           #initial starting cell x index
        self.celly=celly                           #initial starting cell y index
        self.distW = cellx                         #current cell x index
        self.distN = celly                         #current cell y index
        self.distancetuple = self.speedmatrix.shape
        self.indexlen = self.distancetuple[0]
        self.columnlen = self.distancetuple[1]
        self.maxcost=maxcost
        self.cellsize=cellsize
        ####################
        self.dirlist = self.getdirlist(dirname, dirP, dirnearP, dirsideP, diropP)
        self.costmap = pd.DataFrame(index=range(self.indexlen), columns=range(self.columnlen)) #initialize costmap with nan
        self.costmap.iloc[self.celly, self.cellx] = 0 # set the starting point cost to be 0
        self.debugmovepathmap = pd.DataFrame(index=range(self.indexlen), columns=range(self.columnlen))
        self.debugmovepathmap.iloc[self.celly, self.cellx] = 0
        self.movecount = 0
        self.costaccumulated = 0
        self.travelpathlist = []
        self.move2hrs()
        self.outputmap(self.costmap, speedmap, travelcostmap)
        self.outputmap(self.debugmovepathmap, speedmap, TRAVELPATHMAP)
    
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
        print p0, p1, p2, p3
        
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
        for i in range(100):  # it is necessary to set up the upper number of moves
                               # otherwise, in a small map, it may never exceed maxcost and not stop
            if self.costaccumulated < self.maxcost:   
                self.makeonemove()
        print "costmap: \n", self.costmap.fillna(999)
        #print "movepath:\n", self.debugmovepathmap.fillna(-1)
        self.costmap = self.costmap.fillna(999)
        self.debugmovepathmap = self.debugmovepathmap.fillna(-1)
        print self.travelpathlist
               
    
    def makeonemove(self):
        # === fetch current cell data ===
        distN = self.distN                               #distance to top boundary   (steps of moves)
        distS = self.indexlen-1-distN                    #distance to bottom boundary  (steps of moves)
        distW = self.distW                               #distance to left boundary   (steps of moves) 
        distE = self.columnlen-1-distW                   #distance to right boundary (steps of moves)
        pl = self.dirlist                                #direction possibility distribution
        
        print "######################################################################################"
        print "current cell: ", "distN:", distN, " distW:", distW, " distS:", distS, " distE:", distE
        
        # if not meet the boundary, assign the speed in speed map,
        # and assign speed to be 0 otherwise.
        speedW = speedN = speedE = speedS = 0
        speedNW = speedNE = speedSW = speedSE = 0
        speedC = self.speedmatrix.iloc[distN, distW]
        costC = self.costmap.iloc[distN, distW]
        if distN != 0:
            speedN = self.speedmatrix.iloc[distN-1, distW]
        if distS != 0: 
            speedS = self.speedmatrix.iloc[distN+1, distW]
        if distW != 0: 
            speedW = self.speedmatrix.iloc[distN, distW-1]
        if distE != 0: 
            speedE = self.speedmatrix.iloc[distN, distW+1]
            
        if distN != 0 and distW != 0: 
            speedNW = self.speedmatrix.iloc[distN-1, distW-1]
        if distN != 0 and distE != 0:
            speedNE = self.speedmatrix.iloc[distN-1, distW+1]
        if distS != 0 and distW != 0:
            speedSW = self.speedmatrix.iloc[distN+1, distW-1]
        if distS != 0 and distE != 0:  
            speedSE = self.speedmatrix.iloc[distN+1, distW+1]
             
        print "speedlist: ", speedN, speedS, speedW, speedE, speedNW, speedNE, speedSW, speedSE, speedC
        
        # === caculate probability list ===
        #direction weight list, the direction has more probabiltiy are assigned a larger weight
        weightlist = [speedN*pl[0], speedS*pl[1], speedW*pl[2], speedE*pl[3], \
                   speedNW*pl[4], speedNE*pl[5], speedSW*pl[6], speedSE*pl[7]]
        #normalization_factor will never be 0
        normfactor = (weightlist[0] + weightlist[1] + weightlist[2] + weightlist[3] + \
                    weightlist[4] + weightlist[5] + weightlist[6] + weightlist[7])
        
        #p_list is the possiblity list to go which direction from current cell. 
        #p_list = weightlist/normalization_factor
        try:
            p_list = [weightlist[0]/normfactor, weightlist[1]/normfactor, weightlist[2]/normfactor, weightlist[3]/normfactor, \
                      weightlist[4]/normfactor, weightlist[5]/normfactor, weightlist[6]/normfactor, weightlist[7]/normfactor]
        except ZeroDivisionError:
            p_list = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
            print "divide by zero"
            
        #print p_list
            
        # === decide which direction to move ===
        #choose 1 value out of 8 values with p_list with possibility distribution
        move = np.random.choice(8, 1, p=p_list)[0]

        if move == 0:             #move to north
            self.distN -= 1
            speedCnew = speedN
        elif move == 1:           #move to south
            self.distN += 1
            speedCnew = speedS
        elif move == 2:           #move to west
            self.distW -= 1
            speedCnew = speedW
        elif move == 3:           #move to east
            self.distW += 1
            speedCnew = speedE
        elif move == 4:           #move to northwest
            self.distN -= 1
            self.distW -= 1
            speedCnew = speedNW
        elif move == 5:           #move to northeast
            self.distN -= 1
            self.distW += 1
            speedCnew = speedNE
        elif move == 6:           #move to southwest
            self.distN += 1
            self.distW -= 1
            speedCnew = speedSW
        else:                     #move to southeast
            self.distN += 1
            self.distW += 1
            speedCnew = speedSE
            
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
              ",oldspeed: ", speedC, ", newspeed: ", speedCnew, ", traveltime: ", traveltime
        
        # === update the cost map ===
        #Update the travel time/cost from initial cell to the current cell
        #which is the traveltime of traveling one cell plus the previous traveling time costC
        #Note: update only if the current cost is smaller than the previous one
        costNew = min(self.costmap.iloc[self.distN, self.distW], traveltime+costC)
        self.costaccumulated = costNew
        self.costmap.iloc[self.distN, self.distW] = costNew
        self.movecount += 1
        
        self.debugmovepathmap.iloc[self.distN, self.distW] = self.movecount
        self.travelpathlist.append((self.distN, self.distW))
        
        #print "costaccumulated: ", self.costaccumulated
        
    def outputmap(self, matrix, speedmap, travelcostmap):
   		"""Copy the header meta information from speedmap, and output travelcost/travelpath matrix to map
   		   @param: matrix is the matrix to be saved in outputfile, a .txt file.
   		"""
   		with open(speedmap, 'r') as r:
   			lines = r.readlines()
   			lines = [l for l in lines[:6]] # 6 is the number of header rows
   			with open(travelcostmap, 'w') as w:
   				w.writelines(lines)
   		matrix.to_csv(path_or_buf=travelcostmap, sep=' ', index=False, header=False, mode = 'a') # append
            
        
def main():
    RandomWalk(0,0,SPEEDMAP, TRAVELCOSTMAP, "SE") #distW, distN

if __name__ == "__main__":
    main()