import pandas as pd
import numpy as np
import time
from scipy.interpolate import griddata
from multiprocessing.dummy import Pool


"""
Time consumption: 5min
"""

COST = -0.3
NANMAX = 0.3
INPUT="testmap"
OUTPUT="testmapout"
#COST = -100
#NANMAX = 3820
#INPUT="./Data/attrmap-pop.txt"
HEADER="./Input/arcGISheader.txt"
#OUTPUT="./Data/attrmap-pop-interpolated.txt"

def extractheader(headermap):
   with open(headermap, 'r') as h:
      header = h.read()
   return header
#global value header
header = extractheader(HEADER)

class InterpolationMatrix():
   def __init__(self, matrix, nanmax=NANMAX):
      self.matrix = matrix
      start = time.time()
      self.array = np.asarray(matrix)
      print "asarray: ", (time.time()-start)
      self.interpolatedmatrix = self.interpolate2max()
      print "interpolation: ", (time.time()-start)

   def left_interpolate(self,row):
      """[reference]http://stackoverflow.com/questions/22491628/extrapolate-values-in-pandas-dataframe
      """
      size = len(row)
      newrow = []
      for i in xrange(1, size):
         if row[i] < NANMAX and i > 0 and row[i-1] > NANMAX:
            newrow.append(row[i-1] + COST)
         else:
            newrow.append(row[i])
      return newrow

   def right_interpolate(self,row):
      size = len(row)
      maxi = size-1
      newrow = []
      for i in reversed(xrange(0, size-1)):
         if row[i] < NANMAX  and i < maxi and row[i+1] > NANMAX:
            newrow.append(row[i+1] + COST)
         else:
            newrow.append(row[i+1])
      return newrow

   def interpolate2max(self):
      """The interpolation is first done by going from left to right, right to left,
         going down and going up seperately. Then we overlap these four maps to obtain
         the maximum attractiveness for each cell. One last interpolation from left to right
         is done to make sure all cells have been interpolated.
      """
      left = self.matrix.copy()
      right = self.matrix.copy()
      up = self.matrix.copy()
      down = self.matrix.copy()

      #inteporlate copies
      pool = Pool(4)
      left = pool.map(self.left_interpolate, zip(*np.asarray(left)))  # zip(*self.array)[0] is the 0th row
      right = pool.map(self.right_interpolate, zip(*np.asarray(right))) 
      #up = pool.map(self.left_interpolate, up)                        # up[0] is the 0th column
      #down = pool.map(self.right_interpolate, down)

      # overlap copies
      attrmap1 = np.maximum(left,right)
      #attrmap2 = np.maximum(up, down)
      #attrmap = np.maximum(attrmap1, attrmap2)
      # interpolate again
      attrmap = pool.map(self.left_interpolate, attrmap1)
      return attrmap

def outputmap(attrmap, header, output):
   with open(output, 'w') as f:
      f.writelines(header)
   attrmap.to_csv(path_or_buf=output, sep=' ', index=False, header=False, mode='a')



def main():
   attrmap = pd.read_csv(INPUT, sep=" ", skiprows=0, header=None)
   
   interpolation = InterpolationMatrix(attrmap)
   attrmap = interpolation.interpolatedmatrix
   
   attrmap = np.round(attrmap,2)# the output is rounded to 2 digits
   print attrmap
   #outputmap(attrmap, header, OUTPUT)

if __name__ == "__main__":
	main()
