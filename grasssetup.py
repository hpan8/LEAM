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
    infilename = './Input/' + fname + '.tif'
    if grass.run_command('r.in.gdal', input=infilename, output=fname,
            overwrite=True, quiet=True):
        raise RuntimeError('unable to import rastermap ' + fname)

    if grass.run_command('r.info', map=fname):
        raise RuntimeError('unable to print region info ' + fname)

def import_vectormap(layername):
    """Import a vector layer into GRASS. The reion is set to the vector map with 30 meters resolution.
       @param: layername is the input vector files folder and also the imported layer name.
    """
    # remove prior exisiting raster and vector layers
    if grass.run_command('g.remove', rast=layername, vect=layername):
        raise RuntimeError('unable to clear prior raster and vector file: ' + layername)

    # set the region to fit the current vector file with 30 meters resotluion
    if grass.run_command('g.region', flags='d', res=30):
        raise RuntimeError('unable to set region ')

    pathname = './Input/' + layername

    # import vector map
    if grass.run_command('v.in.ogr', flags='o', dsn=pathname,
            snap='0.01', output=layername, overwrite=True, quiet=True):
        raise RuntimeError('unable to import vectormap ' + layername)

    # print vector map data column names
    if grass.run_command('v.db.connect', map=layername, flags='c'):
        raise RuntimeError('unable to print info of vectormap ' + layername)

def vector2rasterpop1000(layername):
    """Transform  the TOTAL_POP column value that is larger than 1000 in the vector layer to raster layer.
       @param: layername is the vector layer to be transformed to the raster form of this layer.
       Note that it is required to have "TOTAL_POP" column in the vector file.
       //TODO: allow user to select which column name to select from vector map.
    """
    layer1000 = layername + "1000"
    if grass.run_command('v.extract', input=layername, output=layer1000, overwrite=True,
        where='TOTAL_POP>=1000'):
        raise RuntimeError('unable to convert vector to raster: ' + layername)
    if grass.run_command('v.to.rast', input=layer1000, output=layername, overwrite=True,
        use='attr', column='TOTAL_POP'):
        raise RuntimeError('unable to convert vector to raster: ' + layername)

def vector2rasterspeed(layername):
    """Transform  the TOTAL_POP column value that is larger than 1000 in the vector layer to raster layer.
       @param: layername is the vector layer to be transformed to the raster form of this layer.
       Note that it is required to have "TOTAL_POP" column in the vector file.
       //TODO: allow user to select which column name to select from vector map.
    """
    if grass.run_command('v.to.rast', input=layername, output=layername, overwrite=True,
        use='attr', column='SPEED'):
        raise RuntimeError('unable to convert vector to raster: ' + layername)

def export_asciimapnull1(layername):
    """Export a raster layer into asciimap. The output folder is 'Data/'.
       @param: layername is the raster layer name.
    """
    outfilename = 'Data/'+layername+'.txt'
    if grass.run_command('r.out.ascii', input=layername, output=outfilename, null=1):
        raise RuntimeError('unable to export ascii map ' + layername)
    # outfilename = 'Data/'+layername+'.tiff'
    # if grass.run_command('r.out.tiff', input=layername, output=outfilename):
    #     raise RuntimeError('unable to export tiff map ' + layername)    

def main():
    grass_config('grass', 'model')

    LANDUSEMAP = 'landuse'
    ROADMAP = 'chicago_road2'
    POPCENTERMAP = 'pop_center'
    EMPCENTERMAP = 'emp_centers5'

    #transform raster landuse to ascii map
    # import_rastermap(LANDUSEMAP)
    # export_asciimap(LANDUSEMAP)

    #transform vector road map to ascii map
    import_vectormap(ROADMAP)
    vector2rasterspeed(ROADMAP)
    export_asciimapnull1(ROADMAP)

    # # transform population centers vector files to ascii map with 2010 population data.
    # import_vectormap(POPCENTERMAP)
    # vector2rasterpop1000(POPCENTERMAP)
    # export_asciimap(POPCENTERMAP)

    # # transform employment centers vector files to ascii map with 2010 population data.
    # import_vectormap(EMPCENTERMAP)
    # vector2rasterpop1000(EMPCENTERMAP)
    # export_asciimap(EMPCENTERMAP)

if __name__ == "__main__":
	main()