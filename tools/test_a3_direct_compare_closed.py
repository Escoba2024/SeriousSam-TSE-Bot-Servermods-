"""Closed-report adapter cases; no native inputs or artifact qualification."""
import copy
import unittest

from a3_compare_direct_closed import compare_reports


class ClosedComparisonTests(unittest.TestCase):
    def report(self,swap):
        row=lambda kills,hp:dict(calls=kills,lethal_calls=kills,hp_loss_raw=hp,
            hp_loss_capped_at_pre_hit_health=hp,armor_loss_raw=0.)
        return dict(window='synthetic'+str(swap),pair=[1,2],swap=swap,
            direct_condition_sha256='a'*64,qualified=False,a3_accepted=False,
            initial_replay_exact=True,cohort_configs_reproduced=True,native_hard_rules_verified=True,source_hashes={},
            damage=dict(full_coverage=True,original_bodies_restored=True,
                server_kill_pairs_equal_all_lethal_records=True,
                known_foreign_matrix={'MITTEL -> STARK':row(2,200.),'STARK -> MITTEL':row(3,300.)}))

    def test_complete_reports_keep_actual_both_directions_without_acceptance(self):
        out=compare_reports([self.report(1),self.report(0)])
        self.assertEqual(out['kill_directions'],[1,1])
        self.assertEqual(out['capped_damage_directions'],[1,1])
        self.assertFalse(out['tier_strength_accepted']);self.assertFalse(out['native_qualified'])
        self.assertEqual(len(out['source_windows']),2)

    def test_missing_direction_is_zero_only_after_full_stream_proof(self):
        a,b=self.report(0),self.report(1)
        del a['damage']['known_foreign_matrix']['MITTEL -> STARK']
        out=compare_reports([a,b]);self.assertEqual(out['windows'][0]['lower_to_higher']['calls'],0)
        a['damage']['full_coverage']=False
        with self.assertRaises(ValueError):compare_reports([a,b])

    def test_restore_kill_initial_proofs_and_inherited_acceptance_cannot_be_skipped(self):
        for scope,key,value in [('damage','original_bodies_restored',False),
            ('damage','server_kill_pairs_equal_all_lethal_records',False),
            (None,'initial_replay_exact',False),(None,'cohort_configs_reproduced',False),
            (None,'native_hard_rules_verified',False),
            (None,'qualified',True),(None,'a3_accepted',True)]:
            a,b=self.report(0),self.report(1)
            target=a if scope is None else a[scope];target[key]=value
            with self.assertRaises(ValueError):compare_reports([a,b])

    def test_mixed_condition_and_repeat_swap_reject(self):
        for field,value in [('direct_condition_sha256','b'*64),('swap',0)]:
            a,b=self.report(0),self.report(1);b[field]=value
            with self.assertRaises(ValueError):compare_reports([a,b])


if __name__=='__main__':unittest.main()
