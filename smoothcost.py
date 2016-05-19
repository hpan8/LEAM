import pandas as pd
import numpy as np
from scipy.interpolate import griddata

"""
Time consumption: 5min
"""

COST = -30
NANMAX = 3820
INPUT="./Data/attrmap-noinf.txt"
HEADER="./Input/arcGISheader.txt"
OUTPUT="./Data/attrmap_interpolated.txt"

def smoothcost(costmap):
   npmap = np.array(costmap)
   print npmap
   i,j = np.unravel_index(npmap.argmin(), npmap.shape)
   print i, ",", j

def left_interpolate(row):
   """[reference]http://stackoverflow.com/questions/22491628/extrapolate-values-in-pandas-dataframe
   """
   #print row
   size = len(row)
   for i in range(size):
      if row[i] < NANMAX and i > 0 and row[i-1] > NANMAX:
         row[i] = row[i-1] + COST
   return row

def right_interpolate(row):
   size = len(row)
   maxi = size-1
   for i in reversed(range(size)):
      if row[i] < NANMAX  and i < maxi and row[i+1] > NANMAX:
         row[i] = row[i+1] + COST
   return row

def interpolate2max(attrmap):
   """The interpolation is first done by going from left to right, right to left,
      going down and going up seperately. Then we overlap these four maps to obtain
      the maximum attractiveness for each cell. One last interpolation from left to right
      is done to make sure all cells have been interpolated.
   """
   # make copies
   left = attrmap.copy()
   right = attrmap.copy()
   up = attrmap.copy()
   down = attrmap.copy()
   #inteporlate copies
   left.apply(left_interpolate, axis=1)
   right.apply(right_interpolate, axis=1)
   up.apply(left_interpolate, axis=0)
   down.apply(right_interpolate, axis=0)
   # overlap copies
   attrmap1 = np.maximum(left,right)
   attrmap2 = np.maximum(up, down)
   attrmap = np.maximum(attrmap1, attrmap2)
   # interpolate again
   attrmap.apply(left_interpolate, axis=1)
   return attrmap

def outputmap(attrmap, header):
   with open(OUTPUT, 'w') as f:
      f.writelines(header)
   attrmap.to_csv(path_or_buf=OUTPUT, sep=' ', index=False, header=False, mode='a')

def extractheader(headermap):
   with open(headermap, 'r') as h:
      header = h.read()
   return header

def main():
   attrmap = pd.read_csv(INPUT, sep=" ", skiprows=6, header=None)
   attrmap = interpolate2max(attrmap)
   header = extractheader(HEADER)
   attrmap = np.round(attrmap,2)# the output is rounded to 2 digits
   outputmap(attrmap, header)

if __name__ == "__main__":
	main()
