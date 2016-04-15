#!/usr/bin/env python
from StringIO import StringIO
import numpy as np
import pandas as pd
import math
from numpy import maximum
from pandas import (Series,DataFrame, Panel,)
from pprint import pprint

"""
This script will do:
1) overlap thousands of maps
"""

def getmincostfrom2maps(map1,map2):
	return np.minimum(map1, map2)


def main():
    map1 = pd.read_csv("./Data/speedmap1.txt", skiprows=6, header=None, sep=r"\s+")
    map2 = pd.read_csv("./Data/speedmap2.txt", skiprows=6, header=None, sep=r"\s+")
    map12 = getmincostfrom2maps(map1, map2)
    pprint(map12)

if __name__ == "__main__":
    main()