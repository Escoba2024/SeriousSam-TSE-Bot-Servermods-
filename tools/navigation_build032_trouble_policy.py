"""One fixed032 LittleTrouble600/DIAG1 condition; no broader runtime admission."""
def options(map_key,duration,diag,build):
 if(map_key!='trouble'or build!='032'or type(duration)not in(int,float)or duration!=600
    or type(diag)is not int or diag!=1):raise ValueError('fixed032 LittleTrouble600s diagnostics1 observation only')
