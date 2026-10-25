#!/usr/bin/env python3
"""Sanitize private Retail combat evidence without inventing hit/damage metrics.

Counts one complete server log, separates stationary-control kills from bot-v-bot
kills, and compares current join-epoch deltas against actual native query scores.
Raw names, profiles, GUIDs, addresses and logs are never included in the output.
"""
import argparse
import json
from pathlib import Path
import re
from analyze_combat_log import analyze, visible


def process_summary(rows):
    windows={};roles={}
    for row in rows:
        for role,sample in row.get('processes',{}).items():
            if sample is None:continue
            r=roles.setdefault(role,dict(rss_peak_mib=0,pss_peak_mib=0))
            r['rss_peak_mib']=max(r['rss_peak_mib'],sample['rss_mib'])
            r['pss_peak_mib']=max(r['pss_peak_mib'],sample['pss_mib'])
            key=(role,sample['start_ticks']);point=(row['elapsed_s'],sample['cpu_s'])
            if key not in windows:windows[key]=[point,point]
            else:
                if point[0]<windows[key][1][0] or point[1]<windows[key][1][1]:
                    raise ValueError('non-monotonic process resource window')
                windows[key][1]=point
    for role,result in roles.items():
        intervals=[w for (name,_),w in windows.items() if name==role]
        seconds=sum(b[0]-a[0] for a,b in intervals)
        cpu=sum(b[1]-a[1] for a,b in intervals)
        result.update(observed_process_seconds=seconds,generations=len(intervals),
                      cpu_core_percent=100*cpu/seconds if seconds else None)
    return roles


def summarize(report,config,server_log,queries):
    roster={i['id']:i['nickname'] for i in config['identities']}
    events=analyze(server_log,roster)
    ids={visible(name).casefold():ident for ident,name in roster.items()}
    windows={}
    for ident,session in events['current_sessions'].items():
        joined=[e for e in report.get('events',[]) if e['id']==ident and e['event']=='joined']
        # The untimed native log cannot identify an unconfirmed extra join.
        # Require a complete corresponding journal before matching its last epoch.
        if not joined or len(joined)!=session['epoch']:continue
        last=max(joined,key=lambda e:e['at'])
        ends=[e['at'] for e in report['events'] if e['id']==ident and e['epoch']==last['epoch']
              and e['event'] in ('left','crashed','disconnected') and e['at']>=last['at']]
        windows[ident]=(last['at'],min(ends) if ends else float('inf'))
    native={}
    for row in queries:
        q=row['query']
        for key,name in q.items():
            if not re.fullmatch(r'player_\d+',key):continue
            ident=ids.get(visible(name).casefold())
            if ident is None:continue
            window=windows.get(ident)
            at=row.get('at')
            if window is None or not isinstance(at,(int,float)) or not window[0]<=at<=window[1]:continue
            score=q.get('frags_'+key[7:])
            if score is not None:native[ident]=int(score)
    players={}
    playing=0
    for ident,stats in events['players'].items():
        seconds=sum(w['playing_s'] for w in report.get('telemetry',{}).get(ident,[]))
        playing+=seconds
        session=events['current_sessions'][ident]
        reconciled=None
        if session['observed_join'] and ident in native:
            reconciled=session['stats']['frag_delta']==native[ident]
        players[ident]=dict(stats,playing_s=seconds,join_epochs=session['epoch'],
                            native_last_frag=native.get(ident),
                            current_session_event_frag=session['stats']['frag_delta'],
                            score_reconciled=reconciled)
    totals={k:sum(p[k] for p in players.values())
            for k in ('kills','deaths','suicides','world_deaths','frag_delta')}
    return dict(status=report.get('status'),dll_sha256=report.get('dll_sha256'),
                preset=report.get('preset'),requested_bots=report.get('max_bots'),
                peak_playing=report.get('peak_playing'),measured_s=report.get('measured_s'),
                elapsed_s=report.get('elapsed_s'),players=players,totals=totals,
                bot_vs_bot_kills=events['bot_vs_bot_kills'],active_player_seconds=playing,
                bot_vs_bot_kills_per_bot_minute=events['bot_vs_bot_kills']*60/playing if playing else None,
                world_deaths_per_bot_minute=totals['world_deaths']*60/playing if playing else None,
                cgroup_peak_mib=report.get('cgroup_peak_mib'),
                cgroup_cpu_core_percent_including_startup=report.get('cgroup_cpu_core_percent'),
                new_throttled_periods=report.get('new_throttled_periods'),
                all_bots_drained=report.get('all_bots_drained'),
                unmounts_ok=bool(report.get('unmounts')) and all(x['exitcode']==0 for x in report['unmounts']),
                shots=None,hits=None,hit_accuracy=None,damage=None,
                limitations=['control client is stationary','engine/spawn RNG not pinned',
                             'event counts include orderly drain; measured_s excludes drain'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',required=True,type=Path)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();root=args.runtime
    report=json.loads((root/'result.json').read_text())
    if report.get('scope')!='ISOLATED_NETNS_RETAIL_WINE':raise ValueError('private namespace evidence required')
    config=json.loads(args.config.read_text())
    log=(root/'layers/server/upper/Dedicated_BotTest.log').read_text(errors='replace')
    queries=[json.loads(line) for line in (root/'combat-queries.jsonl').read_text().splitlines()]
    result=summarize(report,config,log,queries)
    samples=[json.loads(line) for line in (root/'samples.jsonl').read_text().splitlines()]
    result['process_resources']=process_summary(samples)
    logs=list((root/'layers').glob('*/upper/SeriousSam.log'))
    logs+=list((root/'history').glob('*/SeriousSam.log'))
    texts=[log]+[p.read_text(errors='replace') for p in logs]
    result['sync_bad_lines']=sum(len(re.findall(r'SYNCBAD|Too many bad syncs|CRC check failed',text)) for text in texts)
    result['server_sync_ok_lines']=len(re.findall(r'SYNCOK:',log))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','bot_vs_bot_kills','totals','active_player_seconds',
                                         'cgroup_peak_mib','sync_bad_lines','unmounts_ok')}))


if __name__=='__main__':main()
