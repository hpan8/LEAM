import sys
import pandas as pd
POPCENTERLIST = "./Data/popcenterlist.txt"
HEADER = "./Input/arcGISheader.txt"

if len(sys.argv) < 2:
    print "Error: Need an argument less than 99 as cellnum choice."
    exit(0)
cellnum = int(sys.argv[1])
if cellnum >= 100:
    print "Error: the cellnum choice should be less than 100"
    exit(0)
with open(POPCENTERLIST, 'r') as p:
	popcenterlist = p.readlines()
(cellx, celly, weight) = popcenterlist[cellnum].strip('\n').split(',')

outmap = "./Data/" + cellx + "_" + celly + ".txt"
with open(HEADER, 'r') as h:
	header = h.read()
with open(outmap, 'w') as f: 
	f.write(header)
popcentermap = pd.DataFrame(index=range(5571), columns=range(3244))
popcentermap = popcentermap.fillna(0) 
popcentermap.iloc[int(cellx), int(celly)] = 1
popcentermap.to_csv(path_or_buf=outmap, sep=' ', index=False, header=False, mode = 'a') # append