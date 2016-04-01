#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint
import pylab

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
		self.cellx=cellx
		self.celly=celly
		self.speedmap=speedmap
		self.dirP=dirP
		self.dirsideP=dirsideP
		self.diropP=diropP
		self.maxcost=maxcost
		self.cellsize=cellsize




def main():
	RandomWalk(0,0,SPEEDMAP)
	walk_list = np.cumsum(np.random.uniform(0, 1, (100,2)))
	X, Y = np.transpose(walk_list)[0:2]
	pprint(X)
	pprint(Y)
	pylab.figure(figsize=(8,8))
	pylab.plot(X,Y)
	pylab.axis('equal')
	pylab.show()

if __name__ == "__main__":
	main()