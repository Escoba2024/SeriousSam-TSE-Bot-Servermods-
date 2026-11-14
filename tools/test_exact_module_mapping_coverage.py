"""Pure byte-domain mapping regression; no process access or native calls."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch


RECEIPT=Path('/srv/tse-milestone-a-evidence-20261111/a1-mapping-failure-20261114-133108/module-mapping-failure.json')


class ExactCoverageTests(unittest.TestCase):
 def setUp(self):
  try:
   from mapped_rows import canonical_mapped_rows
  except ImportError:
   self.fail('missing exact module coverage implementation')
  self.canonical=canonical_mapped_rows
  self.equal=lambda before,after:self.canonical(before)==self.canonical(after)
  self.whole=['1000-5000 r-xp 00000000 08:01 123 /fixture.dll']
  self.split=['1000-2000 r-xp 00000000 08:01 123 /fixture.dll',
              '2000-3000 r-xp 00001000 08:01 123 /fixture.dll',
              '3000-5000 r-xp 00002000 08:01 123 /fixture.dll']

 def test_actual_archived_twenty_twenty_two_rows_have_identical_coverage(self):
  receipt=json.loads(RECEIPT.read_text())
  self.assertEqual(len(receipt['expected_mapped_rows']),20)
  self.assertEqual(len(receipt['actual_mapped_rows']),22)
  self.assertNotEqual(receipt['expected_mapped_rows'],receipt['actual_mapped_rows'])
  self.assertTrue(self.equal(receipt['expected_mapped_rows'],receipt['actual_mapped_rows']))
  self.assertEqual(self.canonical(receipt['expected_mapped_rows']),self.canonical(receipt['actual_mapped_rows']))

 def test_identical_and_alternative_legal_partitions_match_without_reads(self):
  with patch('builtins.open',side_effect=AssertionError('mapping helper must not read')):
   self.assertTrue(self.equal(self.whole,self.whole))
   self.assertTrue(self.equal(self.whole,self.split))
   self.assertTrue(self.equal(self.split,self.whole))
   self.assertTrue(self.equal(self.whole,['1000-4000 r-xp 0 08:01 123 /fixture.dll','4000-5000 r-xp 3000 08:01 123 /fixture.dll']))

 def test_each_permission_and_file_identity_component_is_exact(self):
  for old,new in [('r-xp','rwxp'),('r-xp','r--p'),('r-xp','--xp'),('r-xp','r-xs'),
                  ('08:01','09:01'),('08:01','08:02'),('123','124'),('/fixture.dll','/other.dll')]:
   changed=list(self.split);changed[1]=changed[1].replace(old,new)
   with self.subTest(change=(old,new)):
    self.assertFalse(self.equal(self.whole,changed))

 def test_address_domain_and_affine_file_offset_cannot_change(self):
  cases=[self.split[:1]+self.split[2:],
         self.split+['5000-6000 r-xp 00004000 08:01 123 /fixture.dll'],
         ['0000-5000 r-xp 00000000 08:01 123 /fixture.dll'],
         [self.split[0],self.split[1].replace('00001000','00002000'),self.split[2]],
         ['1000-5000 r-xp 00001000 08:01 123 /fixture.dll']]
  for rows in cases:
   with self.subTest(rows=rows):self.assertFalse(self.equal(self.whole,rows))

 def test_existing_gaps_and_permission_or_offset_boundaries_remain_exact(self):
  expected=['1000-2000 r-xp 0 08:01 123 /fixture.dll','3000-5000 rwxp 9000 08:01 123 /fixture.dll']
  split=[expected[0],'3000-4000 rwxp 9000 08:01 123 /fixture.dll','4000-5000 rwxp a000 08:01 123 /fixture.dll']
  self.assertTrue(self.equal(expected,split));self.assertEqual(len(self.canonical(split)),2)
  self.assertFalse(self.equal(expected,['1000-5000 r-xp 0 08:01 123 /fixture.dll']))
  self.assertFalse(self.equal(expected,[expected[0],split[1].replace('3000-4000','2000-4000'),split[2]]))

 def test_duplicate_overlap_and_reordered_rows_are_not_sorted_or_discarded(self):
  for rows in (self.split+[self.split[-1]],list(reversed(self.split)),
               [self.split[0],self.split[1].replace('2000-3000','1800-3000'),self.split[2]]):
   with self.subTest(rows=rows):
    with self.assertRaises(ValueError):self.canonical(rows)

 def test_invalid_rows_never_match_even_when_both_inputs_equal(self):
  for row in ('','1000-1000 r-xp 0 08:01 123 /fixture.dll',
              '5000-1000 r-xp 0 08:01 123 /fixture.dll',
              '-1000-5000 r-xp 0 08:01 123 /fixture.dll',
              '1000-5000 rwxy 0 08:01 123 /fixture.dll',
              '1000-5000 r-xp -1 08:01 123 /fixture.dll',
              '1000-5000 r-xp 0 08:GG 123 /fixture.dll',
              '1000-5000 r-xp 0 08:01 -1 /fixture.dll',
              '1000-5000 r-xp 0 08:01 123',
              'garbage'):
   with self.subTest(row=row):
    with self.assertRaises(ValueError):self.canonical([row])
    with self.assertRaises(ValueError):self.equal([row],[row])
  with self.assertRaises(ValueError):self.equal([],[])

 def test_path_spaces_are_preserved_and_deleted_suffix_is_not_dropped(self):
  first=[self.whole[0].replace('/fixture.dll','/fixture directory/with spaces.dll')]
  second=[r.replace('/fixture.dll','/fixture directory/with spaces.dll')for r in self.split]
  self.assertTrue(self.equal(first,second))
  self.assertFalse(self.equal(first,[second[0]+' (deleted)']+second[1:]))


if __name__=='__main__':unittest.main()
