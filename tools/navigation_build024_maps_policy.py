"""Pure contract for one independently selected Build024 map observation."""
MAPS=('skulls','trouble','hole','yodeller')


def options(map_key,duration,diag,build,expected_map):
 if (expected_map not in MAPS or map_key!=expected_map or build!='024'
     or type(duration)not in(int,float)or duration!=600
     or type(diag)is not int or diag!=0):
  raise ValueError('fixed selected024 map requires600s diagnostics0')
