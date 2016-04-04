#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
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

class RandomWalk():
    def __init__(self, cellx, celly, speedmap, cellsize=CELLSIZE, maxcost=MAXCOST, \
    dir="NW", dirP=DIRP, dirsideP=DIRSIDEP, diropP=DIROPP):
        """ Random Walk from one cell on a given map
        @param: cellx and celly is the curretn position x and y indexies in speedmap.
        speedmap is a matrix with speed value in each cell.
                cellsize is the length of each cell.
                maxcost is the termiantion cost from current cell doing stocastic greedy random walk.
                dirP is the probabilty that goes for a pre-selected direction.
                dirsideP is the probabilty that goes for the two directions near pre-selected direction.
                diropP is the proabiltiy taht goes for the opposite direction of pre-selected direction.
                """
        self.speedmap=speedmap
        self.cellx=cellx                           #distance to left boundary   (steps of moves)
        self.celly=celly                           #distance to top boundary    (steps of moves)
        self.distancetuple = self.speedmap.shape
        self.distright = self.distancetuple[0]-1   #distance to right boundary  (steps of moves)
        self.distbottom = self.distancetuple[1]-1  #distance to bottom boundary (steps of moves)
        self.dirP=dirP
        self.dirsideP=dirsideP
        self.diropP=diropP
        self.maxcost=maxcost
        self.cellsize=cellsize
        #pprint(self.speedmap)
        self.makeonemove()
        
        # for i in xrange(5):
        #     for j in xrange(7):
        #         print self.speedmap.iloc[i,j],
        #     print "\n",
        
    def makeonemove(self):
        distleft = self.cellx
        disttop = self.celly
        distright = self.distright
        distbottom = self.distbottom
        speedleft = speedtop = speedright = speedbottom = 0
        pleft = ptop = pright = pbottom = 0
        if (distleft!= 0):
            speedleft = self.speedmap.iloc[distleft-1, disttop]
            pleft = 1
        if (disttop!= 0):
            speedtop  = self.speedmap.iloc[distleft, disttop-1]
            ptop = 1
        if (distright!= 0):
            speedright = self.speedmap.iloc[distleft+1, disttop]
            pright = 1
        if (distbottom!= 0):
            speedbottom = self.speedmap.iloc[distleft, disttop+1]
            pbottom = 1
        
        speedsum = speedleft + speedtop + speedright + speedbottom
        p_list = [pleft*speedleft/speedsum, pright*speedtop/speedsum, ptop*speedright/speedsum, pbottom*speedbottom/speedsum]
        #choose 1 value out of 4 values with p_list as possibility distribution
        move = np.random.choice(4, 1, p=p_list)[0]
        if move == 0:             #move to left
            self.cellx -= 1
            self.distright += 1
        elif move == 1:           #move to top
            self.celly -= 1
            self.distbottom += 1
        elif move == 2:           #move to right
            self.cellx += 1
            self.distright -= 1
        else:                     #move to bottom
            self.celly += 1
            self.distbottom -= 1
        print self.cellx, self.celly, self.distright, self.distbottom
        

def main():
    speedmap = pd.read_csv(SPEEDMAP, skiprows=6, header=None, sep=r"\s+")
    RandomWalk(0,0,speedmap)
    # walk_list = np.cumsum(np.random.uniform(0, 1, (100,2)))
    # X, Y = np.transpose(walk_list)[0:2]
    # pprint(X)
    # pprint(Y)
    # pylab.figure(figsize=(8,8))
    # pylab.plot(X,Y)
    # pylab.axis('equal')
    # pylab.show()

if __name__ == "__main__":
    main()