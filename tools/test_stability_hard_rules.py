import math
import struct
import unittest

import stability_hard_rules as rules


class HardRulesTests(unittest.TestCase):
    def sample(self, changes=None):
        data = bytearray(156)
        for key, (fmt, offset) in rules.FIELDS.items():
            struct.pack_into(fmt, data, offset, (changes or {}).get(key, rules.EXPECTED[key]))
        return {'session156_hex': data.hex()}

    def test_exact_hard_native_rules(self):
        self.assertEqual(rules.validate_session(self.sample()), rules.EXPECTED)

    def test_each_rule_must_match_without_tolerance(self):
        for key, value in rules.EXPECTED.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                rules.validate_session(self.sample({key: value + 1}))
        with self.assertRaises(ValueError):
            rules.validate_session(self.sample({'spawn': 1e-12}))

    def test_missing_short_extra_or_malformed_bytes_reject(self):
        for row in ({}, {'session156_hex': '00'},
                    {'session156_hex': '00' * 157},
                    {'session156_hex': 'zz' * 156}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                rules.validate_session(row)

    def test_nonfinite_spawn_rejects(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                rules.validate_session(self.sample({'spawn': value}))

    def test_native_serious_is_not_hard(self):
        with self.assertRaises(ValueError):
            rules.validate_session(self.sample({'difficulty': 3}))

    def test_query_requires_exact_hard(self):
        self.assertIsNone(rules.validate_query({'difficulty': 'Hard'}))
        for value in ('Serious', '2', '', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                rules.validate_query({'difficulty': value})


if __name__ == '__main__':
    unittest.main()
