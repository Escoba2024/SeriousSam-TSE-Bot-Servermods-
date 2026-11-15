"""One new035/Yodeller600/diag0 condition, not a runtime admission."""
def options(map_key,duration,diag,build):
    if (map_key!='yodeller' or build!='035' or type(duration) not in (int,float) or duration!=600 or
        type(diag)is not int or diag!=0):raise ValueError('fixed035 Yodeller600 diagnostics0 condition required')
