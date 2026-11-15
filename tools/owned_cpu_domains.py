"""Read only explicitly supplied own CPU sources; no discovery/loops/writes.
Process and cgroup domains overlap: never add them or label them host CPU%.
The caller attests ownership and archives returned raw/error rows privately.
"""
import math
from pathlib import Path,PurePosixPath
import time

MAX_RAW=16384

def _need(ok,message):
    if not ok:raise ValueError(message)
def _read(path):
    with open(path,'r')as stream:return stream.read(MAX_RAW+1)
def _text(read,path,row):
    value=read(path);_need(type(value)is str,'text CPU source required')
    row['raw'].append(value[:MAX_RAW+1]);_need(len(value)<=MAX_RAW,'bounded CPU source')
    return value
def _proc(text,pid,start):
    head,tail=text.rsplit(') ',1);fields=tail.split()
    _need(int(head.split(' (',1)[0])==pid and len(fields)>=20,'PID/stat shape changed')
    u,s,t=(int(fields[i])for i in(11,12,19))
    _need(all(0<=v<2**64 for v in(u,s,t))and t==start,'PID/start/counter changed')
    return u,s
def _identity(stat,path):
    value=stat(path);dev,ino=value.st_dev,value.st_ino
    _need(type(dev)is int and 0<=dev<2**64 and type(ino)is int and 0<ino<2**64,'exact cgroup device/inode required')
    return [path,dev,ino]
def _unknown(row,error):
    row.pop('counter',None);row.update(status='UNKNOWN',error=str(error)[:512]);return row

def sample(epoch,processes,cgroups,clock_hz,*,read=_read,stat=lambda p:Path(p).stat(),clock=time.monotonic):
    """Two stat reads per PID; directory identity before/after one cpu.stat.
    Snapshot times bound all counter observations, not an atomic host snapshot.
    """
    _need(type(epoch)is str and 0<len(epoch)<=80,'bounded epoch required')
    _need(type(clock_hz)is int and 0<clock_hz<=1000000,'exact clock Hz required')
    _need(type(processes)is dict and type(cgroups)is dict and 0<len(processes)+len(cgroups)<=64,'bounded source maps required')
    _need(all(type(k)is str and 0<len(k)<=80 for k in[*processes,*cgroups]),'bounded source label required')
    for pair in processes.values():
        _need(type(pair)in(tuple,list)and len(pair)==2 and all(type(v)is int and v>0 for v in pair)and pair[0]<2**31 and pair[1]<2**64,'exact own PID/start required')
    for path in cgroups.values():
        _need(type(path)is str and path.startswith('/sys/fs/cgroup/')and '..'not in PurePosixPath(path).parts and str(PurePosixPath(path))==path,'exact absolute own cgroup path required')
    out={'schema':'OWN_CPU_DOMAINS_V1','epoch':epoch,'clock_hz':clock_hz,'started':None,'finished':None,'processes':{},'cgroups':{},'errors':[]}
    def stamp(key):
        try:
            v=clock();_need(type(v)in(int,float)and math.isfinite(v)and v>=0,'finite monotonic clock required');out[key]=v
        except Exception as error:out['errors'].append(key+':'+str(error)[:512])
    stamp('started')
    for name,(pid,start)in processes.items():
        row={'status':'VALID','identity':[pid,start],'raw':[]};out['processes'][name]=row
        try:
            _need(out['started']is not None,'start clock unknown');path='/proc/'+str(pid)+'/stat'
            first=_proc(_text(read,path,row),pid,start);last=_proc(_text(read,path,row),pid,start)
            _need(all(b>=a for a,b in zip(first,last)),'process counter regressed during read')
            row.update(utime_ticks=last[0],stime_ticks=last[1],counter=sum(last))
        except Exception as error:_unknown(row,error);out['errors'].append('process:'+name+':'+row['error'])
    for name,path in cgroups.items():
        row={'status':'VALID','raw':[]};out['cgroups'][name]=row
        try:
            _need(out['started']is not None,'start clock unknown');before=_identity(stat,path);row['identity_before']=before
            text=_text(read,path+'/cpu.stat',row);after=_identity(stat,path);row['identity_after']=after
            _need(before==after,'cgroup recreated during read');row['identity']=after
            values=[line.split()[1:]for line in text.splitlines()if line.split()and line.split()[0]=='usage_usec']
            _need(len(values)==1 and len(values[0])==1,'one usage_usec required');value=int(values[0][0])
            _need(0<=value<2**64,'cgroup counter range');row['counter']=value
        except Exception as error:_unknown(row,error);out['errors'].append('cgroup:'+name+':'+row['error'])
    stamp('finished')
    if out['started']is None or out['finished']is None or out['finished']<out['started']:
        out['errors'].append('invalid sample time range')
        for domain in('processes','cgroups'):
            for row in out[domain].values():_unknown(row,'invalid sample time range')
    out['status']='UNKNOWN'if out['errors']else'VALID';return out

def delta(before,after):
    """Per-domain CPU seconds and core-equivalent ranges; no additive total."""
    out={'schema':'OWN_CPU_DOMAIN_DELTAS_V1','epoch':after['epoch'],'processes':{},'cgroups':{}};reason=None
    try:
        _need(before['epoch']==after['epoch']and before['clock_hz']==after['clock_hz'],'epoch/clock Hz changed')
        times=[before['started'],before['finished'],after['started'],after['finished']]
        _need(all(type(v)in(int,float)and math.isfinite(v)and v>=0 for v in times),'unknown sample times')
        a,b,c,d=times;_need(a<=b<c<=d,'nonsequential sample ranges');out['elapsed_range']=[c-b,d-a]
    except Exception as error:reason=str(error)
    for domain,scale in(('processes',after['clock_hz']),('cgroups',1000000)):
        for name in sorted(set(before[domain])|set(after[domain])):
            row={'status':'VALID'};out[domain][name]=row
            try:
                _need(reason is None,reason);a=before[domain].get(name,{});b=after[domain].get(name,{})
                _need(a.get('status')==b.get('status')=='VALID'and a['identity']==b['identity'],'missing/reused/unknown CPU source')
                count=b['counter']-a['counter'];_need(count>=0,'CPU counter regressed')
                seconds=count/scale;lo,hi=out['elapsed_range'];ranges=[seconds/hi,seconds/lo]
                _need(all(math.isfinite(v)for v in ranges),'nonfinite CPU range')
                row.update(cpu_seconds=seconds,core_equivalent_range=ranges,identity=b['identity'])
            except Exception as error:_unknown(row,error)
    out['status']='UNKNOWN'if reason or any(r['status']=='UNKNOWN'for d in('processes','cgroups')for r in out[d].values())else'VALID'
    if reason:out['error']=reason
    return out
