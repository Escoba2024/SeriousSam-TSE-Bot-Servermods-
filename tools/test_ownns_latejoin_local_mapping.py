"""Synthetic exact Retail107 local-source mapping; no process reads."""
import importlib.util
import struct
import hashlib
from pathlib import Path
import unittest


class LocalSource(unittest.TestCase):
 def test_missing_passive_mapper_is_red(self):
  self.assertIsNotNone(importlib.util.find_spec('ownns_latejoin_local_mapping'))
 def memory(self):
  import ownns_latejoin_local_mapping as p
  memory={};base=0x60840000;game=0x30000;source=0x50000
  def put(at,raw):memory.update({at+i:b for i,b in enumerate(raw)})
  for rva,raw in p.GUARDS:put(base+rva,bytes.fromhex(raw))
  put(base+0x2fba4,struct.pack('<I',game))
  for slot in range(4):put(game+0xfa4+slot*0x80c,struct.pack('<I',source if slot==0 else 0))
  put(source,struct.pack('<i',8))
  return p,memory,base,game,source,put
 def test_original_local0_global8_uses_actual_source_not_query_complement(self):
  p,m,b,g,s,put=self.memory();out=p.snapshot(lambda a,n:bytes(m[a+i]for i in range(n)),b)
  self.assertEqual(out['locals'],[dict(local=0,source_pointer=s,global_slot=8)])
  self.assertEqual(out['consistency'],'two_equal_reads_not_atomic')
  self.assertFalse(out['native_abi_qualified'])
 def test_wrong_local_global_slot_guard_or_changed_pointer_fails(self):
  for case in ('wrong_global','extra_local','guard','second_read'):
   p,m,b,g,s,put=self.memory()
   if case=='wrong_global':put(s,struct.pack('<i',7))
   elif case=='extra_local':put(g+0xfa4+0x80c,struct.pack('<I',s))
   elif case=='guard':put(b+p.GUARDS[0][0],b'\x90')
   seen=0
   def read(a,n):
    nonlocal seen
    if a==g+0xfa4:
     seen+=1
     if case=='second_read'and seen==2:return struct.pack('<I',s+4)
    return bytes(m[a+i]for i in range(n))
   with self.subTest(case=case),self.assertRaises(ValueError):p.snapshot(read,b)
 def test_failed_global_slot_keeps_actual_source_dword_evidence(self):
  p,m,b,g,s,put=self.memory();put(s,struct.pack('<i',7))
  with self.assertRaises(ValueError)as error:p.snapshot(lambda a,n:bytes(m[a+i]for i in range(n)),b)
  self.assertTrue(any(row['address']==s and row['raw_hex']=='07000000'for row in getattr(error.exception,'raw_reads',[])))
 def test_guards_match_actual_hash_pinned_original_pe_section_bytes(self):
  import ownns_latejoin_local_mapping as p
  raw=Path('/srv/tse-arena-isolated-20261111/vanilla/Bin/GameMP.dll').read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208')
  pe=struct.unpack_from('<I',raw,0x3c)[0];self.assertEqual(raw[pe:pe+4],b'PE\0\0')
  count=struct.unpack_from('<H',raw,pe+6)[0];optional=struct.unpack_from('<H',raw,pe+20)[0];sections=pe+24+optional
  self.assertEqual(struct.unpack_from('<H',raw,pe+24)[0],0x10b)
  for rva,hexbytes in p.GUARDS:
   matches=[]
   for n in range(count):
    vsize,va,size,offset=struct.unpack_from('<IIII',raw,sections+n*40+8)
    if va<=rva and rva+len(bytes.fromhex(hexbytes))<=va+size:matches.append(raw[offset+rva-va:offset+rva-va+len(bytes.fromhex(hexbytes))])
   self.assertEqual(matches,[bytes.fromhex(hexbytes)],hex(rva))


if __name__=='__main__':unittest.main()
