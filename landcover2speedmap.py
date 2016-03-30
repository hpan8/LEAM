#!/usr/bin/env python
import os
import sys
sys.path += ['./bin']
import re
import csv
import subprocess
from glob import iglob
from subprocess import check_call
from grasssetup import grass_config
from grasssetup import import_rastermap

LANDCOVER='./LU2Travel_Speed_Pan/LU2006ASCII/landcover2006.txt'
SPEEDCHART = "./LU2Travel_Speed_Pan/nlcd_1992+lu2travel_speed.txt"

class SpeedMap:

	def __init__(self, landcover, speedchart):
		self.landcovermap = landcover
		self.speed_dict = {}
		self.speedchart2dict(speedchart)
		self.landcover2speedmap(landcover)

	def speedchart2dict(self, speedchart):
		with open(speedchart, 'r') as f:
			next(f) #skip the header row
			for line in f:
				(cat, speed) = line.split(',')
				self.speed_dict[cat] = speed

	def printdict(self, dict):
		for key, value in dict.iteritems():
			print str(key) + ":"+ str(value)

	def landcover2speedmap(self, landcover):
		with open(landcover, 'r') as f:
			inmatrix = [map(int, line.split()) for line in f.readlines()[6:]]
			modification = 0
			for line in inmatrix:
				for cat in line:
					modification = 1
				if modification:
					print line


def main():
    grass_config('grass', 'model')
    #import_rastermap('landcover')
    speedmap = SpeedMap(LANDCOVER, SPEEDCHART)
    #speedmap.printdict(speedmap.speed_dict)


if __name__ == "__main__":
	main()