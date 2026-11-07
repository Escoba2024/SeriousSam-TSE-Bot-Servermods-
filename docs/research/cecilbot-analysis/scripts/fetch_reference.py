#!/usr/bin/env python3
"""Fetch only the pinned public references recorded in reference-manifest.json.
No credentials, game files, installation or services are used. Existing files are
validated, never overwritten. NAV dataset redistribution rights remain unresolved.
"""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for row in json.loads((ROOT/'exports/reference-manifest.json').read_text()):
 path=ROOT/'reference'/row['path']
 if path.exists():data=path.read_bytes()
 else:
  url='https://raw.githubusercontent.com/DreamyCecil/CecilBotMod/'+row['source_commit']+'/'+row['path']
  data=urllib.request.urlopen(url,timeout=30).read()
 if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
  raise SystemExit('HASH MISMATCH: '+row['path'])
 if not path.exists():
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
print('All pinned references verified')
