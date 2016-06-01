import pandas as pd
import numpy as np
import time
from scipy.interpolate import griddata
from multiprocessing.dummy import Pool


"""
Time consumption: 5min
"""

# COST = -1
# NANMAX = 1
# INPUT="testmap1"
# OUTPUT="testmapout"
COST = -100
NANMAX = 3820
INPUT="./Data/attrmap-pop.txt"
HEADER="./Input/arcGISheader.txt"
OUTPUT="./Data/attrmap-pop-interpolated.txt"

def extractheader(headermap):
   with open(headermap, 'r') as h:
      header = h.read()
   return header
#global value header
header = extractheader(HEADER)

class InterpolationMatrix():
   def __init__(self, matrix, nanmax=NANMAX):
      start = time.time()
      self.interpolatedmatrix = self.interpolate2max(matrix)
      print "interpolation: ", (time.time()-start)

   def left_interpolate(self,row):
      """[reference]http://stackoverflow.com/questions/22491628/extrapolate-values-in-pandas-dataframe
      """
      size = len(row)
      print "row: ", row, 
      for i in xrange(size):
         if row[i] <= NANMAX and i > 0 and row[i-1] > NANMAX:
            row[i] = row[i-1] + COST
      print row
      return row

   def right_interpolate(self,row):
      size = len(row)
      maxi = size-1
      for i in reversed(xrange(size)):
         if row[i] <= NANMAX  and i < maxi and row[i+1] > NANMAX:
            row[i] = row[i+1] + COST
      return row

   def interpolate2max(self, matrix):
      """The interpolation is first done by going from left to right, right to left,
         going down and going up seperately. Then we overlap these four maps to obtain
         the maximum attractiveness for each cell. One last interpolation from left to right
         is done to make sure all cells have been interpolated.
      """
      left = np.copy(matrix)
      right = np.copy(left)
      up = np.transpose(np.copy(left))
      down = np.copy(up)

      #inteporlate copies
      pool = Pool(16)
      left = pool.map(self.left_interpolate, left)  
      right = pool.map(self.right_interpolate, right) 
      down = pool.map(self.left_interpolate, down)
      up = pool.map(self.right_interpolate, up)

      # overlap copies
      attrmap1 = np.maximum(left,right)
      attrmap2 = np.transpose(np.maximum(up, down))
      
      attrmap = np.maximum(attrmap1, attrmap2)
      # interpolate again
      attrmap = pool.map(self.left_interpolate, attrmap)
      return attrmap

def outputmap(attrmap, header, output):
   with open(output, 'w') as f:
      f.writelines(header)
      np.savetxt(f, attrmap, fmt='%d',delimiter=' ')



def main():
   attrmap = np.loadtxt(INPUT, delimiter=' ', skiprows=0, dtype='int')
   
   interpolation = InterpolationMatrix(attrmap)
   attrmap = interpolation.interpolatedmatrix
   
   attrmap = np.round(attrmap,0)# the output is rounded to 2 digits
   outputmap(attrmap, header, OUTPUT)

if __name__ == "__main__":
	main()
