
import importlib
import numpy as np
import numpy.ma as ma
import os
import re
import sys

from .. import lu
from .. import utils
from projections.r2py.tree import Node, Operator

class LUH5(object):
  def __init__(self, name, intensity):
    self._name = name
    self._intensity = intensity
    self._inputs = []
    if name in ['plantation_pri', 'plantation_sec']:
      self._inputs = [name]
      self._pkg_func = lambda x: np.full_like(x.values()[0], 0.333)
    else:
      if name in ('secdy', 'secdi', 'secdm'):
        mod_name = 'secondary'
      else:
        mod_name = name
      py = os.path.join(utils.lui_model_dir(), '%s.py' % mod_name)
      if not os.path.isfile(py):
        raise RuntimeError('could not find python module for %s' % mod_name)
      rds = os.path.join(utils.lui_model_dir(), '%s.rds' % mod_name)
      if not os.path.isfile(rds):
        raise RuntimeError('could not find RDS file for %s' % mod_name)
      if os.path.getmtime(py) < os.path.getmtime(rds):
        raise RuntimeError('python module is older than RDS file for %s' % mod_name)
      if intensity != 'minimal':
        if utils.lui_model_dir() not in sys.path:
          sys.path.append(utils.lui_model_dir())
        self._pkg = importlib.import_module(mod_name)
        self._pkg_func = getattr(self._pkg, intensity + '_st')
        self._inputs += getattr(self._pkg, 'inputs')()
      self._inputs += [name + '_' + intensity + '_ref']
      if intensity == 'light':
        self._inputs += [name + '_intense']
      elif intensity == 'minimal':
        self._inputs += [name + '_intense', name + '_light']
    
  @property
  def name(self):
    return self._name + '_' + self.intensity
    
  @property
  def as_intense(self):
    return self._name + '_intense'
    
  @property
  def as_light(self):
    return self._name + '_light'
    
  @property
  def as_minimal(self):
    return self._name + '_minimal'
    
  @property
  def intensity(self):
    return self._intensity
    
  @property
  def syms(self):
    return self._inputs # FIXME: + [self.name + '_ref']

  def eval(self, df):
    if self._name in ['plantation_pri', 'plantation_sec']:
      return df[self._name] / 3
    if self._name[-10:] == '_secondary':
      return ma.where(df['secondary'] <= 0, 0,
                      df['secondary_' + self.intensity] * df[self._name] /
                      (df['secondary'] + 1e-5))
    if self.intensity == 'minimal':
      res = (df[self._name] - df[self.as_intense] - df[self.as_light])
      return res
    res = self._pkg_func(df)
    res[np.where(np.isnan(res))] = 1.0
    res = np.clip(df[self.name + '_ref'] + res, 0, 1)
    if self.intensity == 'light':
      intense = df[self.as_intense] / (df[self._name] + 1e-10)
      res = np.where(intense + res > 1, 1 - intense, res)
    res *= df[self._name]
    return res

def _predictify(root, prefix):
  newr = root.replace(prefix, '')
  newr = newr.replace(' Vegetation', '')
  newr = newr.replace('_Vegetation', '')
  newr = newr.replace(' vegetation', '')
  newr = newr.replace(' forest', '_pri')
  newr = re.sub(r'(Minimal|Light|Intense)[ _]use',  "\\1", newr)
  newr = re.sub(r'(Mature|Intermediate|Young)',  "\\1", newr)
  newr = newr.lower()
  newr = newr.replace(' ', '_')
  if newr == 'plantation_pri':
    name = newr
  else:
    name = newr.rsplit('_', 1)[0]
  assert name in lu.luh5.types() or name in lu.luh5.types(True), 'unknown land use type %s' % root
  return newr

def as_contrast(root, prefix):
  if isinstance(root, str) and re.match(prefix, root):
    newr = root.replace(prefix, '')
    newr = re.sub(r'^.*-', '', newr)
    newr = newr.replace('Managed ', '')
    newr = newr.replace(' use', '')
    newr = newr.replace(' forest', '_pri')
    predictified = _predictify(newr, '')
    if predictified == 'primary':
      ## If the right-hand side of a contrast is "primary" assume it
      ## refers to primary_light_and_intense since primary_minimal is
      ## on the LHS. 
      predictified = 'primary_light_and_intense'
    return predictified
  if (isinstance(root, Node) and root.type is Operator('in') and
      re.match(prefix, root.args[0])):
    name = root.args[0].replace(prefix, '')
    lhs, rhs = name.split('-', 2)
    if lhs.lower() not in ['primary minimal', 'primary vegetation minimal',
                           'primary vegetation minimal use']:
      print('ignoring %s' % root.args[0])
      return 0.0
  return root

def is_luh5(syms, prefix):
  for sym in syms:
    if prefix == 'Contrast':
      sym = re.sub(r'^.*-', '', sym)
    try:
      _ = _predictify(sym, prefix)
    except AssertionError:
      print('lui.is_luh5 failed on %s' % sym)
      return False
  return True

def predictify(root, prefix):
  if isinstance(root, str) and re.match(prefix, root):
    newr = _predictify(root, prefix)
    return newr
  return root
