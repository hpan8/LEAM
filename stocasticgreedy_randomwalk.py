#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
import math
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint
#import pylab

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

DEBUG = 1
if DEBUG == 1:
	SPEEDMAP = "./Data/speedmaptest.txt"
else:
	SPEEDMAP = "./Data/speedmap.txt"

CELLSIZE = 30 #meters
MAXCOST = 120 #minutes
DIRP = 0.5						#possibility to go to pre-selected direction
DIROPP = 0.1 					#possibility to go to the opposite direction of pre-selected direction
DIRSIDEP = 1-(DIRP-DIROPP)/2    #possibility to go to the other two directions

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
    def __init__(self, cellx, celly, speedmap, cellsize=CELLSIZE, maxcost=MAXCOST, \
    dir="NW", dirP=DIRP, dirsideP=DIRSIDEP, diropP=DIROPP):
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
        self.speedmap=speedmap
        self.cellx=cellx                           #initial starting cell x index
        self.celly=celly                           #initial starting cell y index
        self.distW = cellx                         #current cell x index
        self.distN = celly                         #current cell y index
        self.distancetuple = self.speedmap.shape
        self.indexlen = self.distancetuple[1]
        self.columnlen = self.distancetuple[0]
        self.dirP=dirP
        self.dirsideP=dirsideP
        self.diropP=diropP
        self.maxcost=maxcost
        self.cellsize=cellsize
        ####################
        self.costmap = pd.DataFrame(index=range(self.indexlen), columns=range(self.columnlen)) #initialize costmap with nan
        self.makeonemove()

    def makeonemove(self):
        # === fetch current cell data ===
        distN = self.distN                         #distance to top boundary   (steps of moves)
        distS = self.indexlen-1                    #distance to right boundary  (steps of moves)
        distW = self.distW                         #distance to left boundary   (steps of moves) 
        distE = self.columnlen-1                   #distance to bottom boundary (steps of moves)
        
        #print distW, distN, distE, distS
        
        # if not meet the boundary, assign the speed in speed map,
        # and assign speed to be 0 otherwise.
        speedW = speedN = speedE = speedS = 0
        speedNW = speedNE = speedSW = speedSE = 0
        speedC = self.speedmap.iloc[distW, distN]
        if distN != 0:
            speedN = self.speedmap.iloc[distW-1, distN]
        if distS != 0: 
            speedS = self.speedmap.iloc[distW+1, distN]
        if distW != 0: 
            speedW = self.speedmap.iloc[distW, distN-1]
        if distE != 0: 
            speedE = self.speedmap.iloc[distW, distN+1]
            
        if distN != 0 and distW != 0: 
            speedNW = self.speedmap.iloc[distW-1, distN-1]
        if distN != 0 and distE != 0:
            speedNE = self.speedmap.iloc[distW-1, distN+1]
        if distS != 0 and distW != 0:
            speedSW = self.speedmap.iloc[distW+1, distN-1]
        if distS != 0 and distE != 0:  
            speedSE = self.speedmap.iloc[distW+1, distN+1]
             
        #print speedN, speedS, speedW, speedE, speedNW, speedNE, speedSW, speedSE, speedC
        
        # === caculate probability list ===
        #speedsum will never be 0
        speedsum = (speedN + speedS + speedW + speedE + speedNW + speedNE + speedSW + speedSE)*1.0
        
        #p_list is the possiblity list to go which direction from current cell
        try:
            p_list = [speedN/speedsum,  speedS/speedsum,  speedW/speedsum,  speedE/speedsum, \
                      speedNW/speedsum, speedNE/speedsum, speedSW/speedsum, speedSE/speedsum]
        except ZeroDivisionError:
            p_list = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
            print "divide by zero"
            
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
            
        #print move, self.distW, self.distN, speedC, speedCnew, traveltime
        
        # === update the cost map ===
        #update the travel time/cost from initial cell to current cell ()
        #only if the current cost is smaller than the previous one
        self.costmap.iloc[self.distW, self.distN] = min(self.costmap.iloc[distW, distN], traveltime)

def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    RandomWalk(1,1,speedmap)

if __name__ == "__main__":
    main()