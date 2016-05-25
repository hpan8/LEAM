import pandas as pd
import numpy as np

INMAP="testmap"
OUTMAP=""
HEADER="./Input/arcGISheader.txt"
with open(HEADER, 'r') as r:
	lines = r.readlines()
df = pd.read_csv(INMAP, skiprows=0, header=None, sep=r"\s+" ) #skip the 6 header lines
npmatrix = df.as_matrix()
norm_factor = npmatrix.sum()
df = df/norm_factor
print df
with open(OUTMAP, 'w') as w:
	w.writelines(header)
matrix.to_csv(path_or_buf=OUTMAP, sep=' ', index=False, header=False, mode = 'a') # append