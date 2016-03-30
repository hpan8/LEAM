#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint


# overlap two dataframes
#http://stackoverflow.com/questions/26876549/in-python-pandas-numpy-how-to-create-a-column-with-the-max-min-value-from-two
# using np.maxium

#LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landcover2006.txt'    #ascii map
#ROAD='./LU2Travel_Speed_Pan/LU2006ASCII/chrdras.txt'               #ascii map
LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landcover2006-cut.txt'
ROAD='./LU2Travel_Speed_Pan/LU2006ASCII/chrdras-cut.txt'
SPEEDCHART = "./LU2Travel_Speed_Pan/nlcd_1992+lu2travel_speed.txt"

def asciiMap2DataFrame(file):
    return pd.read_csv(file, skiprows=6, header=None, sep=r"\s+")
    
class SpeedMap:
    def __init__(self, landcover_matrix, road_matrix, speedchart):
        self.cat_list = []
        self.speed_list = []
        # read the speedchart to be a speed dictionary
        self.speedchart2dict(speedchart)
        # replace the landcover catogory values with speed values
        self.landcover_matrix = landcover_matrix
        self.landcoverspeed_matrix = self.cat2speedmap(landcover_matrix)
        self.roadspeed_matrix = self.cat2speedmap(road_matrix)
        pprint(self.landcoverspeed_matrix)
        pprint(self.roadspeed_matrix)
    
    def speedchart2dict(self, speedchart):
        with open(speedchart, 'r') as f:
            next(f) #skip the header row
            for line in f:
                (cat, speed) = line.split(',')
                speed = speed.split('\r\n')[0] #get rid of the \r\n appended to each speed
                self.cat_list.append(int(cat))
                self.speed_list.append(int(speed))
    
    def printdict(self, dict):
		for key, value in dict.iteritems():
			print str(key) + ":"+ str(value)
    
    def cat2speedmap(self, matrix):
        return matrix.replace(to_replace=self.cat_list, value=self.speed_list)
        
        
def main():
    landcover_matrix = asciiMap2DataFrame(LANDCOVER)
    road_matrix = asciiMap2DataFrame(ROAD)
    speedmap = SpeedMap(landcover_matrix, road_matrix, SPEEDCHART)
    #speedmap.printdict(speedmap.speed_dict)


if __name__ == "__main__":
	main()