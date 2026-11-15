"""Exact closed Trouble031-case adapter over the unchanged prior pure reader."""
import ast,hashlib,os
from pathlib import Path
BASE=Path(__file__).with_name('audit_hole031_closed.py')
BASE_SHA='475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e'
PAIRS=[
 ('One bounded closed Hole031 audit','One bounded closed Trouble031 audit'),
 ('/srv/tse-milestone-a-evidence-20261111/nav20-031-hole-root-hole-20261115-141204','/srv/tse-milestone-a-evidence-20261111/nav20-031-trouble-root-trouble-20261115-153818'),
 ('/srv/tse-nav20-031-hole600-diag1-root-frozen-20261115','/srv/tse-nav20-031-trouble600-diag1-root-frozen-20261115'),
 ('/srv/tse-hole031-closed-audit-evidence-20261115','/srv/tse-trouble031-closed-audit-evidence-20261115'),
 ('7e581f512eaf9717221d18eeb9b5091e11ed72d83b8960d282858c3bc00262a4','fba9d4a9c276e7dd3612c36ecbd81941ab67cf284a920810a5d3942bce4d7b1f'),
 ("map='hole'","map='trouble'"),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-host/receipt.json','/srv/tse-cecil-rollout-evidence-20261114/navigation031-trouble-host/receipt.json'),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-root-restore.json','/srv/tse-cecil-rollout-evidence-20261114/navigation031-trouble-root-restore.json'),
 ('COMPLETE_CANONICAL_HOLE031_CLOSED_AUDIT_ONLY','COMPLETE_CANONICAL_TROUBLE031_CLOSED_AUDIT_ONLY'),
]
STATE={}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def adapt(raw,reverse=False):
 if not reverse and digest(raw)!=BASE_SHA:raise ValueError('exact corrected Hole031 pure reader required')
 text=raw.decode()
 for a,b in(reversed(PAIRS)if reverse else PAIRS):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('exact unique closed-case literal required')
  text=text.replace(a,b,1)
 changed=text.encode();ast.parse(changed)
 if reverse and digest(changed)!=BASE_SHA:raise ValueError('complete reader inverse differs')
 return changed

def namespace():
 with os.fdopen(os.open(BASE.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:raw=f.read(1024*1024+1)
 if len(raw)>1024*1024:raise ValueError('small reader-source bound')
 transformed=adapt(raw)
 if adapt(transformed,True)!=raw:raise ValueError('whole case-source inverse')
 scope={'__name__':'closed_trouble031_pure_reader','__file__':str(Path(__file__).resolve())}
 exec(compile(transformed,str(BASE)+'[exact-closed-Trouble-case]', 'exec'),scope)
 scope['account'](BASE,raw)
 scope['G']['cache'][str(BASE)]=raw
 STATE.update(scope=scope,base_sha256=digest(raw),transformed_sha256=digest(transformed))
 return scope

def main():
 scope=namespace();scope['main']()
 receipt=dict(status='EXACT_CLOSED_CASE_READER_ADAPTER_ONLY_NO_RUNTIME',base_source_sha256=STATE['base_sha256'],transformed_source_sha256=STATE['transformed_sha256'],adapter_sha256=digest(Path(__file__).read_bytes()),whole_base_source_inverse=True,literal_pairs=PAIRS,limits_unchanged=True,old_raw_replays=0,qualified=False)
 print('ADAPTATION',scope['save']('reader-adaptation.json',receipt),flush=True)
if __name__=='__main__':main()
