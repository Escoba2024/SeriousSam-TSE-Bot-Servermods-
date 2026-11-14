"""Focused direct-tier policy cases; no process, Frida or game access."""
import copy
import unittest

import a3_direct_tiers as policy


CANONICAL = '''bot_bHumanAI=1;
bot_bAutoCombat=1;
bot_bSupplyNavigation=1;
bot_bDiagnostics=0;
bot_iRosterOffset=4;
bot_iProfile0=7;
bot_iProfile1=7;
bot_iProfile2=7;
bot_iProfile3=7;
bot_iProfileSeed=2026110750;
'''


class DirectTierTests(unittest.TestCase):
    def test_four_selected_pair_swap_assignments(self):
        for lower, swap, expected in [(1,0,(1,2)),(1,1,(2,1)),(2,0,(2,3)),(2,1,(3,2))]:
            with self.subTest(lower=lower,swap=swap):
                self.assertEqual(tuple(policy.tiers(lower,swap).values()), expected)

    def test_unknown_pairs_swaps_roles_or_diagnostics_reject(self):
        for lower,swap in [(0,0),(3,0),(1,2),(True,0),(1,False)]:
            with self.assertRaises(ValueError):policy.tiers(lower,swap)
        with self.assertRaises(ValueError):policy.configuration(CANONICAL,'vanilla',1,0,0)
        with self.assertRaises(ValueError):policy.configuration(CANONICAL,'botA',1,0,1)

    def test_both_configs_differ_only_by_tier(self):
        for lower in (1,2):
            for swap in (0,1):
                a=policy.configuration(CANONICAL,'botA',lower,swap,0)
                b=policy.configuration(CANONICAL,'botB',lower,swap,0)
                self.assertEqual(policy.without_tier(a),CANONICAL)
                self.assertEqual(policy.without_tier(a),policy.without_tier(b))
                self.assertIn('bot_iRosterOffset=4;',a)
                self.assertIn('bot_iProfileSeed=2026110750;',a)

    def test_existing_tier_legacy_or_unknown_profile_is_not_a_canonical_source(self):
        for raw in [CANONICAL+'bot_iArenaTier=3;\n',CANONICAL.replace('bot_bHumanAI=1','bot_bHumanAI=0'),
                    CANONICAL.replace('bot_iProfile2=7','bot_iProfile2=1')]:
            with self.assertRaises(ValueError):policy.configuration(raw,'botA',1,0,0)

    def test_direct_registry_relabels_actual_entity_slots_and_keeps_pointer(self):
        mapping=dict(botA=[0,2,4,6],botB=[1,3,5,7],vanilla=[8])
        rows={s:dict(entity_id=100+s,entity_pointer=65536+s*4096)for s in range(9)}
        cohorts={r:dict(candidate=True,tier=t,game_sha256='a'*64)for r,t in policy.tiers(1,1).items()}
        def inherited(rows,mapping,cohorts):
            return {row['entity_id']:dict(pointer=hex(row['entity_pointer']),slot=s,cohort='vanilla'if s==8 else'candidate')for s,row in rows.items()}
        out=policy.registry(inherited,rows,mapping,cohorts)
        self.assertEqual(out[100]['cohort'],'STARK');self.assertEqual(out[101]['cohort'],'MITTEL')
        self.assertEqual(out[100]['pointer'],hex(65536));self.assertEqual(out[108]['cohort'],'vanilla')

    def window(self,swap):
        metrics=lambda kills,hp:dict(lethal_calls=kills,hp_loss_capped_at_pre_hit_health=hp,
                                   hp_loss_raw=hp,armor_loss_raw=0,calls=kills)
        return dict(pair=[1,2],swap=swap,condition_sha256='a'*64,
                    closed_complete=True,native_qualified=False,
                    matrix={'MITTEL -> STARK':metrics(3,300),'STARK -> MITTEL':metrics(5,500)})

    def test_swapped_windows_report_both_actual_directions_without_acceptance(self):
        out=policy.compare([self.window(0),self.window(1)])
        self.assertEqual(out['kill_directions'],[1,1])
        self.assertEqual(out['capped_damage_directions'],[1,1])
        self.assertFalse(out['tier_strength_accepted'])

    def test_tie_and_reversal_remain_visible_without_margin(self):
        a,b=self.window(0),self.window(1)
        a['matrix']['STARK -> MITTEL']['lethal_calls']=3
        b['matrix']['STARK -> MITTEL']['lethal_calls']=2
        out=policy.compare([a,b]);self.assertEqual(out['kill_directions'],[0,-1])
        self.assertFalse(out['tier_strength_accepted'])

    def test_missing_swap_mixed_build_conditions_or_incomplete_window_reject(self):
        a,b=self.window(0),self.window(1)
        with self.assertRaises(ValueError):policy.compare([a])
        for field,value in [('swap',0),('condition_sha256','b'*64),('closed_complete',False)]:
            changed=copy.deepcopy(b);changed[field]=value
            with self.assertRaises(ValueError):policy.compare([a,changed])


if __name__=='__main__':unittest.main()
