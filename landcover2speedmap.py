#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint


# overlap two dataframes
#http://stackoverflow.com/questions/26876549/in-python-pandas-numpy-how-to-create-a-column-with-the-max-min-value-from-two
# using np.maxium

#LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landcover2006.txt'    #ascii map
#ROAD='./LU2Travel_Speed_Pan/LU2006ASCII/chrdras.txt'               #ascii map
LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landcover2006-cut.txt'
ROAD='./LU2Travel_Speed_Pan/LU2006ASCII/chrdras-cut.txt'
# LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landtest.txt'
# ROAD='./LU2Travel_Speed_Pan/LU2006ASCII/roadtest.txt'
SPEEDCHART="./LU2Travel_Speed_Pan/nlcd_1992+lu2travel_speed.txt"
SPEEDMAP="./Data/speedmap.txt"

def asciiMap2DataFrame(file):
    return pd.read_csv(file, skiprows=6, header=None, sep=r"\s+")
    
class SpeedMap:
    def __init__(self, landcover_matrix, road_matrix, speedchart):
        self.cat_list = []
        self.speed_list = []
        self.projectioninfo_list = []
        # read the speedchart to be a speed dictionary
        self.speedchart2dict(speedchart)
        # replace the landcover catogory values with speed values
        self.landcover_matrix = landcover_matrix
        self.landcoverspeed_matrix = self.cat2speedmap(landcover_matrix)
        self.roadspeed_matrix = self.cat2speedmap(road_matrix)
        self.finalspeed_matrix = self.overlapspeedmap(self.landcoverspeed_matrix, self.roadspeed_matrix)

        self.outputspeedmap(self.finalspeed_matrix, SPEEDMAP)
        # pprint(self.landcoverspeed_matrix)
        # pprint(self.roadspeed_matrix)
        # pprint(self.finalspeed_matrix)
    
    def speedchart2dict(self, speedchart):
    	"""Read the speedchart text file and convert it to be a catogory list and its corresponding
    	   speed list.
    	   @param: speedchart txt file with one header row, two columns: catgory values and speed values
    	"""
        with open(speedchart, 'r') as f:
            next(f) #skip the header row
            for line in f:
                (cat, speed) = line.split(',')
                #get rid of the \r\n appended to each speed
                speed = speed.split('\r\n')[0] 
                self.cat_list.append(int(cat))
                self.speed_list.append(int(speed))
        # if catgory is not defined , the speed is 0
        self.cat_list.append(None) 
        self.speed_list.append(0)
    
    def cat2speedmap(self, matrix):
    	"""Replace the catgory values not in the matrix to be None, and then replace
    	   all the catgory values with their corresponding speed value according to the
    	   provided speedchart. If the catgory is None, replace the speed with 0.
    	   @param: matrix is the input map with all catgory values
    	   @output: matrix that has speed values corresponding to the input catgory values.
    	"""
    	matrix =  matrix.where(matrix.isin(self.cat_list) == True, None)
        return matrix.replace(to_replace=self.cat_list, value=self.speed_list)

    def overlapspeedmap(self, matrix1, matrix2):
    	"""Overlap two speed maps by selecting the max value in either of the map.
    	   @param: matrix1 and matrix2 are two maps to be overlapped.
    	   @output: the max values of two matrixes.
    	"""
    	return np.maximum(matrix1, matrix2)

    def outputspeedmap(self, matrix, speedmap):
   		"""Copy the header meta information from Landcover map, and output speed matrix to speedmap
   		   @param: matrix is the matrix to be saved in speedmap txt file.
   		"""
   		with open(LANDCOVER, 'r') as r:
   			lines = r.readlines()
   			lines = [l for l in lines[:6]] # 6 is the number of header rows
   			with open(speedmap, 'w') as w:
   				w.writelines(lines)
   		matrix.to_csv(path_or_buf=speedmap, sep=' ', index=False, header=False, mode = 'a') # append

    def printdict(self, dict):
		for key, value in dict.iteritems():
			print str(key) + ":"+ str(value)
        
        
def main():
    landcover_matrix = asciiMap2DataFrame(LANDCOVER)
    road_matrix = asciiMap2DataFrame(ROAD)
    speedmap = SpeedMap(landcover_matrix, road_matrix, SPEEDCHART)


if __name__ == "__main__":
	main()