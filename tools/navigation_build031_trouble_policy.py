"""Exactly one disabled031 LittleTrouble600 diagnostics1 condition."""
def options(map_key,duration,diag,build):
 if (map_key!='trouble'or build!='031'or type(duration)not in(int,float)
     or duration!=600 or type(diag)is not int or diag!=1):
  raise ValueError('fixed031 LittleTrouble600s diagnostics1 observation only')
