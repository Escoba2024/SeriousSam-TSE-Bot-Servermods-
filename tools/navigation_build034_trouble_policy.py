"""One fixed034 LittleTrouble300/DIAG1 diagnostic; no runtime admission here."""
def options(map_key,duration,diag,build):
 if(map_key!='trouble'or build!='034'or type(duration)not in(int,float)or duration!=300
    or type(diag)is not int or diag!=1):raise ValueError('fixed034 LittleTrouble300s diagnostics1 observation only')

DURATION_OLD="need(type(duration)in(int,float)and duration==600,'fixed600s functional window')"
DURATION_NEW="need(type(duration)in(int,float)and duration==300,'fixed300s diagnostic window')"
def duration_source(text,reverse=False):
 """Only the new copy's exact hardmap duration; old600 policies stay immutable."""
 import ast
 a,b=(DURATION_NEW,DURATION_OLD)if reverse else(DURATION_OLD,DURATION_NEW)
 if text.count(a)!=1 or b in text:raise ValueError('unique original hardmap duration anchor required')
 result=text.replace(a,b,1);ast.parse(result);return result
