"""Bounded ASCII Retail name markup; advanced effects are opt-in qualification.

The 22/32 caps are project policy, not a claim about engine buffer limits.
IDs/profile/GUID/session state stay with the existing SQLite planner.
"""
import random
import re

VISIBLE_CAP = 22
BYTE_CAP = 32
PALETTE = ('FF6655', '66CCFF', 'A5D66A', 'FFCC66', 'CC88FF', 'EEEEEE', '33DDCC')
STYLES = {'plain': 28, 'single': 30, 'duo': 16, 'multi': 5,
          'bold': 7, 'italic': 6, 'bolditalic': 4, 'flash': 3, 'flashcolor': 1}
ADVANCED = {'bold', 'italic', 'bolditalic', 'flash', 'flashcolor'}
UNQUALIFIED = {'flash', 'flashcolor'}  # original Retail decoder consumes the next byte


def validate_native(value, *, flash_probe=False):
    if type(flash_probe) is not bool:raise ValueError('explicit boolean flash probe required')
    if not isinstance(value, str) or not value.isascii() or not 1 <= len(value) <= BYTE_CAP:
        raise ValueError('native name must be 1..32 ASCII bytes')
    i = 0; visible = []; decorated = False
    while i < len(value):
        c = value[i]
        if c != '^':
            if not re.fullmatch(r'[A-Za-z0-9 ._\[\]-]', c):
                raise ValueError('unsafe visible character')
            visible.append(c); i += 1; continue
        token = re.match(r'\^c[0-9A-Fa-f]{6}|\^f[0-9]|\^[biIBF]|\^r', value[i:])
        if token is None: raise ValueError('incomplete or unsupported native markup')
        if token[0].startswith('^f') and not flash_probe:
            raise ValueError('Retail 1.07 flash decoder loses a name byte; private probe only')
        if token[0] == '^r' and i != len(value)-2:
            raise ValueError('reset must terminate the name')
        decorated = True; i += len(token[0])
    name = ''.join(visible)
    if (not 1 <= len(name) <= VISIBLE_CAP or name != name.strip() or
            not any(c.isalnum() for c in name) or (decorated and not value.endswith('^r'))):
        raise ValueError('visible length/terminal reset policy')
    return name


def decorate(name, rng, style='single'):
    if validate_native(name) != name or '^' in name: raise ValueError('plain nickname required')
    if style not in STYLES: raise ValueError('unknown style')
    if style in UNQUALIFIED:style='single'
    colors = rng.sample(PALETTE, 3)
    color = '^c' + colors[0]
    candidates = {
        'plain': name, 'single': color+name+'^r',
        'duo': color+name[:len(name)//2]+'^c'+colors[1]+name[len(name)//2:]+'^r',
        'multi': ''.join('^c'+colors[i]+name[i*len(name)//3:(i+1)*len(name)//3]
                         for i in range(3) if name[i*len(name)//3:(i+1)*len(name)//3])+'^r',
        'bold': '^b'+color+name+'^B^r', 'italic': '^i'+color+name+'^I^r',
        'bolditalic': '^b^i'+color+name+'^I^B^r',
        'flash': '^f3'+name+'^F^r', 'flashcolor': '^f3'+color+name+'^F^r'}
    value = candidates[style]
    if len(value) > BYTE_CAP:
        # Select a simpler complete style, never truncate name or a format code.
        if style=='multi' and len(candidates['duo'])<=BYTE_CAP:value=candidates['duo']
        else:value = color+name+'^r' if len(name)+10 <= BYTE_CAP else name
    validate_native(value)
    return value


def assign(pool, count, *, seed, advanced_styles=False):
    if (not isinstance(pool, list) or type(count) is not int or not 0 <= count <= len(pool)
            or type(seed) is not int or type(advanced_styles) is not bool):
        raise ValueError('pool/count/integer seed/boolean gate required')
    seen = set()
    for name in pool:
        if (validate_native(name) != name or '^' in name or
                re.match(r'(?i)^(?:BOT|\[BOT\])', name) or name.casefold() in seen):
            raise ValueError('duplicate or administrative BOT nickname')
        seen.add(name.casefold())
    rng = random.Random(seed)
    styles = [s for s in STYLES if s not in UNQUALIFIED and (advanced_styles or s not in ADVANCED)]
    result = []
    for i, name in enumerate(rng.sample(pool, count)):
        style = rng.choices(styles, weights=[STYLES[s] for s in styles])[0]
        result.append(dict(id=f'gamer-{i:03d}', nickname=name,
                           native_name=decorate(name, rng, style), profile=i % 8))
    return result


def main():
    import argparse
    import json
    from pathlib import Path
    from bot_sessions import validate_config
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pool',type=Path,default=Path(__file__).parents[1]/'poc/scripts/GamingNicknames.json')
    p.add_argument('--count',type=int,default=24)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--advanced-styles',action='store_true',help='generate private qualification proposals; runtime remains disabled')
    args=p.parse_args()
    identities=assign(json.loads(args.pool.read_text()),args.count,seed=args.seed,
                      advanced_styles=args.advanced_styles)
    c=validate_config(dict(enabled=False,colors_enabled=False,pool_id='gaming-v2',
                           seed=args.seed,servers=['alpha-one'],max_bots=min(8,args.count),
                           min_bots=min(3,args.count),identities=identities))
    with args.output.open('x') as stream:json.dump(c,stream,indent=2);stream.write('\n')


if __name__=='__main__': main()
