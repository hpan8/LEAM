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

# def setregion(n, s, w, e): #doesn' work
#     if grass.run_command('g.region', n=n, s=s, w=w, e=e, res=30):
#         raise RuntimeError('unable to set region info ')

def import_rastermap(pathname, fname):
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
    infilename = pathname + fname + '.gtif'
    if grass.run_command('r.in.gdal', input=infilename, output=fname,
            overwrite=True, quiet=True):
        raise RuntimeError('unable to import rastermap ' + fname)

    if grass.run_command('r.info', map=fname):
        raise RuntimeError('unable to print region info ' + fname)

# def import_vectormap(pathname, fname, layer=''):
#     """Import a vector layer into GRASS.
#     Note that we need a PERMANENT folder in grass folder that has pre-setted projection
#     information prepared before importing vectormap - shapefile.
#     """
#     if grass.find_file(fname)['name']:
#         grass.run_command('g.remove', flags='f', rast=fname)
#     infilename = pathname + fname + '.shp'

#     # remove temporary previously projected shape files
#     for f in iglob('proj.*'):
#         os.remove(f)

#     proj = grass.read_command('g.proj', flags='wf')

#     check_call(['ogr2ogr', '-t_srs', proj, 'proj.shp', fname])
#     clean_fields('proj.shp')

#     if grass.run_command('v.in.ogr', flags='w', dsn='proj.shp',
#            snap='0.01', output=fname, overwrite=True, quiet=True):
#         raise RuntimeError('unable to import vectormap ' + fname)
#     # if grass.run_command('v.in.ogr', input=infilename, output=fname, 
#     #         overwrite=True, quiet=True):
#     #     raise RuntimeError('unable to import vectormap ' + fname)
#     for f in iglob('proj.*'):
#         os.remove(f)

#     if grass.run_command('r.info', flags='g'):
#         raise RuntimeError('unable to print region info ' + fname)

def printregioninfo():
    if grass.run_command('g.region', flags='p'):
        raise RuntimeError('unable to print region info')

def export_asciimap(layername):
    """Export a raster layer into asciimap
    """
    outfilename = 'Data/'+layername+'.txt'
    if grass.run_command('r.out.ascii', input=layername, output=outfilename):
        raise RuntimeError('unable to export ascii map ' + fname)

def main():
    grass_config('grass', 'model')

    #import_rastermap('Data/','landcover')
    #import_vectormap('Data/Population','Top100Pop')
    #printregioninfo()

if __name__ == "__main__":
	main()