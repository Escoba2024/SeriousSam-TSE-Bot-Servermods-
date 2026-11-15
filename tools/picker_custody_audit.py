"""Strict readonly031 custody grammar. Source time is NOT a native clock."""
import math
import re

BASE={'local':'i','tick':'i','actor':'u','generation':'u'}
HINT='ifiiiif'
SCHEMAS={
 'CecilPickerDecision':dict(BASE,time='f',reason='s',gates='uu',mapped='uu',anchor='ii',goal='ii',item='uu',search_after='f',attempt='ff',deadline='ff',budget='ii',origin='sii',scan='iiiiiiiiiu',input='iuuffniii ffff'.replace(' ',''),source_position='fff',attempts='i',overflow='i',refresh='iu'),
 'CecilPickerOrigin':dict(BASE,nearest='sii',h0=HINT,h1=HINT,h2=HINT),
 'CecilPickerAttempt':dict(BASE,attempt='i',index='i',item='u',kind='i',weapon='i',snapshot='uffff',end='s',budget='ii',visibility='iiiif',nearest='sii',path='in',h0=HINT,h1=HINT,h2=HINT),
 'CecilPickerArbitration':dict(BASE,proposal='iufff',gates='uu',taken='i',submitted='i',action='fff',rotation='fff',buttons='u',refresh='iu'),
}
NEAREST={'uncalled','input_guard','no_hint','probes_failed','chosen'}
ENDS={'unattempted','no_choice','missing_entity','visibility','nearest','nearest_budget','no_hint_or_probe','unreachable_path','committed'}


def scalar(raw,kind):
 if kind in('i','u'):
  if not re.fullmatch(r'-?\d+',raw):raise ValueError('typed integer')
  n=int(raw)
  if not((-2**31<=n<2**31)if kind=='i'else(0<=n<2**32)):raise ValueError('integer width')
  return n
 if kind=='s':
  if not re.fullmatch('[a-z_]+',raw):raise ValueError('typed symbol')
  return raw
 if not re.fullmatch(r'[-+]?(?:\d+(?:\.\d*)?(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|inf|nan)',raw,re.I):raise ValueError('typed float')
 value=float(raw)
 if not math.isfinite(value):
  if kind!='n':raise ValueError('nonfinite source-contract field')
  return {'raw':raw,'nonfinite':'nan'if math.isnan(value)else('-inf'if value<0 else'inf')}
 return value


def tuple_value(raw,types):
 if len(types)==1:return scalar(raw,types)
 if not(raw.startswith('(')and raw.endswith(')')):raise ValueError('typed tuple')
 values=raw[1:-1].split(',')
 if len(values)!=len(types):raise ValueError('tuple arity')
 return[scalar(v,t)for v,t in zip(values,types)]


def flag(value):
 if type(value)is not int or value not in(0,1):raise ValueError('boolean flag')


def mask(value,limit):
 known,truth=value
 if known&~limit or truth&~known:raise ValueError('unknown/shortcircuit bitmap')


def probe(value):
 code,before,after,known,length=value
 if code not in range(7)or before<0 or after<0:raise ValueError('probe code/budget')
 flag(known)
 if length<0 or (code in(0,1,2)and known)or(code>=3 and not known):raise ValueError('probe known contract')
 if(code in(1,2)and before!=after)or(code>=3 and after!=before-1):raise ValueError('probe accounting')
 if code==2 and before>2:raise ValueError('reserve veto')
 if code==3 and length!=0:raise ValueError('zero-length clear')


def nearest(row):
 end,result,geometry=row
 if end not in NEAREST or result< -1:raise ValueError('nearest result')
 flag(geometry)
 if(end=='chosen')!=(result>=0):raise ValueError('nearest chosen/result')


def parse(line):
 if not line.startswith('[CecilPicker'):return None
 if len(line.encode('latin1'))>=1024:raise ValueError('fixed1024 format bound')
 head=re.fullmatch(r'\[(CecilPicker\w+)\] (.*)',line)
 if not head:raise ValueError('picker row grammar')
 tag,text=head.groups()
 if tag=='CecilPickerFault':raise ValueError('actual custody format Fault: '+text)
 if tag not in SCHEMAS:raise ValueError('unknown custody schema')
 fields={}
 for part in text.split(' '):
  key,sep,raw=part.partition('=')
  if not sep or key in fields or key not in SCHEMAS[tag]:raise ValueError('whole unique schema')
  fields[key]=tuple_value(raw,SCHEMAS[tag][key])
 if set(fields)!=set(SCHEMAS[tag]):raise ValueError('missing custody field')
 d=fields
 if d['local']not in range(4)or d['tick']<0:raise ValueError('local/tick bounds')
 if tag=='CecilPickerDecision':
  if d['reason']not in('normal_done','no_anchor')or d['time']<0:raise ValueError('decision reason/time')
  mask(d['gates'],7);mask(d['mapped'],63)
  flag(d['overflow']);flag(d['refresh'][0]);flag(d['input'][0]);flag(d['input'][7]);flag(d['input'][8]);flag(d['scan'][8])
  if d['refresh'][1]not in range(32)or d['overflow']or not 0<=d['attempts']<=8:raise ValueError('custody overflow/reason')
  if any(x<0 for x in d['budget'])or any(x<0 for x in d['scan'][:9])or d['scan'][0]>8193 or d['scan'][1]>128 or d['scan'][3]>d['scan'][2]:raise ValueError('scan/budget limits')
  if d['scan'][9]&~((1<<19)-1|(1<<31)):raise ValueError('readreason bitmap')
  nearest(d['origin'])
 elif tag in('CecilPickerOrigin','CecilPickerAttempt'):
  nearest(d['nearest'])
  for k in ('h0','h1','h2'):
   slot,distance,*p=d[k]
   if slot< -1 or distance<0:raise ValueError('hint geometry')
   probe(p)
  if tag=='CecilPickerAttempt':
   if d['attempt']not in range(8)or not -1<=d['index']<128 or d['kind']not in range(-1,6)or not 0<=d['weapon']<=14 or d['end']not in ENDS:raise ValueError('attempt bounds')
   if any(x<0 for x in d['budget']):raise ValueError('attempt budget')
   probe(d['visibility']);flag(d['path'][0])
 elif tag=='CecilPickerArbitration':
  flag(d['proposal'][0]);flag(d['taken']);flag(d['refresh'][0]);mask(d['gates'],1023)
  if d['submitted']!=1 or d['proposal'][1]&~127 or d['refresh'][1]not in range(32):raise ValueError('arbitration contract')
 return {'tag':tag,'fields':d}


def assemble(rows):
 """Input already has role/phase/line. No hidden best-row selection or dedup."""
 batches={}
 if len(rows)>100000:raise ValueError('bounded custody row set')
 for row in rows:
  d=row['fields'];key=(row['phase'],row['role'],d['local'],d['actor'],d['generation'],d['tick'])
  b=batches.setdefault(key,{'key':list(key),'decision':None,'origin':None,'attempts':{},'arbitration':None})
  tag=row['tag']
  if tag=='CecilPickerAttempt':
   idx=d['attempt']
   if idx in b['attempts']:raise ValueError('duplicate admitted attempt')
   b['attempts'][idx]=row
  else:
   name={'CecilPickerDecision':'decision','CecilPickerOrigin':'origin','CecilPickerArbitration':'arbitration'}[tag]
   if b[name]is not None:raise ValueError('duplicate same-call custody')
   b[name]=row
 if len(batches)>8192:raise ValueError('bounded decision set')
 for b in batches.values():
  if b['decision']is None or b['origin']is None:raise ValueError('missing admitted decision/origin')
  d=b['decision']['fields']
  if set(b['attempts'])!=set(range(d['attempts'])):raise ValueError('missing admitted attempt')
  if d['origin']!=b['origin']['fields']['nearest']:raise ValueError('summary/origin custody differs')
  b['attempts']=[b['attempts'][i]for i in range(d['attempts'])]
 return list(batches.values())
