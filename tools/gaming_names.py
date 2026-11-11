"""Bounded Retail 1.07 names and offline fleet assignment proposals.

No process, profile or service is changed. Callers must allocate the whole fleet
under their deployment lock, using fresh active names, and persist bot IDs.
The 22-visible/32-ASCII-byte caps are project policy, not engine buffer claims.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

SEED = 20261111
VISIBLE_CAP = 22
BYTE_CAP = 32
BASELINE_SHA256 = 'cdd04932790ed8ba0d06cffd524c9cd11fadd4b370de11cb02d95303caa13b26'
PALETTE = ('FF6655', '66CCFF', 'A5D66A', 'FFCC66', 'CC88FF', 'EEEEEE', '33DDCC')


def validate_native(value):
    """Accept only the subset corroborated by original Retail decoder probes.

Flash is rejected: the original decoder consumes an extra visible byte.
Balanced style endings and terminal reset prevent format leakage.
"""
    if not isinstance(value, str) or not value.isascii() or not 1 <= len(value) <= BYTE_CAP:
        raise ValueError('name must contain 1..32 ASCII bytes')
    visible, styles = [], set()
    i, decorated = 0, False
    while i < len(value):
        c = value[i]
        if c != '^':
            if not re.fullmatch(r'[A-Za-z0-9 ._\[\]-]', c):
                raise ValueError('unsafe name character')
            visible.append(c)
            i += 1
            continue
        token = re.match(r'\^c[0-9a-fA-F]{6}|\^[bBiIr]', value[i:])
        if token is None:
            raise ValueError('unsupported or incomplete format (flash disabled)')
        code = token[0]
        if code in ('^b', '^i'):
            if code[1] in styles:
                raise ValueError('duplicate style start')
            styles.add(code[1])
        elif code in ('^B', '^I'):
            if code[1].lower() not in styles:
                raise ValueError('unmatched style end')
            styles.remove(code[1].lower())
        elif code == '^r':
            if i != len(value)-2 or styles:
                raise ValueError('balanced styles and final reset required')
        decorated = True
        i += len(code)
    result = ''.join(visible)
    if (not 1 <= len(result) <= VISIBLE_CAP or result != result.strip() or
            not any(c.isalnum() for c in result) or styles or
            (decorated and not value.endswith('^r'))):
        raise ValueError('visible name or terminal format reset invalid')
    return result


def normalize(value):
    return validate_native(value).casefold()


def normalize_occupied(value):
    """Existing external display text is exclusion data, never a new name.

External players need not obey our name length/character/reset policy. Unknown
markup fails closed: obtain the real undecorated query spelling instead of
guessing the broken flash decoder's result. Trim conservatively for exclusion.
"""
    if not isinstance(value,str):
        raise ValueError('occupied display name must be text')
    plain=re.sub(r'\^c[0-9a-fA-F]{6}|\^[bBiIr]', '', value)
    if '^' in plain:
        raise ValueError('unsupported occupied markup; require actual query display name')
    return plain.strip().casefold()


def validate_pool(names):
    if not isinstance(names, list) or not names:
        raise ValueError('nonempty name list required')
    seen = set()
    for name in names:
        key = normalize(name)
        if key in seen:
            raise ValueError('duplicate normalized visible name: '+key)
        seen.add(key)
    return seen


def name_id(name):
    return 'nickname-'+hashlib.sha256(normalize(name).encode('ascii')).hexdigest()[:24]


def decorate(name, seed=SEED):
    """Stable SHA256 style selection; never truncate a name or a token."""
    if validate_native(name) != name:
        raise ValueError('plain source name required')
    digest=hashlib.sha256(f'{seed}:{name}'.encode('ascii')).digest()
    slot=digest[0] % 100
    style = ('plain' if slot < 50 else 'single' if slot < 75 else
             'bold' if slot < 85 else 'italic' if slot < 95 else 'bolditalic')
    color='^c'+PALETTE[digest[1] % len(PALETTE)]
    start, end = {'plain':('', ''), 'single':('', ''), 'bold':('^b','^B'),
                  'italic':('^i','^I'), 'bolditalic':('^b^i','^I^B')}[style]
    native=name if style=='plain' else start+color+name+end+'^r'
    if len(native)>BYTE_CAP:
        native=color+name+'^r'
        style='single'
    validate_native(native)
    return native, style


def make_catalog(names, additions=()):
    validate_pool(names)
    decorated={a['nickname']:a for a in additions}
    if len(decorated)!=len(additions) or not set(decorated)<=set(names):
        raise ValueError('invalid additions catalog')
    rows=[]
    for name in names:
        if '^' in name:
            raise ValueError('merged pool must retain plain names')
        native=decorated.get(name, {}).get('native_name',name)
        if validate_native(native)!=name:
            raise ValueError('native spelling differs from plain nickname')
        rows.append(dict(name_id=name_id(name), nickname=name, native_name=native))
    return rows


def allocate(catalog, bot_ids, *, occupied_names=(), existing=None, seed=SEED):
    """Allocate a complete fleet proposal; stable bot IDs are caller-owned.

occupied_names are OTHER connected players. Do not pass a bot's own persisted
name as occupied. existing retains assignments across additive pool changes.
An insufficient pool or stale collision fails; no partial assignments escape.
"""
    if type(seed) is not int:
        raise ValueError('integer seed required')
    if (not isinstance(bot_ids, list) or len(set(bot_ids))!=len(bot_ids) or
            any(not isinstance(i,str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,96}', i) for i in bot_ids)):
        raise ValueError('unique stable bot IDs required')
    if not isinstance(catalog,list):
        raise ValueError('catalog list required')
    validate_pool([r['native_name'] for r in catalog])
    canonical={r['name_id']:r for r in catalog}
    for row in catalog:
        if row['name_id']!=name_id(row['nickname']) or validate_native(row['native_name'])!=row['nickname']:
            raise ValueError('invalid catalog identity')
    occupied={normalize_occupied(n) for n in occupied_names}
    result={}
    existing={} if existing is None else existing
    if not isinstance(existing,dict) or not set(existing)<=set(bot_ids):
        raise ValueError('existing assignments must belong to requested fleet')
    for bot_id in sorted(existing):
        old=existing[bot_id]
        row=canonical.get(old.get('name_id'))
        if row is None or old!=dict(bot_id=bot_id,**row):
            raise ValueError('existing assignment changed or no longer in catalog')
        key=normalize(row['native_name'])
        if key in occupied:
            raise ValueError('existing assignment collides with an active name')
        occupied.add(key)
        result[bot_id]=dict(bot_id=bot_id,**row)
    for bot_id in sorted(set(bot_ids)-set(existing)):
        candidates=[r for r in catalog if normalize(r['native_name']) not in occupied]
        if not candidates:
            raise ValueError('not enough unoccupied names')
        row=min(candidates,key=lambda r:hashlib.sha256(f'{seed}:{bot_id}:{r["name_id"]}'.encode('ascii')).digest())
        occupied.add(normalize(row['native_name']))
        result[bot_id]=dict(bot_id=bot_id,**row)
    return result


def json_bytes(value):
    return (json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode('ascii')


def build_bundle(directory):
    directory=Path(directory)
    baseline_raw=(directory/'GamingNicknames.baseline.json').read_bytes()
    if hashlib.sha256(baseline_raw).hexdigest()!=BASELINE_SHA256:
        raise ValueError('baseline bytes changed')
    baseline=json.loads(baseline_raw)
    source_raw=(directory/'GamingNicknames.additions.source.json').read_bytes()
    source=json.loads(source_raw)
    if len(baseline)!=208 or len(source)!=250:
        raise ValueError('expected208 preserved names plus250 additions')
    validate_pool(baseline+source)
    additions=[]
    for name in source:
        native,style=decorate(name)
        additions.append(dict(name_id=name_id(name),nickname=name,native_name=native,style=style))
    validate_pool(baseline+[a['native_name'] for a in additions])
    merged=json_bytes(baseline+source)
    added=json_bytes(additions)
    metadata=dict(schema=1,version='milestone-a-names-20261111',seed=SEED,
                  algorithm='sha256(seed:alias) style-v1; curated aliases are fixed input',
                  baseline_count=len(baseline),additional_count=len(additions),total_count=len(baseline)+len(additions),
                  baseline_sha256=BASELINE_SHA256,source_sha256=hashlib.sha256(source_raw).hexdigest(),
                  pool_sha256=hashlib.sha256(merged).hexdigest(),additions_sha256=hashlib.sha256(added).hexdigest(),
                  encoding='ASCII',visible_cap=VISIBLE_CAP,raw_byte_cap=BYTE_CAP,
                  style_counts=dict(sorted(Counter(a['style'] for a in additions).items())),flash_count=0,
                  flash_fallback='plain (original Retail decoder loses a name byte)',
                  max_visible=max(len(a['nickname']) for a in additions),
                  max_raw_bytes=max(len(a['native_name']) for a in additions),
                  bot_id_policy='External stable fleet ID; nickname IDs are not player GUIDs or bot IDs.',
                  acceptance=dict(portable='VALIDATED',native_rendering='OPEN',external_query='OPEN',runtime_deployed=False))
    return {'GamingNicknames.json':merged,'GamingNicknames.additions.json':added,
            'GamingNicknames.metadata.json':json_bytes(metadata)}


def generate_bundle(directory):
    outputs=build_bundle(directory)
    for name,data in outputs.items():
        (Path(directory)/name).write_bytes(data)


def verify_bundle(directory):
    for name,expected in build_bundle(directory).items():
        if (Path(directory)/name).read_bytes()!=expected:
            raise ValueError('bundle differs from fixed inputs: '+name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[1]/'poc/scripts')
    parser.add_argument('--generate',action='store_true',help='regenerate repository data, never runtime')
    parser.add_argument('--request',type=Path,help='JSON: bot_ids, occupied_names, optional existing; proposal to stdout')
    args=parser.parse_args()
    if args.generate:
        generate_bundle(args.data_dir)
    verify_bundle(args.data_dir)
    if args.request:
        request=json.loads(args.request.read_text())
        catalog=make_catalog(json.loads((args.data_dir/'GamingNicknames.json').read_text()),
                             json.loads((args.data_dir/'GamingNicknames.additions.json').read_text()))
        print(json_bytes(allocate(catalog,**request)).decode('ascii'),end='')
    else:
        print((args.data_dir/'GamingNicknames.metadata.json').read_text(),end='')


if __name__=='__main__':
    main()
