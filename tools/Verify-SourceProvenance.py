"""Verify published source bytes and exact stripping back to accepted captures."""
import hashlib
import json
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
proof = json.loads((repo / 'docs/reports/2026-10-12-source-verification.json').read_text())
sources = proof['sources']
assert len(sources) == len({s['name'] for s in sources}) == 13
assert proof['sdkCommit'] == 'aa7869c2c2c4db0562281814d0ac3784e6b9d6f0'
assert proof['includesCommit'] == '94ff8cd0e63941f8601294350b616472f772ed51'
for entry in sources:
    data = (repo / 'poc/release/gamemp' / entry['name']).read_bytes()
    digest = lambda value: hashlib.sha256(value).hexdigest().upper()
    assert digest(data) == entry['publishedSha256'], entry['name']
    offset = entry['noticeOffset']
    notice = entry['noticeText'].encode()
    assert len(notice) == entry['noticeBytes'] and data.count(notice) == 1
    assert data[offset:offset + len(notice)] == notice
    original = data[:offset] + data[offset + len(notice):]
    assert digest(original) == entry['originalSha256'], entry['name']
assert len(proof['compiledOriginalSources']) == 32
print('SOURCE PROVENANCE PASS: 13 published hashes and exact original captures')
