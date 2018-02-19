#!/usr/bin/env python

import itertools
import multiprocessing
import os
import sys
import time

import click
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import rasterio
from rasterio.plot import show

from projections.rasterset import RasterSet
from projections.simpleexpr import SimpleExpr
import projections.r2py.modelr as modelr
import projections.predicts as predicts
import projections.utils as utils

class YearRangeParamType(click.ParamType):
  name = 'year range'

  def convert(self, value, param, ctx):
    try:
      try:
        return [int(value)]
      except ValueError:
        low, high = value.split(':')
        return range(int(low), int(high))
    except ValueError:
      self.fail('%s is not a valid year range' % value, param, ctx)

YEAR_RANGE = YearRangeParamType()

def select_models(model, model_dir):
  """Select the appropriate models for abundance, spieces richness, or
compositional similarity depending on what the user wants to project.

  Assumes models have fixed name and live in the folder passed as a
  parameter.

  """

  if model == 'ab':
    mods = ('ab-model.rds', )
    out = 'Abundance'
  elif model == 'sr':
    mods = ('sr-model.rds', )
    out = 'Richness'
  elif model == 'cs-ab':
    mods = ('cs-ab-model.rds', )
    out = 'CompSimAb'
  elif model == 'cs-sr':
    mods = ('cs-sr-model.rds', )
    out = 'CompSimSR'
  else:
    raise RuntimeError('Unknown model type %s' % model)
  return out, tuple(map(lambda x: os.path.join(model_dir, x), mods))

def var_to_fname(vname, scenario, year):
   # Here you would translate from the variable name to the name of the
   # raster map to use.  For this example I always return the same
   # file name
   convert_dictionnary_PREDICT2NLU={'SSP_UIAnnual_Intense_use':'ann_intense',
                                    'SSP_UIAnnual_Light_use':'ann_light',
                                    'SSP_UIAnnual_Minimal_use':'ann_minimum',
                                    'SSP_UIManaged_pasture_Intense_use':'past_intense',
                                    'SSP_UIManaged_pasture_Light_use':'past_light',
                                    'SSP_UINitrogen_Intense_use':'c3nfx_intense',
                                    'SSP_UINitrogen_Light_use':'c3nfx_light',
                                    'SSP_UINitrogen_Minimal_use':'c3nfx_minimum',
                                    'SSP_UIPerennial_Intense_use':'per_intense',
                                    'SSP_UIPerennial_Light_use':'per_light',
                                    'SSP_UIPerennial_Minimal_use':'per_minimum',
                                    'SSP_UIRangelands_':'range',
                                    'SSP_UISecondary_':'non_agri',
                                    'SSP_UISecondary':'non_agri',
                                    'SSP_UIUrban_Intense_use':'urban_intense',
                                    'SSP_UIUrban_Light_use':'urban_light',
                                    'SSP_UIUrban_Minimal_use':'urban_minimum'
                                        }
   return '../../data/nlu/'+str(scenario)+'/PREDICT_map_'+str(scenario)+'_'+str(year)+'_'+str(convert_dictionnary_PREDICT2NLU[vname])+'.nc'

def PREDICT2NLU_name(vname):
   # Here you would translate from the variable name to the name of the
   # raster map to use.  For this example I always return the same
   # file name
   convert_dictionnary_PREDICT2NLU={'SSP_UIAnnual_Intense_use':'ann_intense',
                                    'SSP_UIAnnual_Light_use':'ann_light',
                                    'SSP_UIAnnual_Minimal_use':'ann_minimum',
                                    'SSP_UIManaged_pasture_Intense_use':'past_intense',
                                    'SSP_UIManaged_pasture_Light_use':'past_light',
                                    'SSP_UINitrogen_Intense_use':'c3nfx_intense',
                                    'SSP_UINitrogen_Light_use':'c3nfx_light',
                                    'SSP_UINitrogen_Minimal_use':'c3nfx_minimum',
                                    'SSP_UIPerennial_Intense_use':'per_intense',
                                    'SSP_UIPerennial_Light_use':'per_light',
                                    'SSP_UIPerennial_Minimal_use':'per_minimum',
                                    'SSP_UIRangelands_':'range',
                                    'SSP_UISecondary_':'non_agri',
                                    'SSP_UISecondary':'non_agri',
                                    'SSP_UIUrban_Intense_use':'urban_intense',#'urban_int', 
                                    'SSP_UIUrban_Light_use':'urban_light',#'urban_light', 
                                    'SSP_UIUrban_Minimal_use':'urban_minimum'#'urban_min'
                                        }
   return convert_dictionnary_PREDICT2NLU[vname]

def project_year(model, model_dir, scenario, year):
  """Run a projection for a single year.  Can be called in parallel when
projecting a range of years.

  """

  print("projecting %s for %s using %s" % (model, year, scenario))

  what, models = select_models(model, model_dir)
  # Read Sam's abundance model (forested and non-forested)
  mod = modelr.load(models[0])
  predicts.predictify(mod)

  # Import standard PREDICTS rasters
  #rasters = predicts.rasterset('luh2', scenario, year)
  #rs = RasterSet(rasters)
  # Create a dict() with all the inputs
  df = dict()
  fn_region_map="../../land-use2/output_yad/NLU_regions.nc"
  region_map=netCDF4.Dataset(fn_region_map,'r')
  region_map_array=region_map.variables['NLU_regions'][:].data
  region_map.close()
  for vname in mod.syms:
    ds = netCDF4.Dataset(var_to_fname(vname, scenario, year),'r')
    data = ds.variables[PREDICT2NLU_name(vname)][:]
    #import pdb;pdb.set_trace()
    if isinstance(data, np.ma.MaskedArray):
      data=np.where(np.isnan(data), 0, data[:].data)
    ds.close()
#    import pdb;pdb.set_trace()
    data=np.where(region_map_array==-9999, 0, data)
    data[data<0]=0
    df[vname] = data
  # Verify all rasters have the same shape
  shapes = set([arr.shape for arr in df.values()])
  assert(len(shapes) == 1)
  # Evaluation engine expects one dimensional arrays (1D) so reshape
  # input.  We undo the transformation on the result.  Note that these are
  # cheap operations with numpy arrays (only pdate metadata).
  for vname in df.keys():
     df[vname] = df[vname].reshape(-1)
  res = mod.eval(df)
  #if "ab" in model:
        #res_exp=np.array(res,dtype=np.float128)

  if what in ('CompSimAb', 'CompSimSR'):
    expr = '(inv_logit(%s) - 0.01) / (inv_logit(%f) - 0.01)'
  else:
    expr = '(exp(%s) / exp(%f))'
  rs[what] = SimpleExpr(what, expr % (mod.output, mod.intercept))

  rs[mod.output] = mod

  if what not in rs:
    print('%s not in rasterset' % what)
    print(', '.join(sorted(rs.keys())))
    sys.exit(1)

  stime = time.time()
  data, meta = rs.eval(what, quiet=True)
  etime = time.time()
  print("executed in %6.2fs" % (etime - stime))
  oname = '%s/luh2/%s-%s-%d.tif' % (utils.outdir(), scenario, what, year)
  with rasterio.open(oname, 'w', **meta) as dst:
    dst.write(data.filled(meta['nodata']), indexes=1)
  if None:
    fig = plt.figure(figsize=(8, 6))
    show(data, cmap='viridis', ax=plt.gca())
    fig.savefig('luh2-%s-%d.png' % (scenario, year))
  return

def unpack(args):
  """Unpack arguments passed to parallel map."""
  project_year(*args)

@click.command()
@click.argument('what', type=click.Choice(['ab', 'sr', 'cs-ab', 'cs-sr']))
@click.argument('scenario', type=str)
@click.argument('years', type=str)
@click.argument('output_dir', type=str)
@click.option('--model-dir', '-m', type=click.Path(file_okay=False),
              default=os.path.abspath('.'),
              help='Directory where to find the models ' +
              '(default: ../models)')
@click.option('--parallel', '-p', default=1, type=click.INT,
              help='How many projections to run in parallel (default: 1)')

def project(what, scenario, years,output_dir, model_dir, parallel=1):
  """Project changes in terrestrial biodiversity using REDICTS models.

  Writes output to a GeoTIFF file named <scenario>-<what>-<year>.tif.

  """

  #utils.luh2_check_year(min(years), scenario)
  #utils.luh2_check_year(max(years), scenario)
  if parallel == 1:
    tuple(map(lambda y: project_year(what, model_dir, scenario, y),
              years))
    return
  pool = multiprocessing.Pool(processes=parallel)
  pool.map(unpack, zip(itertools.repeat(what),
                       itertools.repeat(model_dir),
                       itertools.repeat(scenario), years))

if __name__ == '__main__':
#pylint: disable-msg=no-value-for-parameter
  project()
#pylint: enable-msg=no-value-for-parameter
