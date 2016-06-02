import pandas as pd
import numpy as np
import time
from scipy.interpolate import griddata
from multiprocessing.dummy import Pool

"""
Time consumption for 64 threads and 1 repeattime: 12min
Time consumption for 64 threads and 2 repeattime: 24min
"""

#INPUT="testmap1"
#OUTPUT="testmapout"
INPUT="./Data/attrmap-pop.txt"
OUTPUT="./Data/attrmap-pop-interpolated.txt"
HEADER="./Input/arcGISheader.txt"
WEIGHTMAP = "./Input/weightmap.txt"
DIRPROBMAP = "./Data/dirprobmap.txt"
DIRPROBMAX = 200
THREADNUM = 64
REPEATNUM = 1


def extractheader(headermap):
	with open(headermap, 'r') as h:
		header = h.read()
	return header
#global value header
header = extractheader(HEADER)

class SmoothCost():
	def __init__(self, matrix, weightarray, dirprobmatrix, repeattimes=REPEATNUM, dirprobmax=DIRPROBMAX):
		start = time.time()
		self.weightarray = weightarray
			self.matrix = matrix
			(self.rows, self.cols) = matrix.shape
			self.maxrow = self.rows-2
			self.maxcol = self.cols-2
			self.dirprobmatrix = dirprobmatrix
			self.dirprobmax = dirprobmax
			self.smoothedmap = np.zeros((self.rows, self.cols), dtype=np.int)
			#self.smooth2max(repeattimes)

	 def smoothrow(self, rowidx):
			"""This function assigns the center of 5*5 cells a value that equals to the sum of all cells having larger values multiplying by
				 a weight. The weight is read from the input weightmap and has a value propotional to the distance to the center cell. Repeat 
				 the steps for all cells of the row with rowidx in the attrmap matrix.
				 @param: rowidx is the row index of the attrmap matrix.
				 @output: the smoothedmap filled with row index of rowidx.
			"""
			if rowidx < 2 or rowidx >= self.maxrow:
				 return
			#debug: print "rowidx: ", rowidx , "==========="
			for colidx in xrange(2, self.maxcol): # for each cell in a row
				midval = self.matrix[rowidx][colidx]
				#debug: print "colidx: ", colidx, "-----------"
				#debug: print "midval: ", midval
				nearsum = 0
				weightsum = 0
				index = 0
				for i in xrange(rowidx-2, rowidx+3):    # for each row of the 25 cells
					for j in xrange(colidx-2, colidx+3): # for each cell of the 25 cells
					    curval = self.matrix[i][j]
						if midval < curval:
							curweight = self.weightarray[index]
							nearsum += curval*curweight
							weightsum += curweight
						index += 1
				#debug: print nearsum, " ", weightsum
				if weightsum == 0:
					self.smoothedmap[rowidx][colidx] = 0
				else:
					curlandtypeweight = min(self.dirprobmatrix[rowidx][colidx], self.dirprobmax)
					newval = nearsum/weightsum
					self.smoothedmap[rowidx][colidx] = (newval-midval)*curlandtypeweight/self.dirprobmax + midval

	 def smooth2max(self, repeattimes):
			"""smooth2max creates THREADNUM number of threads to parallell smoothing each row of the attrmap matrix.
				 As the two side columns and rows are not smoothed in the attrmap, overlay the original map and smoothedmap
				 can obtain the original attrativenesss score for the side columns and rows. Also, cells that decreases its
				 values due to rounding to int can have the original higher values back.
			"""
			for i in xrange(repeattimes):
				pool = Pool(THREADNUM)
				pool.map(self.smoothrow, xrange(self.rows))
			
				#debug:
				#for rowidx in xrange(self.rows):
				#   self.smoothrow(rowidx)
				self.matrix = np.maximum(self.smoothedmap, self.matrix)
			self.smoothedmap = self.matrix

def outputmap(attrmap, header, output):
	with open(output, 'w') as f:
		f.writelines(header)
		np.savetxt(f, attrmap, fmt='%d',delimiter=' ')

def main():
	attrmap_df = pd.read_csv(INPUT, sep=' ', skiprows=6, header=None, dtype=np.float)
	attrmap = np.asarray(attrmap_df).round
	weightarray = np.fromfile(WEIGHTMAP, sep=' ', dtype=np.int)
	dirprob_df = pd.read_csv(DIRPROBMAP, sep=' ', skiprows=6, header=None, dtype=np.int)

	smoothcost = SmoothCost(attrmap, weightarray, dirprob_df)
	attrmap = smoothcost.smoothedmap
	outputmap(attrmap, header, OUTPUT)

if __name__ == "__main__":
	main()
