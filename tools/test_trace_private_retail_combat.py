from pathlib import Path
import unittest
import trace_private_retail_combat as t


class ProbeSafety(unittest.TestCase):
    def test_export_index_is_not_public_ordinal(self):
        text='''ImageBase 600c0000
 [ 2] +base[ 3] 7120 Export RVA
 [ 3] +base[ 4] 8100 Export RVA
 [ 2] ?Function@@Z
 [ 3] ?Other@@Z
'''
        self.assertEqual(t.export_rvas(text,['?Function@@Z']),{'?Function@@Z':0x7120})
        with self.assertRaises(ValueError):t.export_rvas(text,['missing'])

    def test_public_or_stale_runtime_is_rejected_before_attach(self):
        good=dict(status='MEASURING',scope='ISOLATED_NETNS_RETAIL_WINE',
                  cgroup='/sys/fs/cgroup/tse-sessions-123',network_namespace='net:[123]')
        t.validate_runtime(Path('/srv/tse-session-qualification-ai2-test'),good)
        for path,report in [('/srv/tse-redstation-public-20261025',good),
                            ('/tmp/tse-session-qualification-ai2-test',good),
                            ('/srv/tse-session-qualification-ai2-test',dict(good,status='PASS_LIMITED')),
                            ('/srv/tse-session-qualification-ai2-test',dict(good,cgroup='/sys/fs/cgroup'))]:
            with self.subTest(path=path,report=report),self.assertRaises(ValueError):
                t.validate_runtime(Path(path),report)


if __name__=='__main__':unittest.main()
