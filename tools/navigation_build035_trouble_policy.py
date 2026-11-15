"""One fixed035 LittleTrouble300/DIAG1 diagnostic; no runtime admission."""
def options(map_key,duration,diag,build):
 if(map_key!='trouble'or build!='035'or type(duration)not in(int,float)or duration!=300
    or type(diag)is not int or diag!=1):raise ValueError('fixed035 LittleTrouble300s diagnostics1 observation only')
