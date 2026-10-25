import unittest
from ai2_run_summary import summarize, process_summary


class RunSummary(unittest.TestCase):
    def test_prior_epoch_query_cannot_qualify_a_later_equal_score(self):
        config={'identities':[{'id':'a','nickname':'Alpha'}]}
        report={'events':[dict(id='a',epoch=1,event='joined',at=10),
                          dict(id='a',epoch=1,event='left',at=15),
                          dict(id='a',epoch=2,event='joined',at=20)],'telemetry':{}}
        queries=[{'at':12,'query':{'player_1':'Alpha','frags_1':'0'}}]
        r=summarize(report,config,'Alpha joined\nAlpha left\nAlpha joined\n',queries)
        self.assertIsNone(r['players']['a']['score_reconciled'])
        self.assertIsNone(r['players']['a']['native_last_frag'])
        queries.append({'at':21,'query':{'player_3':'Alpha','frags_3':'0'}})
        self.assertTrue(summarize(report,config,'Alpha joined\nAlpha left\nAlpha joined\n',queries)['players']['a']['score_reconciled'])

    def test_process_cpu_windows_do_not_mix_rejoined_generations(self):
        rows=[]
        for at,start,cpu,rss in [(0,100,0,100),(10,100,1,120),(20,200,0,90),(30,200,.2,110)]:
            rows.append({'elapsed_s':at,'processes':{'a':dict(start_ticks=start,cpu_s=cpu,rss_mib=rss,pss_mib=80)}})
        p=process_summary(rows)['a']
        self.assertEqual(p['rss_peak_mib'],120)
        self.assertEqual(p['observed_process_seconds'],20)
        self.assertAlmostEqual(p['cpu_core_percent'],6)
        self.assertEqual(p['generations'],2)
        self.assertEqual(process_summary([{'elapsed_s':1}]),{})

    def test_rejoins_keep_event_totals_separate_from_native_session_score(self):
        config={'identities':[{'id':'a','nickname':'Alpha'},{'id':'b','nickname':'Bravo'}]}
        report={'status':'PASS_LIMITED_SESSION_LIFECYCLE','events':[
            dict(id='a',epoch=1,event='joined',at=0),dict(id='b',epoch=1,event='joined',at=0),
            dict(id='b',epoch=1,event='left',at=40),dict(id='b',epoch=2,event='joined',at=50)],'telemetry':{
            'a':[{'playing_s':60,'reports':[]}],
            'b':[{'playing_s':30,'reports':[]},{'playing_s':30,'reports':[]}]}}
        log='Alpha joined\nBravo joined\nAlpha poured lead into Control\nAlpha poured lead into Bravo\nBravo passed away\nBravo left\nBravo joined\n'
        queries=[{'at':60,'query':{'player_1':'Alpha','frags_1':'2','player_3':'Bravo','frags_3':'0'}}]
        r=summarize(report,config,log,queries)
        self.assertEqual(r['totals']['kills'],2)
        self.assertEqual(r['bot_vs_bot_kills'],1)
        self.assertEqual(r['totals']['world_deaths'],1)
        self.assertEqual(r['active_player_seconds'],120)
        self.assertEqual(r['bot_vs_bot_kills_per_bot_minute'],.5)
        self.assertEqual(r['players']['b']['frag_delta'],-1)
        self.assertEqual(r['players']['b']['native_last_frag'],0)
        self.assertTrue(r['players']['b']['score_reconciled'])
        self.assertIsNone(r['hits'])
        self.assertIsNone(r['hit_accuracy'])

    def test_native_score_mismatch_and_missing_join_remain_unqualified(self):
        config={'identities':[{'id':'a','nickname':'Alpha'}]}
        query=[{'at':1,'query':{'player_2':'Alpha','frags_2':'-3'}}]
        report={'events':[dict(id='a',epoch=1,event='joined',at=0)],'telemetry':{}}
        r=summarize(report,config,'Alpha joined\nAlpha passed away\n',query)
        self.assertFalse(r['players']['a']['score_reconciled'])
        self.assertIsNone(r['bot_vs_bot_kills_per_bot_minute'])
        r=summarize({'telemetry':{}},config,'Alpha passed away\n',query)
        self.assertIsNone(r['players']['a']['score_reconciled'])
