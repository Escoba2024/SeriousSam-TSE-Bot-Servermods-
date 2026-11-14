"""One diagnostic condition only. No runtime, asset, input or process calls."""
def options(map_key,duration,diag,build):
 if (map_key!='redstation' or build!='023' or type(duration)not in(int,float)
     or duration!=180 or type(diag)is not int or diag!=1):
  raise ValueError('diagnostic requires Build023 RedStation180s diagnostics1 only')


def hard_options(map_key,duration,diag,catalog):
 options(map_key,duration,diag,'023')
 if type(catalog)is not dict or map_key not in catalog:
  raise ValueError('diagnostic requires existing RedStation catalog binding')
