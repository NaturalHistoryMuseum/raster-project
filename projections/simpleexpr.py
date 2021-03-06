
import numpy as np
import numpy.ma as ma

import projections.r2py.reval as reval
import projections.r2py.rparser as rparser

class SimpleExpr():
  def __init__(self, name, expr):
    self.name = name
    self.tree = reval.make_inputs(rparser.parse(expr))
    lokals = {}
    exec(reval.to_py(self.tree, name), lokals)
    self.func = lokals[name + '_st']

  @property
  def syms(self):
    return reval.find_inputs(self.tree)
  
  def eval(self, df, window=None):
    try:
      res = self.func(df)
    except KeyError as e:
      print("Error: input '%s' not defined" % e)
      raise e
    if not isinstance(res, np.ndarray):
      if not window:
        res = ma.masked_array(np.full(tuple(df.values())[0].shape, res,
                                      dtype=np.float32))
      else:
        h = window[0][1] - window[0][0]
        w = window[1][1] - window[1][0]
        res = ma.masked_array(np.full((h, w), res, dtype=np.float32))
    return res
