import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import qualify_bot_sessions as q


class NativeArtifact(unittest.TestCase):
    def test_resource_collection_waits_for_confirmed_join(self):
        record=q.process_record(os.getpid())
        unconfirmed=dict(record,start_ticks=record['start_ticks']+1)
        samples=q.sample_resources({'server':record,'bot':unconfirmed},{'bot':{'status':'JOINING'}})
        self.assertGreater(samples['server']['rss_mib'],0)
        self.assertIsNone(samples['bot'])
        with self.assertRaises(RuntimeError):
            q.sample_resources({'bot':unconfirmed},{'bot':{'status':'PLAYING'}})

    def test_resource_sample_is_bound_to_real_process_generation(self):
        record=q.process_record(os.getpid())
        sample=q.process_resources(record)
        self.assertGreater(sample['rss_mib'],0)
        self.assertGreater(sample['pss_mib'],0)
        self.assertGreaterEqual(sample['cpu_s'],0)
        self.assertEqual(sample['start_ticks'],record['start_ticks'])
        wrong=dict(record,start_ticks=record['start_ticks']+1)
        with self.assertRaises(RuntimeError):q.process_resources(wrong)

    def test_offline_guard_requires_unchanged_explicit_shutdown(self):
        with tempfile.TemporaryDirectory() as d:
            marker=Path(d)/'disabled.json'
            marker.write_text(json.dumps(dict(status='DISABLED_BY_USER',host='ubuntu-4gb-nbg1-2')))
            digest=hashlib.sha256(marker.read_bytes()).hexdigest()
            with patch.object(q,'host_public_runtime_state',return_value=([],set()),create=True):
                q.offline_public_guard(marker,digest)
                marker.write_text(json.dumps(dict(status='ENABLED',host='ubuntu-4gb-nbg1-2')))
                with self.assertRaises(RuntimeError):q.offline_public_guard(marker,digest)
                digest=hashlib.sha256(marker.read_bytes()).hexdigest()
                with self.assertRaises(RuntimeError):q.offline_public_guard(marker,digest)
                marker.unlink()
                with self.assertRaises(RuntimeError):q.offline_public_guard(marker,digest)

    def test_offline_guard_rejects_public_games_or_listeners(self):
        with tempfile.TemporaryDirectory() as d:
            marker=Path(d)/'disabled.json'
            marker.write_text(json.dumps(dict(status='DISABLED_BY_USER',host='ubuntu-4gb-nbg1-2')))
            digest=hashlib.sha256(marker.read_bytes()).hexdigest()
            for observations in [(['DedicatedServer'],set()),(['SeriousSam.exe'],set()),
                                 ([],{25600}),([],{25601})]:
                with patch.object(q,'host_public_runtime_state',return_value=observations,create=True):
                    with self.assertRaises(RuntimeError):q.offline_public_guard(marker,digest)

    def test_fault_probe_waits_for_complete_population(self):
        states={'p':dict(id='p',status='PLAYING'),'q':dict(id='q',status='JOINING')}
        self.assertIsNone(q.crash_probe_candidate(states,100,2))
        states['q']['status']='PLAYING'
        self.assertIsNone(q.crash_probe_candidate(states,89,2))
        self.assertEqual(q.crash_probe_candidate(states,90,2),'p')
    def test_cancel_probe_requires_actual_joining_transition(self):
        events=[dict(id='p',epoch=1,event='join_requested',reason='scheduled'),
                dict(id='p',epoch=1,event='leave_requested',reason='admin'),
                dict(id='p',epoch=1,event='left',reason='admin')]
        self.assertTrue(q.joining_cancel_evidence(events,0))
        self.assertFalse(q.joining_cancel_evidence(events,1))
        self.assertFalse(q.joining_cancel_evidence(events+[dict(id='p',epoch=1,event='joined')],0))
        self.assertFalse(q.joining_cancel_evidence(events[:-1],0))
    def test_pinned_artifact_and_hash_drift(self):
        with tempfile.TemporaryDirectory() as d:
            dll=Path(d)/'GameMP.dll';dll.write_bytes(b'private-test-fixture')
            manifest=Path(d)/'manifest.json'
            digest=hashlib.sha256(dll.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(dict(build_ok=True,qualified=False,candidate=str(dll),dll_sha256=digest)))
            self.assertEqual(q.select_artifact(manifest),(dll,digest))
            dll.write_bytes(b'drift')
            with self.assertRaises(ValueError):q.select_artifact(manifest)
            manifest.write_text(json.dumps(dict(build_ok=False,candidate=str(dll),dll_sha256=digest)))
            with self.assertRaises(ValueError):q.select_artifact(manifest)


if __name__=='__main__':unittest.main()
