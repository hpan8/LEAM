#!/usr/bin/env python
import pandas as pd
import numpy as np
import math
import pprint

#select a row: df.iloc[0]
#select a column: df[0]
def centermap2indexlist(fname):
	matrix=pd.read_csv(fname, skiprows=6, header=None, sep=r"\s+") # 6 header lines
	matrixdrop = matrix.replace(-9999, np.nan)
	matrixdrop = matrixdrop.dropna(axis='index', how='all')
	matrixdrop = matrixdrop.dropna(axis='columns', how='all')
	index_list = matrixdrop.index.values.tolist()
	column_list = matrixdrop.columns.values.tolist()
	center_list = [] #triplet tuples list (index_val, column_val, value)

	for i in index_list:
		for j in column_list:
			val = matrix.iat[i,j]
			if not val == -9999:
			    center_list.append((i, j, val))
	print center_list
	print len(center_list)

	return center_list

def main():
	centermap2indexlist('./Data/toppopascii.txt')

if __name__ == "__main__":
    main()