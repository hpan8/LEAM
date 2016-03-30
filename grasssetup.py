#!/usr/bin/env python
import os
import sys
sys.path += ['./bin']
from glob import iglob
# import subprocess
# from subprocess import check_call

InputPath = './Data'

def grass_config(location, mapset, gisbase='/usr/local/grass-6.4.5svn', gisdbase='.'):
    """ Set grass environment to run grass.script as grass
    """
    os.environ['GISBASE'] = gisbase
    os.environ['GRASS_VERBOSE'] = '0'
    os.environ['GRASS_OVERWRITE'] = '1'
    sys.path.append(os.path.join(gisbase, 'etc', 'python'))

    global grass
    __import__('grass.script')
    grass = sys.modules['grass.script']
    from grass.script.setup import init
    gisrc = init(gisbase, gisdbase, location, mapset)    

def import_rastermap(fname):
    """Import a raster layer into GRASS
    Note that we need a PERMANENT folder in grass folder that has pre-setted projection
    information prepared before importing rastermap.
    @param filename without .gtif postfix
    """
    # proj = grass.read_command('g.proj', flags='wf')
    # with open(os.devnull, 'wb') as FNULL:
    #      check_call(['gdalwarp', '-t_srs', proj, 'Data/landcover.gtif', 'Data/landcover.gtif'], 
    #                 stdout=FNULL, stderr=subprocess.STDOUT, shell=True)

    if grass.find_file(fname)['name']:
         grass.run_command('g.remove', flags='f', rast=fname)
    if grass.run_command('r.in.gdal', input='Data/landcover.gtif', output=fname,
            overwrite=True, quiet=True):
        raise RuntimeError('unable to import rastermap ' + fname)

def main():
    grass_config('grass', 'model')

    import_rastermap('landcover')

if __name__ == "__main__":
	main()