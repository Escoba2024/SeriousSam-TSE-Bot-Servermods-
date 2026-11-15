"""One fixed diagnostic observation; no comparison or functional acceptance."""


def options(map_key,duration,diag,build):
 if (map_key!='skulls'or build!='027'or type(duration)not in(int,float)
     or duration!=600 or type(diag)is not int or diag!=1):
  raise ValueError('fixed027 Skulls600s diagnostics1 observation only')
