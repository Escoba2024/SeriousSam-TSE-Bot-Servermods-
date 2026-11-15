"""Exactly one Build031 Hole600 diagnostic observation; no runtime activation."""
def options(map_key,duration,diag,build):
 if (map_key!='hole' or build!='031' or type(duration) not in (int,float)
     or duration!=600 or type(diag) is not int or diag!=1):
  raise ValueError('fixed031 Hole600s diagnostics1 observation only')
