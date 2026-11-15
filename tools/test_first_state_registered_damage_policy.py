"""Actual new validator on packets produced by actual transformed JS callbacks."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from tools import test_first_state_registered_damage_patch as fixture
PARENT=fixture.PARENT
read=fixture.read

def policy(root):
    name='registered_policy_'+str(id(root));s=importlib.util.spec_from_file_location(name,root/'observer_policy.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def packets():
    text=fixture.ActualRegisteredScope().run_js("""
const ps=[];const t=x.startTick();ps.push(x.api.drain());
const a=x.enter('cast_ray',0x100000,[0x700000]);ps.push(x.api.drain());
const b=x.enter('continue_cast',0x100000,[0x700000]);x.leave(b);ps.push(x.api.drain());x.leave(a);
x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);ps.push(done(x));
console.log(JSON.stringify(ps));
""")
    return json.loads(text)

def respawn_packet():
    source=read(Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/respawn_fixture.js'))
    source=source.replace(b"const B=require('../../initial-static-bindings.json');",b"const B=require('./observer_harness').G;")
    # The inherited fixture predates the reviewed two-stage idle detach API.
    source=source.replace(b"x.api.stop();const end=x.api.drain();",b"x.api.stop();x.api.finishstop();const end=x.api.drain();")
    return json.loads(fixture.ActualRegisteredScope().run_js("""
const {scenario}=require('./tests/respawn_fixture');const r=scenario();
assert.equal(r.packet.counters.faults,0,JSON.stringify(r.packet.errors));
assert(r.packet.events.some(e=>e.kind==='initialize_player'&&e.data.payload.respawn_source&&e.data.payload.respawn_source.chain_bound===true));
console.log(JSON.stringify([r.packet,r.end]));
""",extra={'tests/respawn_fixture.js':source}))

class RegisteredPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=tempfile.TemporaryDirectory(prefix='registered-policy-');cls.root=Path(cls.directory.name)
        cls.old=cls.root/'old';cls.new=cls.root/'new'
        for root in(cls.old,cls.new):
            (root/'bindings').mkdir(parents=True)
            for f in('observer_policy.py','event-schema.json','bindings/original-bindings.json'):
                (root/f).write_bytes(read(PARENT/'vendor/observer'/f))
        helper=Path(__file__).with_name('first_state_registered_damage_policy.py')
        if helper.exists():
            from tools import first_state_registered_damage_policy as p
            (cls.new/'observer_policy.py').write_text(p.patch_policy((cls.new/'observer_policy.py').read_text()))
            (cls.new/'event-schema.json').write_text(p.patch_schema((cls.new/'event-schema.json').read_text()))
        cls.new_policy=policy(cls.new);cls.old_policy=policy(cls.old);cls.ps=packets()

    @classmethod
    def tearDownClass(cls):cls.directory.cleanup()

    def test_actual_scope_packets_pending_and_complete_strictly_validate(self):
        p=self.new_policy;t=p.TraceValidator(self.ps[0]['identity'])
        for packet in self.ps:t.consume(packet)
        self.assertEqual(t.last['scope_counters']['entered_excluded'],2)
        ident=self.ps[0]['identity'];external={'schema':'a1.first-state.external-restore.v1','before_identity':ident,
            'after_identity':ident,'script_unloaded':True,'session_detached':True,'prior_errors':[],
            'regions':p.expected_restore_regions(ident)}
        self.assertEqual(len(external['regions']),38)
        self.assertEqual(t.finish(external)['status'],'OBSERVER_TRANSPORT_COMPLETE_ONLY')

    def test_both_scope_validators_reject_the_other_contract(self):
        for p in self.ps:
            with self.assertRaises(self.old_policy.TraceRejected):self.old_policy.validate_packet(p)
        old=json.loads(fixture.ActualRegisteredScope().run_js("console.log(JSON.stringify(done(x)));",legacy=True))
        with self.assertRaises(self.new_policy.TraceRejected):self.new_policy.validate_packet(old)

    def test_counter_row_parent_native_order_mutations_are_rejected(self):
        paths=[('scope_counters','pending'),('scope_counters','entered_excluded'),
               ('scope_counters','native_edges'),('scope_counters','rows_attempted'),('counters','events_attempted')]
        for a,b in paths:
            with self.subTest(field=b):
                ps=copy.deepcopy(self.ps);ps[-1][a][b]+=1
                t=self.new_policy.TraceValidator(ps[0]['identity'])
                with self.assertRaises(self.new_policy.TraceRejected):
                    for p in ps:t.consume(p)
        for field in('row_sequence','sequence','call_id','parent_call_id','excluded_calls_before'):
            with self.subTest(field=field):
                ps=copy.deepcopy(self.ps);e=ps[-1]['events'][0];e[field]=(e[field]or 0)+1
                t=self.new_policy.TraceValidator(ps[0]['identity'])
                with self.assertRaises(self.new_policy.TraceRejected):
                    for p in ps:t.consume(p)

    def test_old_life_thread_raw_and_sticky_guards_still_reject(self):
        for mutation in('life','thread','raw','drop','fault','restored'):
            with self.subTest(mutation=mutation):
                ps=copy.deepcopy(self.ps);last=ps[-1]
                if mutation=='life':next(e for e in last['events']if e['player'])['player']['generation']+=1
                elif mutation=='thread':last['events'][0]['thread_id']+=1
                elif mutation=='raw':next(e for e in last['events']if e['kind']=='apply_action')['data']['raw_args_hex']='00'
                elif mutation=='restored':last['restored'][next(iter(last['restored']))]=False
                else:last['counters']['dropped'if mutation=='drop'else'faults']+=1
                t=self.new_policy.TraceValidator(ps[0]['identity'])
                with self.assertRaises(self.new_policy.TraceRejected):
                    for p in ps:t.consume(p)
                    ident=ps[0]['identity'];t.finish({'schema':'a1.first-state.external-restore.v1','before_identity':ident,
                        'after_identity':ident,'script_unloaded':True,'session_detached':True,'prior_errors':[],
                        'regions':self.new_policy.expected_restore_regions(ident)})

    def test_actual_unknown_weapon_owner_is_retained_but_incomplete(self):
        p=json.loads(fixture.ActualRegisteredScope().run_js("""
const t=x.startTick();x.call('fire_colt',0x520000,[0x910000]);x.leave(t);
console.log(JSON.stringify(done(x)));
"""))
        self.assertTrue(any(e['kind']=='fire_colt'for e in p['events']))
        self.assertEqual(p['scope_counters']['entered_excluded'],0)
        with self.assertRaisesRegex(self.new_policy.TraceRejected,'INCOMPLETE'):
            self.new_policy.TraceValidator(p['identity']).consume(p)

    def test_actual_registered_receive_without_known_owner_or_chain_is_incomplete(self):
        p=json.loads(fixture.ActualRegisteredScope().run_js("""
const t=x.startTick();x.call('receive_damage',0x300000,[0x320000,1,['f',20],0x710000,0x71000c],x.bases['Engine.dll']+x.G.call_returns.direct_to_receive);
x.leave(t);console.log(JSON.stringify(done(x)));
"""))
        events=[e for e in p['events']if e['kind']=='receive_damage']
        self.assertEqual(len(events),2);self.assertEqual(events[0]['data']['scope'],'registered')
        self.assertIsNone(events[0]['data']['payload']['inflictor'])
        self.assertFalse(events[0]['data']['payload']['chain_bound'])
        with self.assertRaisesRegex(self.new_policy.TraceRejected,'INCOMPLETE'):
            self.new_policy.TraceValidator(p['identity']).consume(p)

    def test_every_explicit_false_chain_and_respawn_source_is_incomplete(self):
        for kind in('fire_one_bullet','prepare_bullet','launch_bullet','cast_ray','inflict_direct_damage','receive_damage'):
            with self.subTest(kind=kind):
                ps=copy.deepcopy(self.ps)
                row=next(e for p in ps for e in p['events']if e['kind']==kind)
                self.assertIs(row['data']['payload']['chain_bound'],True)
                row['data']['payload']['chain_bound']=False
                t=self.new_policy.TraceValidator(ps[0]['identity'])
                with self.assertRaisesRegex(self.new_policy.TraceRejected,'INCOMPLETE'):
                    for p in ps:t.consume(p)
        ps=respawn_packet()
        for kind in('end_make_copy','death_handler','initialize_player'):
            with self.subTest(kind=kind):
                mutated=copy.deepcopy(ps)
                row=next(e for p in mutated for e in p['events']if e['kind']==kind and(kind!='initialize_player'or e['data']['payload']['respawn_source']is not None))
                q=row['data']['payload']
                if kind=='initialize_player':q=q['respawn_source']
                self.assertIs(q['chain_bound'],True);q['chain_bound']=False
                t=self.new_policy.TraceValidator(mutated[0]['identity'])
                with self.assertRaisesRegex(self.new_policy.TraceRejected,'INCOMPLETE'):
                    for p in mutated:t.consume(p)

    def test_actual_bound_respawn_chain_and_optional_null_fields_still_validate(self):
        ps=respawn_packet();t=self.new_policy.TraceValidator(ps[0]['identity'])
        for p in ps:t.consume(p)
        initial=next(e for e in ps[0]['events']if e['kind']=='initialize_player')
        self.assertIsNone(initial['data']['payload']['respawn_source'])
        self.assertTrue(any(e['kind']=='process_game_tick'and'chain_bound'not in e['data']['payload']for e in ps[0]['events']))

    def test_whole_policy_schema_inverse_and_old_life_restore_bytes_unchanged(self):
        from tools import first_state_registered_damage_policy as m
        old=read(PARENT/'vendor/observer/observer_policy.py').decode();new=m.patch_policy(old)
        self.assertEqual(m.reverse_policy(new),old)
        for a,b in [('def expected_restore_regions(','class TraceValidator:'),
                    ("  if e['tick']!=",' def finish('),(' def finish(',None)]:
            stop_old=len(old)if b is None else old.index(b);stop_new=len(new)if b is None else new.index(b)
            self.assertEqual(new[new.index(a):stop_new],old[old.index(a):stop_old])
        schema=read(PARENT/'vendor/observer/event-schema.json').decode();changed=m.patch_schema(schema)
        self.assertEqual(m.reverse_schema(changed,schema),schema)
        for a,b in [("'victim lifetime changed'","'mutated'"),("'player life generation mismatch'","'mutated'")]:
            if a in new:
                with self.assertRaises(ValueError):m.reverse_policy(new.replace(a,b,1))
        with self.assertRaises(ValueError):m.reverse_schema(changed.replace(m.WIRE,m.WIRE+'-foreign'),schema)

    def test_actual_unchanged_batch_session_archives_raw_rejects_SF_and_failed_tails(self):
        from tools import first_state_autodrain_session as session
        from tools import test_first_state_autodrain_session as fixture_session
        self.assertEqual(read(Path(session.__file__)),read(PARENT/'first_state_autodrain_session.py'))
        values=json.loads(fixture.ActualRegisteredScope().run_js("""
const t=x.startTick();x.call('cast_ray',0x100000,[0x700000]);
x.call('apply_action',0x310000,[0x720000,['f',1]]);x.init();x.shot();x.leave(t);
const p=x.api.drain();console.log(JSON.stringify([p,done(x)]));
"""))
        for variant in('valid','raw','hash','S','F','drop'):
            with self.subTest(variant=variant):
                v=copy.deepcopy(values)
                if variant=='raw':v[1]=b'{malformed'
                if variant=='drop':v[1]['counters']['dropped']+=1
                batch=fixture_session.batch(v,stop=1,final=2)
                if variant=='hash':batch['captures'][1]['sha256']='0'*64
                if variant=='S':batch['stop_serial']=3
                if variant=='F':batch['final_serial']=1
                ports=fixture_session.Ports([batch],fixture_session.batch([],stop=1,final=2))
                core=fixture_session.Core(ports);core.identity=values[0]['identity'];core.trace=self.new_policy.TraceValidator(core.identity)
                def regions():
                    ports.ops.append('regions');return self.new_policy.expected_restore_regions(core.identity)
                ports.read_regions=regions
                observer=session.BatchObserverSession(core,validate_packet=self.new_policy.validate_packet)
                result=observer.finish()
                self.assertEqual([r['serial']for r in result['packet_receipts']],[1,2])
                self.assertIn('unload',ports.ops);self.assertIn('detach',ports.ops);self.assertIn('regions',ports.ops)
                if variant=='valid':
                    self.assertEqual(result['status'],'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY',result['errors'])
                    self.assertEqual(result['cutoff_sequence'],len(values[0]['events']))
                    self.assertEqual(result['validated_packets'],2);self.assertTrue(result['main_tick_pair_before_cutoff'])
                else:self.assertEqual(result['status'],'FAIL')

if __name__=='__main__':unittest.main()
