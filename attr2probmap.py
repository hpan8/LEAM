import pandas as pd
import numpy as np

INMAP=""
OUTMAP=""
with open(speedmap, 'r') as r:
	lines = r.readlines()
	header = [l for l in lines[:6]] # 6 is the number of header rows
df = pd.read_csv(INMAP, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
npmatrix = df.as_matrix()
norm_factor = npmatrix.sum()
df = df/norm_factor
with open(ATTRACTIVEMAP, 'w') as w:
	w.writelines(header)
matrix.to_csv(path_or_buf=OUTMAP, sep=' ', index=False, header=False, mode = 'a') # append