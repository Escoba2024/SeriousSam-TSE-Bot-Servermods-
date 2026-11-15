"""Actual archive/reconstruction only within temporary fixtures, no real trees."""
import hashlib
import importlib.util
import io
import inspect
import json
import os
from pathlib import Path
import stat
import struct
import tarfile
import tempfile
import unittest
from unittest.mock import patch

TOOL=Path(__file__).with_name('restore_copy_roundtrip.py')
class RestoreCopy(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TOOL.is_file(),'new pack/fresh-restore API absent')
        spec=importlib.util.spec_from_file_location('restore_copy',TOOL);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
    def tree(self,base):
        root=base/'source';root.mkdir();(root/'sub').mkdir();(root/'empty').mkdir()
        (root/'sub/file').write_bytes(b'own fixture\0\xff'*50);(root/'zero').touch()
        os.setxattr(root,'user.own-test',b'directory\0');os.setxattr(root/'sub/file','user.own-test',b'\x00\xffvalue')
        for i,p in enumerate([root/'sub/file',root/'zero',root/'sub',root/'empty',root]):
            os.chmod(p,0o640 if p.is_file()else 0o750);os.utime(p,ns=(1500000000123456789+i,1600000000987654321+i))
        return root
    def test_full_file_directory_metadata_bytes_xattrs_noatime_roundtrip(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);before=self.m.inventory(s);r=self.m.pack(s,b/'fresh.tar.gz')
            self.assertEqual(self.m.inventory(s),before);self.assertEqual((b/'fresh.tar.gz').stat().st_mode&0o777,0o600)
            self.assertEqual(r['manifest'],before);self.assertTrue(r['verified'])
            got=self.m.restore(b/'fresh.tar.gz',b/'restored',r['archive_sha256'])
            self.assertTrue(got['verified']);self.assertEqual(self.m.inventory(b/'restored'),before)
            self.assertNotEqual(before['records'][0]['atime_ns'],before['records'][0]['mtime_ns'])
    def test_links_special_git_and_sparse_are_rejected(self):
        for kind in('symlink','hardlink','fifo','git','sparse'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
                b=Path(d);s=self.tree(b)
                if kind=='symlink':(s/'link').symlink_to(s/'sub/file')
                elif kind=='hardlink':os.link(s/'sub/file',s/'hard')
                elif kind=='fifo':os.mkfifo(s/'fifo')
                elif kind=='git':(s/'.git').mkdir()
                else:
                    with (s/'sparse').open('wb')as f:f.seek(1024*1024);f.write(b'x')
                with self.assertRaises((ValueError,OSError)):self.m.inventory(s)
                self.assertFalse((b/'archive').exists())
    def test_existing_output_or_inside_source_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);archive=b/'archive';archive.write_bytes(b'sentinel')
            with self.assertRaises((ValueError,FileExistsError)):self.m.pack(s,archive)
            self.assertEqual(archive.read_bytes(),b'sentinel')
            with self.assertRaises(ValueError):self.m.pack(s,s/'archive')
            r=self.m.pack(s,b/'fresh.tar.gz');target=b/'existing';target.mkdir();(target/'sentinel').write_text('same')
            with self.assertRaises((ValueError,FileExistsError)):self.m.restore(b/'fresh.tar.gz',target,r['archive_sha256'])
            self.assertEqual((target/'sentinel').read_text(),'same')
    def test_corrupt_hash_or_archive_path_cannot_escape_or_pass(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);r=self.m.pack(s,b/'fresh.tar.gz')
            with self.assertRaises(ValueError):self.m.restore(b/'fresh.tar.gz',b/'bad','0'*64)
            self.assertFalse((b/'bad').exists())
            manifest=r['manifest'];manifest['records'][1]['path']='../escape'
            data=json.dumps(manifest).encode();bad=b/'evil.tar.gz'
            with tarfile.open(bad,'w:gz')as tf:
                h=tarfile.TarInfo('manifest.json');h.size=len(data);tf.addfile(h,io.BytesIO(data))
            digest=hashlib.sha256(bad.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):self.m.restore(bad,b/'evil-target',digest)
            self.assertFalse((b/'escape').exists());self.assertFalse((b/'evil-target').exists())
    def test_xattr_errors_and_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b)
            with patch.object(self.m.os,'listxattr',side_effect=PermissionError('xattrs denied')):
                with self.assertRaises(PermissionError):self.m.inventory(s)
            r=self.m.pack(s,b/'fresh.tar.gz')
            with patch.object(self.m.os,'setxattr',side_effect=OSError('xattr unsupported')):
                with self.assertRaises(OSError):self.m.restore(b/'fresh.tar.gz',b/'restore',r['archive_sha256'])
            self.assertTrue(s.exists());self.assertTrue((b/'fresh.tar.gz').exists())
    def test_no_sparse_support_cannot_pass(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);real=self.m.os.lseek
            def fail(fd,offset,whence):
                if whence==os.SEEK_HOLE:raise OSError('unsupported hole detection')
                return real(fd,offset,whence)
            with patch.object(self.m.os,'lseek',side_effect=fail):
                with self.assertRaises(OSError):self.m.pack(s,b/'no-support.tar.gz')
            # Existing nonregular sources are never opened with blocking FIFO IO.
            self.assertFalse((b/'no-support.tar.gz').exists())
    def test_actual_compressed_writes_require_caller_reserve_admission(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);before=self.m.inventory(s);calls=[]
            def reserve(n):
                calls.append(n)
                return sum(calls)<=32
            # On the original unbounded implementation call its real old API:
            # RED must be successful unadmitted writing, not an unexpected kwarg.
            kw={'reserve':reserve}if'reserve'in inspect.signature(self.m.pack).parameters else{}
            with self.assertRaisesRegex(ValueError,'reserve'):
                self.m.pack(s,b/'partial',**kw)
            self.assertTrue(calls);self.assertTrue((b/'partial').exists())
            self.assertLessEqual((b/'partial').stat().st_size,32)
            self.assertEqual(self.m.inventory(s),before)
    def test_admitted_chunks_cover_exact_output_including_gzip_footer(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);calls=[]
            def reserve(n):calls.append(n);return True
            kw={'reserve':reserve}if'reserve'in inspect.signature(self.m.pack).parameters else{}
            r=self.m.pack(s,b/'archive',**kw)
            self.assertTrue(r['verified']);self.assertTrue(calls)
            self.assertEqual(sum(calls),(b/'archive').stat().st_size)
            self.assertGreater(len(calls),3)
    def test_actual_posix_acl_capability_and_other_owner_roundtrip(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);f=s/'sub/file';os.chown(f,65534,65534)
            def acl(entries):return struct.pack('<I',2)+b''.join(struct.pack('<HHI',*e)for e in entries)
            os.setxattr(f,'system.posix_acl_access',acl([(1,6,0xffffffff),(2,4,0),(4,4,0xffffffff),(16,4,0xffffffff),(32,0,0xffffffff)]))
            os.setxattr(s,'system.posix_acl_default',acl([(1,7,0xffffffff),(2,4,65534),(4,5,0xffffffff),(16,5,0xffffffff),(32,0,0xffffffff)]))
            os.setxattr(f,'security.capability',struct.pack('<5I',0x02000001,1<<10,0,0,0))
            before=self.m.inventory(s);r=self.m.pack(s,b/'archive')
            self.m.restore(b/'archive',b/'target',r['archive_sha256'])
            self.assertEqual(self.m.inventory(b/'target'),before);self.assertEqual(self.m.inventory(s),before)
            got=next(r for r in before['records']if r['path']=='sub/file')
            self.assertEqual((got['uid'],got['gid']),(65534,65534))
            self.assertIn('security.capability',got['xattrs']);self.assertIn('system.posix_acl_access',got['xattrs'])
    def test_changed_source_during_pack_and_reserve_exception_fail_without_deletion(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=self.tree(b);calls=[]
            def mutate(n):
                calls.append(n)
                if len(calls)==1:(s/'sub/file').write_bytes(b'changed own fixture')
                return True
            with self.assertRaisesRegex(ValueError,'source'):
                self.m.pack(s,b/'partial',reserve=mutate)
            self.assertTrue((s/'sub/file').exists());self.assertTrue((b/'partial').exists())
            def fail(n):raise OSError('caller disk read failed')
            with self.assertRaises((OSError,ValueError)):
                self.m.pack(s,b/'reserve-partial',reserve=fail)
            self.assertEqual((b/'reserve-partial').stat().st_size,0)
    def test_payload_corruption_and_hardlink_member_fail_before_target_creation(self):
        for kind in('bytes','hardlink'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
                b=Path(d);s=self.tree(b);m=self.m.inventory(s);bad=b/'bad';data=json.dumps(m).encode()
                with tarfile.open(bad,'w:gz')as tf:
                    h=tarfile.TarInfo('manifest.json');h.size=len(data);tf.addfile(h,io.BytesIO(data))
                    for r in m['records']:
                        if r['kind']!='file':continue
                        h=tarfile.TarInfo('files/'+r['path']);h.size=r['size']
                        if kind=='hardlink':h.type=tarfile.LNKTYPE;h.linkname='elsewhere';h.size=0;tf.addfile(h)
                        else:tf.addfile(h,io.BytesIO(b'X'*r['size']))
                with self.assertRaises(ValueError):
                    self.m.restore(bad,b/'target',hashlib.sha256(bad.read_bytes()).hexdigest())
                self.assertFalse((b/'target').exists())
    def test_even_empty_gnu_sparse_tar_member_is_rejected(self):
        with tempfile.TemporaryDirectory()as d:
            b=Path(d);s=b/'source';s.mkdir();(s/'empty').touch();m=self.m.inventory(s)
            data=json.dumps(m).encode();bad=b/'sparse.tar.gz'
            with tarfile.open(bad,'w:gz',format=tarfile.GNU_FORMAT)as tf:
                h=tarfile.TarInfo('manifest.json');h.size=len(data);tf.addfile(h,io.BytesIO(data))
                h=tarfile.TarInfo('files/empty');h.type=tarfile.GNUTYPE_SPARSE;tf.addfile(h)
            with self.assertRaises(ValueError):
                self.m.restore(bad,b/'target',hashlib.sha256(bad.read_bytes()).hexdigest())
            self.assertFalse((b/'target').exists())

if __name__=='__main__':unittest.main()
