#!/usr/bin/env python3
"""Read-only monitor entrypoint for the explicitly configured colored roster."""
import sys
from pathlib import Path
if len(sys.argv)<2 or sys.argv[1]!='monitor':
 raise SystemExit('only read-only monitor action is allowed')
sys.path.insert(0,'/srv/tse-ops-monitor-release-20261022/b5a6cba/tools')
sys.path.insert(0,'/srv/tse-ops-monitor-release-20261022/b5a6cba/tools/operations')
import fleet_supervisor as s
assert s.q is s.h.q
s.q.ROSTER=['BOT-^cDDEEFF[Q] Pip^r', 'BOT-^c80D8FFNils^r', 'BOT-^cA5D6A7Mara^r', 'BOT-^cFFD180Rudi^r', 'BOT-^cFFD180Juna^r', 'BOT-^cFFD180Rin^r', 'BOT-^cFFD180[AG] Lea^r', 'BOT-^cA5D6A7Lars^r']
s.q.ROSTER=[__import__("re").sub(r"\^c[0-9a-fA-F]{6}|\^r","",n) for n in s.q.ROSTER]
s.main()
