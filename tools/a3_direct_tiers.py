"""Pure policies for four separately selected direct-tier windows; no runtime."""
import copy
import math
import re


NAMES = {1:'MITTEL', 2:'STARK', 3:'DEMON'}


def require(value, message):
    if not value:
        raise ValueError('direct tiers: '+message)


def tiers(lower, swap):
    require(type(lower) is int and lower in (1,2), 'adjacent pair1/2 or2/3')
    require(type(swap) is int and swap in (0,1), 'swap0/1')
    pair = (lower, lower+1) if swap == 0 else (lower+1, lower)
    return dict(zip(('botA','botB'), pair))


def assignments(raw):
    result = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith('//'):
            continue
        m = re.fullmatch(r'\s*(\w+)\s*=\s*([^;\r\n]+);\s*', line)
        require(m is not None and m[1] not in result, 'unparsed/duplicate configuration')
        result[m[1]] = m[2].strip()
    return result


def configuration(raw, role, lower, swap, diagnostics):
    selected = tiers(lower, swap)
    require(role in selected, 'physical role')
    require(type(diagnostics) is int and diagnostics == 0, 'fixed diagnostics0')
    values = assignments(raw)
    for key, value in [('bot_bHumanAI','1'),('bot_bAutoCombat','1'),
                       ('bot_bSupplyNavigation','1'),('bot_bDiagnostics','0'),
                       ('bot_iRosterOffset','4'),('bot_iProfileSeed','2026110750')]:
        require(values.get(key) == value, 'canonical source '+key)
    require(all(values.get('bot_iProfile'+str(i)) == '7' for i in range(4)),
            'canonical explicit profile7')
    require('bot_iArenaTier' not in values, 'canonical source already contains tier')
    return raw + '\nbot_iArenaTier='+str(selected[role])+';\n'


def without_tier(raw):
    require(len(re.findall(r'(?m)^bot_iArenaTier=[123];$',raw)) == 1,
            'exact one appended tier')
    stripped = re.sub(r'\nbot_iArenaTier=[123];\n\Z','',raw)
    require(stripped != raw, 'canonical appended tier shape')
    return stripped


def registry(inherited_builder, rows, mapping, cohorts):
    require(set(cohorts) == {'botA','botB'}, 'two actual physical cohorts')
    require(all(c['candidate'] is True and type(c['tier']) is int and c['tier'] in NAMES
                for c in cohorts.values()), 'both cohorts use the actual candidate and tier')
    require(len({c['game_sha256'] for c in cohorts.values()}) == 1,
            'identical DLL required')
    require(abs(cohorts['botA']['tier']-cohorts['botB']['tier']) == 1,
            'adjacent distinct tiers')
    result = copy.deepcopy(inherited_builder(rows,mapping,cohorts))
    for role in ('botA','botB'):
        tier = cohorts[role]['tier']
        for slot in mapping[role]:
            row = rows[slot]
            item = result[row['entity_id']]
            require(item['slot'] == slot and item['pointer'] == hex(row['entity_pointer']),
                    'inherited actual entity/pointer/slot binding')
            item.update(cohort=NAMES[tier], tier=tier, role=role)
    return result


def compare(windows):
    """Report exact event directions; no kill margin or automatic A3 acceptance."""
    require(len(windows) == 2 and {w['swap'] for w in windows} == {0,1},
            'both distinct swapped windows required')
    windows = sorted(windows,key=lambda w:w['swap'])
    first = windows[0]
    lower, upper = first['pair']
    tiers(lower,0)
    require(upper == lower+1, 'adjacent pair')
    require(all(w['pair'] == first['pair'] and w['condition_sha256'] == first['condition_sha256']
                and w.get('closed_complete') is True for w in windows),
            'incomplete or mixed comparison conditions')
    low, high = NAMES[lower], NAMES[upper]
    records = []
    for window in windows:
        matrix = window['matrix']
        lo, hi = matrix[low+' -> '+high], matrix[high+' -> '+low]
        for row in (lo,hi):
            for field in ('calls','lethal_calls','hp_loss_raw',
                          'hp_loss_capped_at_pre_hit_health','armor_loss_raw'):
                value = row[field]
                require(type(value) in (int,float) and math.isfinite(value) and value >= 0,
                        'explicit finite actual metric '+field)
        records.append(dict(swap=window['swap'],lower_to_higher=copy.deepcopy(lo),
                            higher_to_lower=copy.deepcopy(hi)))
    sign = lambda value:(value>0)-(value<0)
    return dict(scope='TWO_DIRECT_SWAPPED_WINDOWS_REVIEW_REQUIRED',pair=[lower,upper],
                condition_sha256=first['condition_sha256'],windows=records,
                kill_directions=[sign(r['higher_to_lower']['lethal_calls']-r['lower_to_higher']['lethal_calls'])for r in records],
                capped_damage_directions=[sign(r['higher_to_lower']['hp_loss_capped_at_pre_hit_health']-r['lower_to_higher']['hp_loss_capped_at_pre_hit_health'])for r in records],
                tier_strength_accepted=False,native_qualified=False)
