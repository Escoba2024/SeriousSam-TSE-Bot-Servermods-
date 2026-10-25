import unittest
import analyze_combat_log as a


class CombatEvidence(unittest.TestCase):
    def test_legitimate_rejoin_resets_current_score_not_lifetime_events(self):
        log=('Raven joined\nNox joined\nRaven killed Nox\nRaven left\n'
             'Raven joined\nRaven passed away\n')
        r=a.analyze(log,{'a':'Raven','b':'Nox'})
        self.assertEqual(r['players']['a']['kills'],1)
        self.assertEqual(r['current_sessions']['a']['epoch'],2)
        self.assertEqual(r['current_sessions']['a']['stats']['frag_delta'],-1)
        self.assertEqual(r['bot_vs_bot_kills'],1)

    def test_self_kill_does_not_become_positive_frag(self):
        r=a.analyze('Raven killed Raven\n',{'a':'Raven'})
        self.assertEqual(r['recognized_deaths'],0)
    def test_real_events_and_environment_are_separate_from_fire_actions(self):
        log = ('^o^b^cFF0000Raven^r^r poured lead into ^oNox^r\n'
               '^oNox^r blew himself away\n'
               '^oRaven^r went over the edge\n'
               '[BotDriver] bot0 tick=100 fire=1 combat_fire_actions=900\n'
               '^oRaven^r joined\n')
        r = a.analyze(log, {'p0': 'Raven', 'p1': 'Nox'})
        self.assertEqual(r['players']['p0'], dict(kills=1, deaths=1, suicides=0,
                         world_deaths=1, frag_delta=0, kill_types={'bullet': 1}))
        self.assertEqual(r['players']['p1']['frag_delta'], -1)
        self.assertEqual(r['players']['p1']['deaths'], 2)
        self.assertIsNone(r['shots'])
        self.assertIsNone(r['hit_accuracy'])

    def test_unknown_players_do_not_get_published(self):
        r = a.analyze('PrivateUser killed Raven\nRaven blew PrivateUser away\n', {'p': 'Raven'})
        self.assertEqual(r['players']['p']['kills'], 1)
        self.assertEqual(r['players']['p']['deaths'], 1)
        self.assertNotIn('PrivateUser', str(r))

    def test_unknown_messages_are_not_fabricated_events(self):
        r = a.analyze('Raven fired at Nox\nRaven killed Nox extra\n', {'p': 'Raven'})
        self.assertEqual(r['recognized_deaths'], 0)

    def test_casefold_collision_rejected(self):
        with self.assertRaises(ValueError):
            a.analyze('', {'a': 'Raven', 'b': '^cff0000raven^r'})


if __name__ == '__main__': unittest.main()
