"""Actual proc/FD/table fixture races, no live process/network operations."""
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_owned_sync_capture import udp


@contextmanager
def actual_fixture():
 import owned_sync_capture as c
 with tempfile.TemporaryDirectory()as directory:
  root=Path(directory);proc=root/'proc';arena=root/'arena';arena.mkdir()
  (proc/'1/ns').mkdir(parents=True);(proc/'1/ns/net').write_text('host')
  ns=root/'shared-netns';ns.write_text('owned')
  registry={};table='header\n'+''.join(udp(p,i)+'\n'for p,i in[(27850,200),(27851,250),(30001,201),(30002,202),(30003,203)])
  for i,role in enumerate(c.ROLES):
   pid=100+i;p=proc/str(pid);(p/'fd').mkdir(parents=True);(p/'ns').mkdir();(p/'net').mkdir();(arena/role).mkdir()
   (p/'cwd').symlink_to(arena/role);(p/'ns/net').hardlink_to(ns)
   (p/'comm').write_text('DedicatedServer'if role=='server'else'SeriousSam.exe')
   unit='own-'+role+'.service';(p/'cgroup').write_text('0::/system.slice/'+unit+'\n')
   (p/'net/udp').write_text(table);(p/'net/udp6').write_text('header\n')
   for index,inode in enumerate([200,250]if role=='server'else[200+i]):(p/'fd'/str(index)).symlink_to('socket:[%d]'%inode)
   registry[role]=dict(identity=[pid,1000+i],unit=unit)
  (proc/'102/fd/46').symlink_to('/a/closed/non-udp-file')
  def fake_path(value):
   value=str(value)
   return proc/value.removeprefix('/proc/').removeprefix('/proc')if value.startswith('/proc')else Path(value)
  with patch.object(c,'Path',side_effect=fake_path),patch.object(c,'ARENA',arena),patch.object(c,'read_start',side_effect=lambda pid:1000+pid-100):yield c,root,proc,registry


class FdChurnTests(unittest.TestCase):
 def disappearing(self,scan,udp_socket=False):
  with actual_fixture()as(c,root,proc,registry):
   before=c.observe_roles(registry);target=proc/'102/fd'/('0'if udp_socket else'46')
   actual_readlink=Path.readlink;actual_iterdir=Path.iterdir;calls=0;scans=0
   def race(path):
    nonlocal calls
    if path==target:
     calls+=1
     if calls==scan:path.unlink()
    return actual_readlink(path)
   def counted(path):
    nonlocal scans
    if path==proc/'102/fd':scans+=1
    return actual_iterdir(path)
   with patch.object(Path,'readlink',race),patch.object(Path,'iterdir',counted):
    if udp_socket:
     with self.assertRaises(ValueError):c.observe_roles(registry)
    else:self.assertEqual(c.observe_roles(registry),before)
   self.assertEqual(calls,scan);self.assertEqual(scans,2)
 def test_disappearing_nonudp_fd_first_scan_keeps_exact_binding(self):self.disappearing(1)
 def test_disappearing_nonudp_fd_second_scan_keeps_exact_binding(self):self.disappearing(2)
 def test_disappearing_udp_fd_first_scan_fails(self):self.disappearing(1,True)
 def test_disappearing_udp_fd_second_scan_fails(self):self.disappearing(2,True)
 def rejected_actual_change(self,change):
  import owned_capture_exec as helper
  with actual_fixture()as(c,root,proc,registry):
   binding=c.observe_roles(registry);config=root/'config.json'
   c.exclusive_json(config,dict(source_pins={},registry=registry,binding=binding,owner_path=str(root/'owned-sync-owner.json')))
   if change=='port':
    table=proc/'102/net/udp';table.write_text(table.read_text().replace('0100007F:7532','0100007F:7542'))
   elif change=='inode':
    fd=proc/'102/fd/0';fd.unlink();fd.symlink_to('socket:[999]')
    table=proc/'102/net/udp';table.write_text(table.read_text().replace(' 202 2 0 0',' 999 2 0 0'))
   elif change=='namespace':
    ns=proc/'102/ns/net';ns.unlink();ns.write_text('different')
   with patch.object(helper,'RUNTIME_REVIEWED',True),patch.object(helper,'observe_roles',side_effect=c.observe_roles),patch.object(helper.os,'execv')as execute:
    if change=='pid':
     with patch.object(c,'read_start',return_value=999),self.assertRaises(ValueError):helper.main(config)
    else:
     with self.assertRaises(ValueError):helper.main(config)
    execute.assert_not_called();self.assertFalse((root/'owned-sync-owner.json').exists())
 def test_actual_udp_port_change_rejected_before_exec(self):self.rejected_actual_change('port')
 def test_actual_udp_inode_replacement_rejected_before_exec(self):self.rejected_actual_change('inode')
 def test_actual_pid_change_rejected_before_exec(self):self.rejected_actual_change('pid')
 def test_actual_namespace_change_rejected_before_exec(self):self.rejected_actual_change('namespace')
 def test_non_enoent_readlink_errors_remain_hard_failures(self):
  for error in(PermissionError('denied'),OSError('other IO error')):
   with self.subTest(error=type(error).__name__),actual_fixture()as(c,root,proc,registry):
    original=Path.readlink
    def fail(path):
     if path==proc/'102/fd/46':raise error
     return original(path)
    with patch.object(Path,'readlink',fail),self.assertRaises(type(error)):c.observe_roles(registry)


if __name__=='__main__':unittest.main()
