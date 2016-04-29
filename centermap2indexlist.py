#!/usr/bin/env python
import pandas as pd
import numpy as np
import math
import pprint

POPCENTERLIST = "./Data/popcenterlist.txt"
EMPCENTERLIST = "./Data/empcenterlist.txt"

#select a row: df.iloc[0]
#select a column: df[0]
def centermap2indexlist(fname):
    matrix=pd.read_csv(fname, skiprows=6, header=None, sep=r"\s+") # 6 header lines
    matrixdrop = matrix.replace('*', np.nan)
    matrixdrop = matrixdrop.dropna(axis='index', how='all')
    matrixdrop = matrixdrop.dropna(axis='columns', how='all')
    index_list = matrixdrop.index.values.tolist()
    column_list = matrixdrop.columns.values.tolist()
    center_list = [] #triplet tuples list (index_val, column_val, value)

    for i in index_list:
        for j in column_list:
            val = matrix.iat[i,j]
            if not val == '*':
                center_list.append((i, j, val))
    dtype = [('cellx', int), ('celly', int), ('value', int)]
    center_nplist = np.array(center_list, dtype=dtype)
    center_sortedlist = np.sort(center_nplist, kind='mergesort', order='value')
    print len(center_sortedlist)
    startof100cells = len(center_sortedlist)-100
    center_sorted100list = center_sortedlist[startof100cells:]
    print center_sorted100list
    return center_sorted100list

def main():
    popcenter_list = centermap2indexlist('./Data/pop_center.txt')
    empcenter_list = centermap2indexlist('./Data/emp_centers5.txt')
    with open(POPCENTERLIST, 'w') as p:
        for x, y, val in popcenter_list:
            p.write("%i,%i,%i\n" % (x,y,val))
    with open(EMPCENTERLIST, 'w') as e:
        for x, y, val in empcenter_list:
            e.write("%i,%i,%i\n" % (x,y,val))

if __name__ == "__main__":
    main()