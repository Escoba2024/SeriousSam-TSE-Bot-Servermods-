"""Recheck two closed private windows before reporting direct tier directions."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

import a3_direct_tiers


def compare_reports(reports):
    """Only reports freshly returned by the full closed-window analyzer qualify here."""
    windows=[]
    for r in reports:
        if r.get('qualified')is not False or r.get('a3_accepted')is not False:
            raise ValueError('offline analysis cannot inherit A3/native acceptance')
        if not(r.get('native_hard_rules_verified')is True and
               r['damage']['full_coverage']and r['damage']['original_bodies_restored']and
               r['damage']['server_kill_pairs_equal_all_lethal_records']and
               r['initial_replay_exact']and r['cohort_configs_reproduced']):
            raise ValueError('complete Originaldamage/initial/restore proofs required')
        matrix=copy.deepcopy(r['damage']['known_foreign_matrix'])
        low,high=[a3_direct_tiers.NAMES[t]for t in r['pair']]
        # A missing direction is zero only after the whole closed call stream was
        # checked. Never manufacture zeros from an absent/incomplete observation.
        for key in (low+' -> '+high,high+' -> '+low):
            matrix.setdefault(key,dict(calls=0,lethal_calls=0,hp_loss_raw=0.,
                hp_loss_capped_at_pre_hit_health=0.,armor_loss_raw=0.))
        windows.append(dict(pair=r['pair'],swap=int(r['swap']),
            condition_sha256=r['direct_condition_sha256'],closed_complete=True,
            matrix=matrix))
    output=a3_direct_tiers.compare(windows)
    output['source_windows']=[dict(window=r['window'],source_hashes=r['source_hashes'])for r in reports]
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('window0');parser.add_argument('window1')
    args=parser.parse_args()
    path=Path(__file__).resolve().parent/'analyze-direct020.py'
    spec=importlib.util.spec_from_file_location('direct_closed_window_analyzer',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reports=[module.analyze(w)for w in (args.window0,args.window1)]
    output=compare_reports(reports)
    target=path.parent/f"pair{output['pair'][0]}{output['pair'][1]}-comparison.json"
    target.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
