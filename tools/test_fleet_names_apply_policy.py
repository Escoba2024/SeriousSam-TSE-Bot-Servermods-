import copy
import unittest
import fleet_names_apply_policy as p
from gaming_names import name_id


def fixture():
    rows, obs = [], {}
    count = 0
    for i in p.INSTANCES:
        locals_, query = [], []
        for role in ('botA', 'botB'):
            for n in range(4):
                count += 1
                name = f'Name{count}'
                ordinal = n + (4 if role == 'botB' else 0)
                rows.append(dict(instance=i, role=role, local=n, bot_id=f'{i}.bot.{ordinal:03d}', native_name=name, nickname=name, name_id=name_id(name)))
                locals_.append(dict(role=role, local=n, index=ordinal, guid=f'{count:032x}', native=name, profile_native=name))
                query.append(name)
        obs[i] = dict(locals=locals_, query_names=query+['UNKNOWN'])
    return rows, obs


class Policy(unittest.TestCase):
    def test_unknown_allowed_without_collision(self):
        rows, obs = fixture()
        self.assertEqual(p.fleet(rows, obs, applied=True)['own_count'], 48)
    def test_collisions_and_missing_actual_identity(self):
        rows, obs = fixture()
        for mutate in (lambda x:x['redstation']['query_names'].append('Name9'),
                       lambda x:x['redstation']['query_names'].append('Name1'),
                       lambda x:x['redstation']['locals'].pop(),
                       lambda x:x['redstation']['locals'][0].update(index=1),
                       lambda x:x['redstation']['locals'][0].update(guid=x['redstation']['locals'][1]['guid']),
                       lambda x:x['redstation']['locals'][0].update(profile_native='Other')):
            with self.subTest(mutate=mutate):
                bad=copy.deepcopy(obs);mutate(bad)
                with self.assertRaises(ValueError):p.fleet(rows,bad,applied=True)
    def test_all_48_and_stable_ids(self):
        rows,obs=fixture()
        for bad in (rows[:-1],rows+[rows[0]], [dict(r,bot_id='wrong') for r in rows]):
            with self.assertRaises(ValueError):p.fleet(bad,obs)
    def test_legacy_flash_exclusion_not_new_output(self):
        rows,obs=fixture();local=obs['redstation']['locals'][0]
        local.update(native='^f8OldName^r',profile_native='^f8OldName^r')
        obs['redstation']['query_names'][0]='^f8OldName^r'
        p.fleet(rows,obs)
        with self.assertRaises(ValueError):p.fleet(rows,obs,applied=True)
    def test_attach_exact_four_and_epoch(self):
        text='\n'.join(f'[BotDriver] local player {n} (player index {n+4}) is now bot-driven: Name{n}'for n in range(4))
        self.assertEqual(len(p.attach_rows(text)),4)
        with self.assertRaises(ValueError):p.attach_rows(text+'\n[BotDriver] local player 0 (player index 3) is now bot-driven: Other')
    def test_path_boundary_no_dll_or_server(self):
        roots={i:'/fake/'+i for i in p.INSTANCES}
        paths=[f'{roots[i]}/{r}/Players/Player{n}.plr' for i in p.INSTANCES for r in ('botA','botB')for n in range(4)]
        paths +=[roots['redstation']+'/'+n for n in ('launch-botA.sh','launch-botB.sh','roster100.json')]
        p.name_only_paths(paths,roots)
        with self.assertRaises(ValueError):p.name_only_paths(paths+['/fake/server/Bin/GameMP.dll'],roots)


class Backend:
    def __init__(self, fail=None, recovery_fail=None):self.calls=[];self.fail=fail;self.recovery_fail=recovery_fail
    def event(self,state,**kw):self.calls.append('journal:'+state)
    def __getattr__(self,name):
        def call():
            self.calls.append(name)
            if name in (self.fail,self.recovery_fail):raise ValueError(name)
            return {'names_only':True}
        return call


class Transaction(unittest.TestCase):
    def test_complete_apply(self):
        b=Backend();p.transaction(b)
        self.assertEqual(b.calls[-1],'journal:applied_names_only')
        self.assertNotIn('rollback_close',b.calls)
    def test_every_mutating_failure_rolls_back_exact_startup_order(self):
        for point in ('close_own_clients','backup_after_close','apply_names','start_own_clients','verify_applied'):
            b=Backend(point)
            with self.assertRaises(ValueError):p.transaction(b)
            self.assertEqual(b.calls[-1],'journal:rolled_back')
            self.assertLess(b.calls.index('rollback_verify'),b.calls.index('rollback_launch_policy'))
            self.assertLess(b.calls.index('rollback_restore'),b.calls.index('rollback_start'))
    def test_recovery_error_never_success(self):
        b=Backend('apply_names','rollback_restore')
        with self.assertRaises(RuntimeError):p.transaction(b)
        self.assertEqual(b.calls[-1],'journal:rollback_incomplete')
    def test_preflight_failure_never_stops_anything(self):
        b=Backend('preflight')
        with self.assertRaises(ValueError):p.transaction(b)
        self.assertEqual(b.calls,['journal:preflight','preflight'])

class JournalFailures(unittest.TestCase):
    def test_failure_event_io_does_not_skip_guarded_rollback(self):
        class Once(Backend):
            def event(self,state,**kw):
                super().event(state,**kw)
                if state=='apply_failed':raise OSError('journal temporarily full')
        b=Once('apply_names')
        with self.assertRaisesRegex(ValueError,'apply_names'):
            p.transaction(b)
        self.assertIn('rollback_restore',b.calls)
        self.assertEqual(b.calls[-1],'journal:rolled_back')

    def test_rollback_journal_failure_retains_original_and_recovery_errors(self):
        class Broken(Backend):
            def event(self,state,**kw):
                super().event(state,**kw)
                if state in ('rollback_close_own_clients','rollback_incomplete'):
                    raise OSError('journal unavailable')
        b=Broken('apply_names')
        with self.assertRaises(RuntimeError) as caught:p.transaction(b)
        self.assertIn('apply_names',str(caught.exception))
        self.assertIn('journal unavailable',str(caught.exception))
        self.assertNotIn('rollback_close',b.calls)

    def test_failed_first_close_intent_never_closes_running_clients(self):
        class Broken(Backend):
            def event(self,state,**kw):
                super().event(state,**kw)
                if state=='close_own_clients':raise OSError('journal failed')
        b=Broken()
        with self.assertRaises(OSError):p.transaction(b)
        self.assertNotIn('close_own_clients',b.calls)
        self.assertNotIn('rollback_close',b.calls)

if __name__=='__main__':unittest.main()
