"""Adapter models: no game, Xlib, Frida or displays."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from test_a1_xres_attribution_evidence import fixture


class Adapter(unittest.TestCase):
 def module(self):return importlib.import_module('a1_xres_attribution')
 def test_disabled_start_precedes_qualification_path_or_spawn(self):
  with self.assertRaisesRegex(RuntimeError,'disabled'):self.module().PassiveRecorder.start(None,None,None,None)
 def test_parent_uses_same_proxy_arm_and_sticky_release_safe_bodies(self):
  m=self.module();import a1_passive_xrecord as old
  for name in('arm','before_input','reserve_attempt','record_emission'):
   self.assertIs(getattr(m.PassiveRecorder,name),getattr(old.PassiveRecorder,name))
  self.assertIs(m.instrument_transport,old.instrument_transport)
 def test_lifecycle_qualification_must_be_real_and_source_fingerprint_exact(self):
  m=self.module();q=dict(status='PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY',no_inputs=True,normal_closes=True,lifecycle_started=True,lifecycle_died=True,exactly_two_snapshots=True,driver_requests_bound=True,fingerprints=m.fingerprints())
  for change in('missing','wrong_status','missing_died','changed_source','wrong_closes','zero_driver_requests'):
   value=dict(q)
   if change=='missing':value=None
   elif change=='wrong_status':value['status']='PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY'
   elif change=='missing_died':value['lifecycle_died']=False
   elif change=='changed_source':value['fingerprints']={}
   elif change=='wrong_closes':value['normal_closes']=False
   else:value['driver_requests_bound']=False
   with patch.object(m.legacy,'require_method_qualification',return_value={}):
    with self.assertRaises((ValueError,RuntimeError)):m.require_method_qualification({'xres_lifecycle_qualification':value})
  with patch.object(m.legacy,'require_method_qualification',return_value={}):self.assertEqual(m.require_method_qualification({'xres_lifecycle_qualification':q}),q)
 def test_exclusive_metadata_sidecar_hash_prevents_foreign_or_partial_evidence(self):
  m=self.module();rows,s,e,n=fixture()
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);raw=b''.join((json.dumps(row)+'\n').encode()for row in rows);(root/'record-raw.jsonl').write_bytes(raw)
   side=json.dumps(dict(expected=e,snapshots=s,attempts=[{},{}],errors=[])).encode();(root/'xres-attribution.json').write_bytes(side);n['xres_evidence']=dict(path='xres-attribution.json',sha256=hashlib.sha256(side).hexdigest(),bytes=len(side))
   r=m.audit_attribution(root,n);self.assertEqual(r['own_original_request_rows'],2)
   (root/'xres-attribution.json').write_bytes(side+b' ')
   with self.assertRaises(ValueError):m.audit_attribution(root,n)
 def test_failed_extended_evidence_does_not_repeat_or_skip_inherited_close(self):
  m=self.module();obj=m.PassiveRecorder.__new__(m.PassiveRecorder);obj.closed=False;obj.directory=Path('/unused');calls=[]
  def close(self,phases):calls.append('legacy');self.closed=True;self.final={'status':'PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY','native':{},'errors':[]};return self.final
  with patch.object(m.legacy.PassiveRecorder,'close',close),patch.object(m,'audit_attribution',side_effect=ValueError('missing lifecycle')):r=obj.close([])
  self.assertEqual(calls,['legacy']);self.assertEqual(r['status'],'FAIL_PASSIVE_XRECORD_DIAGNOSTIC');self.assertTrue(r['errors']);self.assertIs(r,obj.close([]));self.assertEqual(calls,['legacy'])


if __name__=='__main__':unittest.main()
