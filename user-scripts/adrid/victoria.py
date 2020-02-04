import time
import fiona
import multiprocessing
from rasterio.plot import show
import math
import os
import click
#import matlibplot.pyplot as plt
import numpy as np
import numpy.ma as ma
import rasterio
from rasterio.plot import show, show_hist
import pandas

from projections.rasterset import RasterSet, Raster
from projections.simpleexpr import SimpleExpr
import projections.predicts as predicts
import projections.r2py.modelr as modelr
import projections.utils as utils

years = [2049,2100]

for year in years:

    print(year)

    # Read in the model
    mod = modelr.load('D:/victoria_projections/ab_model.rds')
    predicts.predictify(mod)
    
    rasters = predicts.rasterset('luh2', 'ssp1_rcp2.6_image', year, hpd_trend='wpp')
    #rasters = predicts.rasterset('luh2', 'ssp5_rcp8.5_remind-magpie', year, hpd_trend='wpp')
    
    # set soil properties to 0
    rasters['BD'] = SimpleExpr('BD', 0)
    rasters['CLAY'] = SimpleExpr('CLAY', 0)
    rasters['OC'] = SimpleExpr('OC', 0)
    rasters['phkcl'] = SimpleExpr('phkcl', 0)

    #note that rasters.keys() shows you all the names of the rasters in this object
    rasters['secondary_vegetation_minimal'] = SimpleExpr('secondary_vegetation_minimal', 'young_secondary_minimal + intermediate_secondary_minimal + mature_secondary_minimal')
    rasters['secondary_vegetation_light'] = SimpleExpr('secondary_vegetation_light', 'young_secondary_light + intermediate_secondary_light + mature_secondary_light')
    rasters['secondary_vegetation_intense'] = SimpleExpr('secondary_vegetation_intense', 'young_secondary_intense + intermediate_secondary_intense + mature_secondary_intense')

    rasters['primary_vegetation_intense'] = SimpleExpr('primary_vegetation_intense', 'primary_intense')
    rasters['primary_vegetation_light'] = SimpleExpr('primary_vegetation_light', 'primary_light')
    
    rasters['plantation_pri'] = SimpleExpr('plantation_pri', 'perennial + timber')
    rasters['plantation_pri_intense'] = SimpleExpr('plantation_pri_intense', 'perennial_intense + timber_intense')
    rasters['plantation_pri_light'] = SimpleExpr('plantation_pri_light', 'perennial_light + timber_light')
    rasters['plantation_pri_minimal'] = SimpleExpr('plantation_pri_minimal', 'perennial_minimal + timber_minimal')
    
    rs = RasterSet(rasters)

    # back transform (they were transformed using log(x+1)
    rs[mod.output] = mod
    rs['output'] = SimpleExpr('output', '(exp(%s) / exp(%f))' % (mod.output, mod.intercept))
    rs.write('output', 'D:/victoria_projections/ssp2.6/ab-%d.tif' % year)

for year in years:

    print(year)

    # Read in the model
    mod = modelr.load('D:/victoria_projections/ab_model.rds')
    predicts.predictify(mod)
    
    rasters = predicts.rasterset('luh2', 'ssp5_rcp8.5_remind-magpie', year, hpd_trend='wpp')
    
    # set soil properties to 0
    rasters['BD'] = SimpleExpr('BD', 0)
    rasters['CLAY'] = SimpleExpr('CLAY', 0)
    rasters['OC'] = SimpleExpr('OC', 0)
    rasters['phkcl'] = SimpleExpr('phkcl', 0)

    #note that rasters.keys() shows you all the names of the rasters in this object
    rasters['secondary_vegetation_minimal'] = SimpleExpr('secondary_vegetation_minimal', 'young_secondary_minimal + intermediate_secondary_minimal + mature_secondary_minimal')
    rasters['secondary_vegetation_light'] = SimpleExpr('secondary_vegetation_light', 'young_secondary_light + intermediate_secondary_light + mature_secondary_light')
    rasters['secondary_vegetation_intense'] = SimpleExpr('secondary_vegetation_intense', 'young_secondary_intense + intermediate_secondary_intense + mature_secondary_intense')

    rasters['primary_vegetation_intense'] = SimpleExpr('primary_vegetation_intense', 'primary_intense')
    rasters['primary_vegetation_light'] = SimpleExpr('primary_vegetation_light', 'primary_light')
    
    rasters['plantation_pri'] = SimpleExpr('plantation_pri', 'perennial + timber')
    rasters['plantation_pri_intense'] = SimpleExpr('plantation_pri_intense', 'perennial_intense + timber_intense')
    rasters['plantation_pri_light'] = SimpleExpr('plantation_pri_light', 'perennial_light + timber_light')
    rasters['plantation_pri_minimal'] = SimpleExpr('plantation_pri_minimal', 'perennial_minimal + timber_minimal')
    
    rs = RasterSet(rasters)

    # back transform (they were transformed using log(x+1)
    rs[mod.output] = mod        
    rs['output'] = SimpleExpr('output', '(exp(%s) / exp(%f))' % (mod.output, mod.intercept))
    rs.write('output', 'D:/victoria_projections/ssp5/ab-%d.tif' % year)


years = [2014]

for year in years:

    print(year)

    # Read in the model
    mod = modelr.load('D:/victoria_projections/ab_model.rds')
    predicts.predictify(mod)
    
    rasters = predicts.rasterset('luh2', 'historical', year, hpd_trend='wpp')
    
    # set soil properties to 0
    rasters['BD'] = SimpleExpr('BD', 0)
    rasters['CLAY'] = SimpleExpr('CLAY', 0)
    rasters['OC'] = SimpleExpr('OC', 0)
    rasters['phkcl'] = SimpleExpr('phkcl', 0)

    #note that rasters.keys() shows you all the names of the rasters in this object
    rasters['secondary_vegetation_minimal'] = SimpleExpr('secondary_vegetation_minimal', 'young_secondary_minimal + intermediate_secondary_minimal + mature_secondary_minimal')
    rasters['secondary_vegetation_light'] = SimpleExpr('secondary_vegetation_light', 'young_secondary_light + intermediate_secondary_light + mature_secondary_light')
    rasters['secondary_vegetation_intense'] = SimpleExpr('secondary_vegetation_intense', 'young_secondary_intense + intermediate_secondary_intense + mature_secondary_intense')

    rasters['primary_vegetation_intense'] = SimpleExpr('primary_vegetation_intense', 'primary_intense')
    rasters['primary_vegetation_light'] = SimpleExpr('primary_vegetation_light', 'primary_light')
    
    rasters['plantation_pri'] = SimpleExpr('plantation_pri', 'perennial + timber')
    rasters['plantation_pri_intense'] = SimpleExpr('plantation_pri_intense', 'perennial_intense + timber_intense')
    rasters['plantation_pri_light'] = SimpleExpr('plantation_pri_light', 'perennial_light + timber_light')
    rasters['plantation_pri_minimal'] = SimpleExpr('plantation_pri_minimal', 'perennial_minimal + timber_minimal')
    
    rs = RasterSet(rasters)

    # back transform (they were transformed using log(x+1)
    rs[mod.output] = mod        
    rs['output'] = SimpleExpr('output', '(exp(%s) / exp(%f))' % (mod.output, mod.intercept))
    rs.write('output', 'D:/victoria_projections/historical/ab-%d.tif' % year)

